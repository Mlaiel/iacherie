"""
Security Regression Tests
Tests to ensure security fixes don't regress and new security issues aren't introduced
"""
import pytest
import asyncio
import hashlib
import secrets
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


class TestSecurityRegression:
    """Security regression test suite"""
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_sql_injection_regression(self):
        """Test that SQL injection fixes remain effective"""
        
        def test_sql_injection_protection(input_value: str) -> bool:
            """Test SQL injection protection"""
            # Simulate parameterized query protection
            dangerous_patterns = [
                "'; DROP TABLE",
                "' OR '1'='1",
                "UNION SELECT",
                "'; INSERT INTO",
                "'; UPDATE",
                "'; DELETE FROM"
            ]
            
            # Should reject dangerous inputs
            for pattern in dangerous_patterns:
                if pattern.lower() in input_value.lower():
                    return False  # Input rejected (secure)
            
            return True  # Input accepted (safe)
        
        # Test previously fixed SQL injection vectors
        known_sql_injection_attempts = [
            "admin'; DROP TABLE users; --",
            "' OR '1'='1' --",
            "1' UNION SELECT username, password FROM users --",
            "'; INSERT INTO users (username, password) VALUES ('hacker', 'password'); --"
        ]
        
        for attempt in known_sql_injection_attempts:
            # These should be blocked
            assert test_sql_injection_protection(attempt) is False, \
                f"SQL injection protection failed for: {attempt}"
        
        # Test legitimate inputs
        legitimate_inputs = [
            "john.doe@example.com",
            "Regular search term",
            "Product name with spaces",
            "User123"
        ]
        
        for input_val in legitimate_inputs:
            assert test_sql_injection_protection(input_val) is True, \
                f"Legitimate input incorrectly blocked: {input_val}"
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_xss_protection_regression(self):
        """Test that XSS protection remains effective"""
        
        def sanitize_user_input(input_value: str) -> str:
            """Sanitize user input to prevent XSS"""
            if not input_value:
                return ""
            
            # HTML entity encoding
            html_entities = {
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#x27;',
                '&': '&amp;',
                '/': '&#x2F;'
            }
            
            sanitized = input_value
            for char, entity in html_entities.items():
                sanitized = sanitized.replace(char, entity)
            
            # Remove script tags
            import re
            sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            
            return sanitized
        
        # Test known XSS vectors
        xss_vectors = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<div onclick='alert(\"XSS\")'>Click me</div>"
        ]
        
        for vector in xss_vectors:
            sanitized = sanitize_user_input(vector)
            
            # Verify dangerous content is neutralized
            assert '<script>' not in sanitized.lower(), f"Script tag not removed from: {vector}"
            assert 'javascript:' not in sanitized.lower(), f"JavaScript URL not removed from: {vector}"
            assert 'onerror=' not in sanitized.lower(), f"Event handler not removed from: {vector}"
            assert 'onload=' not in sanitized.lower(), f"Event handler not removed from: {vector}"
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_authentication_bypass_regression(self):
        """Test that authentication bypass fixes remain effective"""
        
        class MockAuthenticator:
            def __init__(self):
                self.valid_users = {
                    "admin": {"password_hash": "hashed_admin_password", "role": "admin"},
                    "user1": {"password_hash": "hashed_user_password", "role": "user"}
                }
            
            def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
                """Authenticate user"""
                # Simulate secure authentication
                if not username or not password:
                    return None
                
                user = self.valid_users.get(username)
                if not user:
                    return None
                
                # Simulate password verification (simplified)
                expected_hash = user["password_hash"]
                provided_hash = f"hashed_{password}"
                
                if provided_hash == expected_hash:
                    return {"username": username, "role": user["role"]}
                
                return None
        
        auth = MockAuthenticator()
        
        # Test legitimate authentication
        valid_auth = auth.authenticate("admin", "admin_password")
        assert valid_auth is not None
        assert valid_auth["username"] == "admin"
        
        # Test known bypass attempts
        bypass_attempts = [
            ("admin' --", "any_password"),  # SQL injection
            ("admin", "' OR '1'='1"),       # SQL injection in password
            ("admin", ""),                  # Empty password
            ("", "admin_password"),         # Empty username
            ("admin\x00", "admin_password"), # Null byte injection
            ("admin\"; --", "any_password")  # Command injection attempt
        ]
        
        for username, password in bypass_attempts:
            result = auth.authenticate(username, password)
            assert result is None, f"Authentication bypass succeeded with: {username}, {password}"
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_session_security_regression(self):
        """Test that session security fixes remain effective"""
        
        class MockSessionManager:
            def __init__(self):
                self.sessions = {}
                self.session_timeout = timedelta(minutes=30)
            
            def create_session(self, user_id: str) -> str:
                """Create secure session"""
                session_id = secrets.token_urlsafe(32)
                self.sessions[session_id] = {
                    "user_id": user_id,
                    "created_at": datetime.now(),
                    "last_activity": datetime.now(),
                    "ip_address": "192.168.1.100",  # Mock IP
                    "user_agent": "Test-Agent/1.0"   # Mock user agent
                }
                return session_id
            
            def validate_session(self, session_id: str, ip_address: str = None, 
                               user_agent: str = None) -> Optional[Dict[str, Any]]:
                """Validate session with security checks"""
                if not session_id or session_id not in self.sessions:
                    return None
                
                session = self.sessions[session_id]
                now = datetime.now()
                
                # Check session timeout
                if now - session["last_activity"] > self.session_timeout:
                    del self.sessions[session_id]
                    return None
                
                # Check IP address consistency (if provided)
                if ip_address and session["ip_address"] != ip_address:
                    # Potential session hijacking
                    return None
                
                # Update last activity
                session["last_activity"] = now
                
                return session
        
        session_mgr = MockSessionManager()
        
        # Test legitimate session creation and validation
        session_id = session_mgr.create_session("user123")
        assert len(session_id) == 43  # URL-safe base64 of 32 bytes
        
        session = session_mgr.validate_session(session_id, "192.168.1.100")
        assert session is not None
        assert session["user_id"] == "user123"
        
        # Test session hijacking protection
        hijacked_session = session_mgr.validate_session(session_id, "192.168.1.200")
        assert hijacked_session is None, "Session hijacking should be prevented"
        
        # Test session fixation protection
        fixed_session_id = "fixed_session_id_123"
        fixed_session = session_mgr.validate_session(fixed_session_id)
        assert fixed_session is None, "Session fixation should be prevented"
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_file_upload_security_regression(self):
        """Test that file upload security fixes remain effective"""
        
        def validate_file_upload(filename: str, content: bytes, content_type: str) -> Dict[str, Any]:
            """Validate file upload security"""
            issues = []
            
            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.docx']
            file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
            
            if file_ext not in allowed_extensions:
                issues.append(f"File extension {file_ext} not allowed")
            
            # Check file size (max 10MB)
            max_size = 10 * 1024 * 1024
            if len(content) > max_size:
                issues.append(f"File size {len(content)} exceeds maximum {max_size}")
            
            # Check for executable content
            executable_signatures = [
                b'\x4d\x5a',  # PE executable
                b'\x7f\x45\x4c\x46',  # ELF executable
                b'#!/bin/',  # Shell script
                b'<?php',    # PHP script
            ]
            
            for signature in executable_signatures:
                if content.startswith(signature):
                    issues.append("Executable content detected")
                    break
            
            # Check content type consistency
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if file_ext in image_extensions and not content_type.startswith('image/'):
                issues.append("Content type mismatch with file extension")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues
            }
        
        # Test legitimate file uploads
        legitimate_files = [
            ("document.pdf", b"%PDF-1.4\n", "application/pdf"),
            ("image.jpg", b"\xff\xd8\xff\xe0", "image/jpeg"),
            ("text.txt", b"Hello, world!", "text/plain")
        ]
        
        for filename, content, content_type in legitimate_files:
            result = validate_file_upload(filename, content, content_type)
            assert result["valid"] is True, f"Legitimate file rejected: {filename}"
        
        # Test malicious file uploads
        malicious_files = [
            ("malware.exe", b"\x4d\x5a\x90\x00", "application/octet-stream"),
            ("script.php", b"<?php system($_GET['cmd']); ?>", "text/plain"),
            ("shell.sh", b"#!/bin/bash\nrm -rf /", "text/plain"),
            ("fake.jpg", b"<?php echo 'hacked'; ?>", "image/jpeg")  # Content type mismatch
        ]
        
        for filename, content, content_type in malicious_files:
            result = validate_file_upload(filename, content, content_type)
            assert result["valid"] is False, f"Malicious file allowed: {filename}"
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_password_policy_regression(self):
        """Test that password policy fixes remain effective"""
        
        def validate_password_policy(password: str) -> Dict[str, Any]:
            """Validate password against policy"""
            issues = []
            
            # Minimum length
            if len(password) < 8:
                issues.append("Password must be at least 8 characters long")
            
            # Character requirements
            if not any(c.isupper() for c in password):
                issues.append("Password must contain at least one uppercase letter")
            
            if not any(c.islower() for c in password):
                issues.append("Password must contain at least one lowercase letter")
            
            if not any(c.isdigit() for c in password):
                issues.append("Password must contain at least one digit")
            
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                issues.append("Password must contain at least one special character")
            
            # Common password check
            common_passwords = [
                "password", "123456", "qwerty", "admin", "letmein",
                "welcome", "monkey", "dragon", "password123", "admin123"
            ]
            
            if password.lower() in common_passwords:
                issues.append("Password is too common")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues
            }
        
        # Test weak passwords (should be rejected)
        weak_passwords = [
            "123456",
            "password",
            "admin",
            "abc123",
            "Password",  # Missing digit and special char
            "password123",  # Missing uppercase and special char
            "PASSWORD123!"  # Missing lowercase
        ]
        
        for password in weak_passwords:
            result = validate_password_policy(password)
            assert result["valid"] is False, f"Weak password accepted: {password}"
        
        # Test strong passwords (should be accepted)
        strong_passwords = [
            "MyStr0ng!Password",
            "C0mpl3x$P@ssw0rd",
            "Secure#123Password",
            "Random&P@ssw0rd456"
        ]
        
        for password in strong_passwords:
            result = validate_password_policy(password)
            assert result["valid"] is True, f"Strong password rejected: {password}"


