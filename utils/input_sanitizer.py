"""
Input Sanitizer Utilities - Enterprise Security
==============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Expert Roles: Security Expert + Backend Senior + Lead Dev IA
Provides comprehensive input sanitization and security validation.
"""

import re
import html
import json
import logging
import hashlib
import base64
from typing import Any, Dict, List, Optional, Union, Set, Tuple
from datetime import datetime
from urllib.parse import quote, unquote, urlparse
import bleach
from markupsafe import Markup
import sqlparse


class SanitizationConfig:
    """Configuration for sanitization rules."""
    
    def __init__(self):
        # HTML sanitization settings
        self.allowed_html_tags = [
            'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'img', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        ]
        
        self.allowed_html_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height'],
            '*': ['class', 'id']
        }
        
        # Dangerous patterns to remove/escape
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'data:',
            r'on\w+\s*=',
            r'expression\s*\(',
            r'@import',
            r'\\x[0-9a-fA-F]{2}',
            r'\\u[0-9a-fA-F]{4}'
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r'(\s*(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+)',
            r'(\s*(or|and)\s+["\']?\d+["\']?\s*=\s*["\']?\d+["\']?)',
            r'(\s*;\s*(update|delete|insert|create|drop|alter)\s+)',
            r'(\/\*.*?\*\/)',
            r'(--.*$)',
            r'(\'\s*(or|and)\s+\'\w+\'\s*=\s*\'\w+)',
            r'(\"\s*(or|and)\s+\"\w+\"\s*=\s*\"\w+)',
        ]
        
        # File upload restrictions
        self.allowed_file_extensions = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
        }
        
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # Input length limits
        self.field_length_limits = {
            'username': 50,
            'email': 254,
            'password': 128,
            'name': 100,
            'description': 5000,
            'comment': 2000,
            'url': 2048,
            'phone': 20
        }


class SanitizationResult:
    """Result container for sanitization operations."""
    
    def __init__(self, original_value: Any, sanitized_value: Any, 
                 is_safe: bool, warnings: List[str] = None, 
                 threats_detected: List[str] = None):
        self.original_value = original_value
        self.sanitized_value = sanitized_value
        self.is_safe = is_safe
        self.warnings = warnings or []
        self.threats_detected = threats_detected or []
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'original_value': str(self.original_value)[:100] + "..." if len(str(self.original_value)) > 100 else str(self.original_value),
            'sanitized_value': self.sanitized_value,
            'is_safe': self.is_safe,
            'warnings': self.warnings,
            'threats_detected': self.threats_detected,
            'timestamp': self.timestamp.isoformat()
        }