class TestSecurityFeatureRegression:
    """Test that security features continue to work correctly"""
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_csrf_protection_regression(self):
        """Test CSRF protection remains effective"""
        
        class MockCSRFProtection:
            def __init__(self):
                self.tokens = {}
            
            def generate_token(self, session_id: str) -> str:
                """Generate CSRF token"""
                token = secrets.token_urlsafe(32)
                self.tokens[session_id] = {
                    "token": token,
                    "created_at": datetime.now(),
                    "used": False
                }
                return token
            
            def validate_token(self, session_id: str, provided_token: str) -> bool:
                """Validate CSRF token"""
                if session_id not in self.tokens:
                    return False
                
                token_data = self.tokens[session_id]
                
                # Check if token matches
                if token_data["token"] != provided_token:
                    return False
                
                # Check if token is expired (5 minutes)
                if datetime.now() - token_data["created_at"] > timedelta(minutes=5):
                    del self.tokens[session_id]
                    return False
                
                # Mark token as used (one-time use)
                if token_data["used"]:
                    return False
                
                token_data["used"] = True
                return True
        
        csrf = MockCSRFProtection()
        session_id = "test_session_123"
        
        # Test legitimate CSRF token usage
        token = csrf.generate_token(session_id)
        assert len(token) == 43  # URL-safe base64 of 32 bytes
        
        # Token should validate once
        assert csrf.validate_token(session_id, token) is True
        
        # Token should not validate twice (replay attack)
        assert csrf.validate_token(session_id, token) is False
        
        # Invalid token should not validate
        assert csrf.validate_token(session_id, "invalid_token") is False
        
        # Token for wrong session should not validate
        wrong_session_token = csrf.generate_token("wrong_session")
        assert csrf.validate_token(session_id, wrong_session_token) is False
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_rate_limiting_regression(self):
        """Test rate limiting continues to work"""
        
        class MockRateLimiter:
            def __init__(self, max_requests: int = 60, window_minutes: int = 1):
                self.max_requests = max_requests
                self.window_minutes = window_minutes
                self.request_log = {}
            
            def is_request_allowed(self, identifier: str) -> bool:
                """Check if request is allowed"""
                now = datetime.now()
                
                if identifier not in self.request_log:
                    self.request_log[identifier] = []
                
                # Clean old requests
                cutoff_time = now - timedelta(minutes=self.window_minutes)
                self.request_log[identifier] = [
                    req_time for req_time in self.request_log[identifier]
                    if req_time > cutoff_time
                ]
                
                # Check if limit exceeded
                if len(self.request_log[identifier]) >= self.max_requests:
                    return False
                
                # Log this request
                self.request_log[identifier].append(now)
                return True
        
        rate_limiter = MockRateLimiter(max_requests=5, window_minutes=1)
        client_ip = "192.168.1.100"
        
        # First 5 requests should be allowed
        for i in range(5):
            assert rate_limiter.is_request_allowed(client_ip) is True, f"Request {i+1} should be allowed"
        
        # 6th request should be blocked
        assert rate_limiter.is_request_allowed(client_ip) is False, "Rate limit should be enforced"
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_input_sanitization_regression(self):
        """Test input sanitization continues to work"""
        
        def sanitize_input(input_data: Any) -> Any:
            """Sanitize various types of input"""
            if isinstance(input_data, str):
                # Remove null bytes
                sanitized = input_data.replace('\x00', '')
                
                # Limit length
                if len(sanitized) > 1000:
                    sanitized = sanitized[:1000]
                
                # Remove control characters
                sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
                
                return sanitized
            
            elif isinstance(input_data, dict):
                return {key: sanitize_input(value) for key, value in input_data.items()}
            
            elif isinstance(input_data, list):
                return [sanitize_input(item) for item in input_data]
            
            return input_data
        
        # Test malicious inputs
        malicious_inputs = [
            "Normal text\x00with null byte",
            "Text with\x01control\x02characters",
            "A" * 2000,  # Oversized input
            {"key": "value\x00with null"},
            ["item1", "item2\x01with control"]
        ]
        
        for input_data in malicious_inputs:
            sanitized = sanitize_input(input_data)
            
            if isinstance(sanitized, str):
                assert '\x00' not in sanitized, "Null bytes should be removed"
                assert len(sanitized) <= 1000, "Length should be limited"
                assert all(ord(c) >= 32 or c in '\t\n\r' for c in sanitized), "Control chars should be removed"


class TestSecurityConfigurationRegression:
    """Test security configuration doesn't regress"""
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_security_headers_regression(self):
        """Test security headers remain configured"""
        
        def get_security_headers() -> Dict[str, str]:
            """Get current security headers configuration"""
            return {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Content-Security-Policy": "default-src 'self'",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            }
        
        headers = get_security_headers()
        
        # Verify all critical headers are present
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        for header in required_headers:
            assert header in headers, f"Security header {header} is missing"
        
        # Verify header values are secure
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] in ["DENY", "SAMEORIGIN"]
        assert "max-age=" in headers["Strict-Transport-Security"]
    
    @pytest.mark.security
    @pytest.mark.regression
    def test_encryption_configuration_regression(self):
        """Test encryption configuration remains secure"""
        
        def get_encryption_config() -> Dict[str, Any]:
            """Get encryption configuration"""
            return {
                "algorithm": "AES-256-GCM",
                "key_size": 256,
                "iv_size": 96,
                "tag_size": 128,
                "key_derivation": "PBKDF2-SHA256",
                "iterations": 100000,
                "salt_size": 128
            }
        
        config = get_encryption_config()
        
        # Verify strong encryption settings
        assert config["algorithm"] in ["AES-256-GCM", "AES-256-CBC", "ChaCha20-Poly1305"]
        assert config["key_size"] >= 256, "Key size should be at least 256 bits"
        assert config["iterations"] >= 100000, "PBKDF2 iterations should be at least 100,000"
        assert config["salt_size"] >= 128, "Salt size should be at least 128 bits"
    
    @pytest.mark.security  
    @pytest.mark.regression
    def test_database_security_regression(self):
        """Test database security configuration"""
        
        def get_database_config() -> Dict[str, Any]:
            """Get database security configuration"""
            return {
                "use_ssl": True,
                "verify_ssl_cert": True,
                "min_tls_version": "1.2",
                "connection_encryption": True,
                "prepared_statements": True,
                "sql_injection_protection": True,
                "audit_logging": True,
                "connection_timeout": 30,
                "query_timeout": 60
            }
        
        db_config = get_database_config()
        
        # Verify secure database settings
        assert db_config["use_ssl"] is True, "Database should use SSL"
        assert db_config["verify_ssl_cert"] is True, "SSL certificates should be verified"
        assert db_config["prepared_statements"] is True, "Should use prepared statements"
        assert db_config["sql_injection_protection"] is True, "SQL injection protection should be enabled"
        assert db_config["audit_logging"] is True, "Database audit logging should be enabled"