class InputSanitizer:
    """
    Enterprise-grade input sanitization utility.
    
    Features:
    - XSS prevention and HTML sanitization
    - SQL injection prevention
    - File upload security validation
    - CSRF token validation
    - Input length and format validation
    - Encoding normalization
    - Threat detection and logging
    """
    
    def __init__(self, config: SanitizationConfig = None, strict_mode: bool = True):
        self.config = config or SanitizationConfig()
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)
        
        # Compile regex patterns for performance
        self.dangerous_regex = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                               for pattern in self.config.dangerous_patterns]
        
        self.sql_regex = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                         for pattern in self.config.sql_patterns]
    
    def sanitize_html(self, html_input: str, allow_tags: bool = True) -> SanitizationResult:
        """Sanitize HTML input to prevent XSS attacks."""
        if not isinstance(html_input, str):
            html_input = str(html_input)
        
        original_value = html_input
        warnings = []
        threats_detected = []
        
        # Check for dangerous patterns
        for i, pattern in enumerate(self.dangerous_regex):
            if pattern.search(html_input):
                threats_detected.append(f"Dangerous pattern detected: {self.config.dangerous_patterns[i]}")
        
        if allow_tags:
            # Use bleach for safe HTML sanitization
            sanitized = bleach.clean(
                html_input,
                tags=self.config.allowed_html_tags,
                attributes=self.config.allowed_html_attributes,
                strip=True
            )
        else:
            # Escape all HTML
            sanitized = html.escape(html_input)
        
        # Additional safety checks
        if '<script' in html_input.lower():
            threats_detected.append("Script tag detected")
        
        if 'javascript:' in html_input.lower():
            threats_detected.append("JavaScript protocol detected")
        
        # Check if content was modified
        if sanitized != original_value:
            warnings.append("Content was modified during sanitization")
        
        is_safe = len(threats_detected) == 0
        
        return SanitizationResult(
            original_value=original_value,
            sanitized_value=sanitized,
            is_safe=is_safe,
            warnings=warnings,
            threats_detected=threats_detected
        )
    
    def sanitize_sql_input(self, sql_input: str) -> SanitizationResult:
        """Sanitize input to prevent SQL injection attacks."""
        if not isinstance(sql_input, str):
            sql_input = str(sql_input)
        
        original_value = sql_input
        warnings = []
        threats_detected = []
        
        # Check for SQL injection patterns
        for i, pattern in enumerate(self.sql_regex):
            matches = pattern.findall(sql_input)
            if matches:
                threats_detected.append(f"SQL injection pattern detected: {self.config.sql_patterns[i]}")
        
        # Escape single quotes
        sanitized = sql_input.replace("'", "''")
        
        # Remove dangerous SQL keywords in non-query contexts
        if self.strict_mode:
            dangerous_keywords = ['UNION', 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'EXEC', 'EXECUTE']
            for keyword in dangerous_keywords:
                if keyword.upper() in sanitized.upper():
                    threats_detected.append(f"Dangerous SQL keyword detected: {keyword}")
                    sanitized = re.sub(re.escape(keyword), '', sanitized, flags=re.IGNORECASE)
        
        # Check for comment patterns
        if '--' in sanitized or '/*' in sanitized:
            threats_detected.append("SQL comment detected")
            sanitized = re.sub(r'--.*$', '', sanitized, flags=re.MULTILINE)
            sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        is_safe = len(threats_detected) == 0
        
        if sanitized != original_value:
            warnings.append("Input was modified during SQL sanitization")
        
        return SanitizationResult(
            original_value=original_value,
            sanitized_value=sanitized,
            is_safe=is_safe,
            warnings=warnings,
            threats_detected=threats_detected
        )
    
    def sanitize_file_upload(self, filename: str, file_content: bytes, 
                           file_type: str = None) -> SanitizationResult:
        """Sanitize and validate file uploads."""
        original_filename = filename
        warnings = []
        threats_detected = []
        
        # Sanitize filename
        sanitized_filename = re.sub(r'[^\w\.-]', '_', filename)
        
        # Check file extension
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        allowed_extensions = []
        for ext_list in self.config.allowed_file_extensions.values():
            allowed_extensions.extend(ext_list)
        
        if file_ext not in allowed_extensions:
            threats_detected.append(f"File extension not allowed: {file_ext}")
        
        # Check file size
        if len(file_content) > self.config.max_file_size:
            threats_detected.append(f"File size exceeds limit: {len(file_content)} bytes")
        
        # Check for executable content
        executable_signatures = [
            b'\x4d\x5a',  # PE executable
            b'\x7f\x45\x4c\x46',  # ELF executable
            b'\xcf\xfa\xed\xfe',  # Mach-O executable
            b'#!/',  # Script shebang
            b'<script',  # HTML script
            b'<?php'  # PHP script
        ]
        
        for sig in executable_signatures:
            if file_content.startswith(sig):
                threats_detected.append(f"Executable content detected")
                break
        
        # Check for embedded scripts in images
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
            suspicious_content = [b'<script', b'javascript:', b'<?php', b'<%']
            for content in suspicious_content:
                if content in file_content:
                    threats_detected.append("Embedded script detected in image")
                    break
        
        # Validate filename length
        if len(sanitized_filename) > 255:
            sanitized_filename = sanitized_filename[:255]
            warnings.append("Filename truncated to 255 characters")
        
        # Check for double extensions
        if filename.count('.') > 1:
            warnings.append("Multiple file extensions detected")
        
        is_safe = len(threats_detected) == 0
        
        return SanitizationResult(
            original_value=original_filename,
            sanitized_value=sanitized_filename,
            is_safe=is_safe,
            warnings=warnings,
            threats_detected=threats_detected
        )
    
    def sanitize_url(self, url: str) -> SanitizationResult:
        """Sanitize and validate URLs."""
        if not isinstance(url, str):
            url = str(url)
        
        original_value = url
        warnings = []
        threats_detected = []
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            threats_detected.append(f"URL parsing failed: {str(e)}")
            return SanitizationResult(original_value, url, False, warnings, threats_detected)
        
        # Check protocol
        if parsed.scheme not in ['http', 'https']:
            threats_detected.append(f"Dangerous URL scheme: {parsed.scheme}")
        
        # Check for dangerous protocols
        dangerous_schemes = ['javascript', 'vbscript', 'data', 'file', 'ftp']
        if parsed.scheme.lower() in dangerous_schemes:
            threats_detected.append(f"Dangerous URL scheme detected: {parsed.scheme}")
        
        # Check for IP addresses (potential internal network access)
        ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        if ip_pattern.match(parsed.hostname or ''):
            warnings.append("IP address detected in URL")
        
        # Check for suspicious domains
        suspicious_domains = ['localhost', '127.0.0.1', '0.0.0.0', '10.', '192.168.', '172.']
        for domain in suspicious_domains:
            if domain in (parsed.hostname or '').lower():
                threats_detected.append(f"Suspicious domain detected: {domain}")
        
        # URL encode the path and query
        sanitized_url = f"{parsed.scheme}://{parsed.netloc}"
        
        if parsed.path:
            sanitized_url += quote(parsed.path, safe='/')
        
        if parsed.query:
            sanitized_url += '?' + quote(parsed.query, safe='&=')
        
        if parsed.fragment:
            sanitized_url += '#' + quote(parsed.fragment)
        
        # Check URL length
        if len(sanitized_url) > self.config.field_length_limits.get('url', 2048):
            threats_detected.append("URL exceeds maximum length")
        
        is_safe = len(threats_detected) == 0
        
        return SanitizationResult(
            original_value=original_value,
            sanitized_value=sanitized_url,
            is_safe=is_safe,
            warnings=warnings,
            threats_detected=threats_detected
        )
    
    def sanitize_json_input(self, json_input: str, max_depth: int = 10) -> SanitizationResult:
        """Sanitize JSON input to prevent injection attacks."""
        if not isinstance(json_input, str):
            json_input = str(json_input)
        
        original_value = json_input
        warnings = []
        threats_detected = []
        
        try:
            # Parse JSON to validate structure
            data = json.loads(json_input)
            
            # Check nesting depth
            def check_depth(obj, current_depth=0):
                if current_depth > max_depth:
                    threats_detected.append(f"JSON nesting too deep: {current_depth}")
                    return
                
                if isinstance(obj, dict):
                    for value in obj.values():
                        check_depth(value, current_depth + 1)
                elif isinstance(obj, list):
                    for item in obj:
                        check_depth(item, current_depth + 1)
            
            check_depth(data)
            
            # Check for large arrays/objects
            def check_size(obj):
                if isinstance(obj, dict) and len(obj) > 1000:
                    warnings.append(f"Large object with {len(obj)} keys")
                elif isinstance(obj, list) and len(obj) > 10000:
                    warnings.append(f"Large array with {len(obj)} items")
                elif isinstance(obj, str) and len(obj) > 100000:
                    warnings.append(f"Large string with {len(obj)} characters")
            
            check_size(data)
            
            # Re-serialize to ensure clean JSON
            sanitized = json.dumps(data, separators=(',', ':'), ensure_ascii=True)
            
        except json.JSONDecodeError as e:
            threats_detected.append(f"Invalid JSON format: {str(e)}")
            sanitized = json_input
        
        # Check for suspicious patterns in raw JSON
        for pattern in self.dangerous_regex:
            if pattern.search(json_input):
                threats_detected.append("Dangerous pattern detected in JSON")
        
        is_safe = len(threats_detected) == 0
        
        return SanitizationResult(
            original_value=original_value,
            sanitized_value=sanitized,
            is_safe=is_safe,
            warnings=warnings,
            threats_detected=threats_detected
        )
    
    def sanitize_field_input(self, field_name: str, field_value: Any) -> SanitizationResult:
        """Sanitize input based on field type and rules."""
        if not isinstance(field_value, str):
            field_value = str(field_value)
        
        original_value = field_value
        warnings = []
        threats_detected = []
        
        # Get field length limit
        max_length = self.config.field_length_limits.get(field_name, 1000)
        
        # Trim to max length
        if len(field_value) > max_length:
            field_value = field_value[:max_length]
            warnings.append(f"Field truncated to {max_length} characters")
        
        # Field-specific sanitization
        if field_name in ['email']:
            # Email sanitization
            field_value = field_value.lower().strip()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', field_value):
                threats_detected.append("Invalid email format")
        
        elif field_name in ['username']:
            # Username sanitization
            field_value = re.sub(r'[^\w\.-]', '', field_value)
            if not re.match(r'^[a-zA-Z0-9_]{3,30}$', field_value):
                threats_detected.append("Invalid username format")
        
        elif field_name in ['phone']:
            # Phone number sanitization
            field_value = re.sub(r'[^\d+\-\(\)\s]', '', field_value)
        
        elif field_name in ['name', 'description', 'comment']:
            # General text sanitization
            html_result = self.sanitize_html(field_value, allow_tags=False)
            field_value = html_result.sanitized_value
            threats_detected.extend(html_result.threats_detected)
        
        # Remove null bytes
        if '\x00' in field_value:
            field_value = field_value.replace('\x00', '')
            threats_detected.append("Null byte detected and removed")
        
        # Check for control characters
        control_chars = re.findall(r'[\x00-\x1f\x7f-\x9f]', field_value)
        if control_chars:
            warnings.append(f"Control characters detected: {len(control_chars)}")
            field_value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', field_value)
        
        is_safe = len(threats_detected) == 0
        
        return SanitizationResult(
            original_value=original_value,
            sanitized_value=field_value,
            is_safe=is_safe,
            warnings=warnings,
            threats_detected=threats_detected
        )
    
    def sanitize_batch(self, data: Dict[str, Any]) -> Dict[str, SanitizationResult]:
        """Sanitize multiple fields in batch."""
        results = {}
        
        for field_name, field_value in data.items():
            if field_name.endswith('_url'):
                results[field_name] = self.sanitize_url(field_value)
            elif field_name.endswith('_html'):
                results[field_name] = self.sanitize_html(field_value, allow_tags=True)
            elif field_name.endswith('_json'):
                results[field_name] = self.sanitize_json_input(field_value)
            else:
                results[field_name] = self.sanitize_field_input(field_name, field_value)
        
        return results
    
    def generate_csrf_token(self, session_id: str, secret_key: str) -> str:
        """Generate CSRF token for form protection."""
        timestamp = str(int(datetime.now().timestamp()))
        token_data = f"{session_id}:{timestamp}:{secret_key}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        return base64.b64encode(f"{timestamp}:{token_hash}".encode()).decode()
    
    def validate_csrf_token(self, token: str, session_id: str, secret_key: str, 
                           max_age: int = 3600) -> bool:
        """Validate CSRF token."""
        try:
            decoded = base64.b64decode(token.encode()).decode()
            timestamp_str, token_hash = decoded.split(':', 1)
            
            # Check token age
            token_timestamp = int(timestamp_str)
            current_timestamp = int(datetime.now().timestamp())
            
            if current_timestamp - token_timestamp > max_age:
                return False
            
            # Verify token
            expected_data = f"{session_id}:{timestamp_str}:{secret_key}"
            expected_hash = hashlib.sha256(expected_data.encode()).hexdigest()
            
            return token_hash == expected_hash
            
        except Exception:
            return False


# Convenience functions
def sanitize_html_quick(html_content: str) -> str:
    """Quick HTML sanitization."""
    sanitizer = InputSanitizer()
    result = sanitizer.sanitize_html(html_content)
    return result.sanitized_value


def sanitize_sql_quick(sql_input: str) -> str:
    """Quick SQL input sanitization."""
    sanitizer = InputSanitizer()
    result = sanitizer.sanitize_sql_input(sql_input)
    return result.sanitized_value


def validate_file_upload_quick(filename: str, content: bytes) -> bool:
    """Quick file upload validation."""
    sanitizer = InputSanitizer()
    result = sanitizer.sanitize_file_upload(filename, content)
    return result.is_safe


def sanitize_url_quick(url: str) -> str:
    """Quick URL sanitization."""
    sanitizer = InputSanitizer()
    result = sanitizer.sanitize_url(url)
    return result.sanitized_value


# Example usage and testing
if __name__ == "__main__":
    sanitizer = InputSanitizer()
    
    # Test HTML sanitization
    html_test = '<script>alert("XSS")</script><p>Safe content</p>'
    html_result = sanitizer.sanitize_html(html_test)
    print(f"HTML sanitization: {html_result.to_dict()}")
    
    # Test SQL injection prevention
    sql_test = "'; DROP TABLE users; --"
    sql_result = sanitizer.sanitize_sql_input(sql_test)
    print(f"SQL sanitization: {sql_result.to_dict()}")
    
    # Test URL sanitization
    url_test = "javascript:alert('XSS')"
    url_result = sanitizer.sanitize_url(url_test)
    print(f"URL sanitization: {url_result.to_dict()}")
    
    # Test batch sanitization
    batch_data = {
        "username": "test_user!@#",
        "email": "TEST@EXAMPLE.COM",
        "comment_html": "<script>alert('test')</script><p>Comment</p>",
        "profile_url": "https://example.com/profile"
    }
    
    batch_results = sanitizer.sanitize_batch(batch_data)
    for field, result in batch_results.items():
        print(f"{field}: {result.to_dict()}")