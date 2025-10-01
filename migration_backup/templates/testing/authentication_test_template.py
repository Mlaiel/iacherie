
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
"""
🔒 AUTHENTICATION TEST TEMPLATE - SECURITY EXPERT IMPLEMENTATION
================================================================

Enterprise-grade authentication testing template for IA Chéries Creator Economy Platform.
Comprehensive security testing covering:
- JWT authentication validation
- OAuth2 integration testing
- Multi-factor authentication (MFA) 
- Session management security
- Token lifecycle testing
- Authentication bypass prevention
- Rate limiting validation
- Password policy enforcement

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Security Expert & Testing Specialist
Team: Lead Dev IA + Backend Senior + Security Engineer
Version: 1.0.0
"""

import pytest
import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import jwt
import pyotp
import httpx
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from faker import Faker
import bcrypt
from cryptography.fernet import Fernet
import secrets
import base64
from passlib.context import CryptContext
import re

# Application imports
from core.security import SecurityManager, TokenManager, AuthenticationService
from core.config import get_settings
from utils.exceptions import AuthenticationError, ValidationError, SecurityError
from monitoring.test_metrics import TestMetricsCollector
from tests.fixtures import create_test_user, generate_test_credentials

# Initialize test utilities
fake = Faker()
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class AuthTestContext:
    """Authentication test context with security utilities"""
    
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = field(default_factory=fake.user_name)
    email: str = field(default_factory=fake.email)
    password: str = field(default="TestPass123!")
    mfa_secret: str = field(default_factory=pyotp.random_base32)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    session_id: Optional[str] = None
    csrf_token: Optional[str] = None
    device_fingerprint: Optional[str] = None
    ip_address: str = field(default_factory=fake.ipv4)
    user_agent: str = field(default_factory=fake.user_agent)
    
    def __post_init__(self):
        self.password_hash = pwd_context.hash(self.password)
        self.device_fingerprint = hashlib.sha256(
            f"{self.user_agent}{self.ip_address}".encode()
        ).hexdigest()


class AuthenticationTestTemplate:
    """
    🔒 ENTERPRISE AUTHENTICATION TESTING FRAMEWORK
    
    Comprehensive authentication testing template providing:
    - JWT token validation and security testing
    - OAuth2 flow testing with provider simulation
    - Multi-factor authentication (MFA) validation
    - Session management and security testing
    - Rate limiting and brute force protection
    - Password policy and strength validation
    - Authentication bypass attempt detection
    - Token lifecycle and refresh testing
    - Device fingerprinting validation
    - CSRF protection testing
    """
    
    def __init__(self):
        self.security_manager = SecurityManager()
        self.token_manager = TokenManager()
        self.auth_service = AuthenticationService()
        self.metrics_collector = TestMetricsCollector("authentication")
        self.test_contexts: List[AuthTestContext] = []
        
    async def setup_test_environment(self) -> AuthTestContext:
        """Setup isolated authentication test environment"""
        context = AuthTestContext()
        self.test_contexts.append(context)
        
        # Create test user with proper authentication setup
        await self._create_test_user(context)
        
        return context
    
    async def teardown_test_environment(self, context: AuthTestContext):
        """Clean up authentication test environment"""
        try:
            # Revoke all tokens
            if context.access_token:
                await self.token_manager.revoke_token(context.access_token)
            if context.refresh_token:
                await self.token_manager.revoke_token(context.refresh_token)
            
            # Clear sessions
            if context.session_id:
                await self.auth_service.destroy_session(context.session_id)
                
            # Remove test user
            await self._cleanup_test_user(context)
            
        except Exception as e:
            self.metrics_collector.record_error("teardown_failed", str(e))
    
    async def _create_test_user(self, context: AuthTestContext):
        """Create test user with authentication data"""
        user_data = {
            "id": context.user_id,
            "username": context.username,
            "email": context.email,
            "password_hash": context.password_hash,
            "mfa_secret": context.mfa_secret,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "login_attempts": 0,
            "locked_until": None
        }
        
        await self.auth_service.create_user(user_data)
    
    async def _cleanup_test_user(self, context: AuthTestContext):
        """Remove test user and associated data"""
        await self.auth_service.delete_user(context.user_id)

    # ==================== JWT AUTHENTICATION TESTS ====================
    
    async def test_jwt_token_generation(self, context: AuthTestContext):
        """Test JWT token generation with proper claims"""
        start_time = time.time()
        
        try:
            # Generate access token
            token_data = {
                "sub": context.user_id,
                "username": context.username,
                "email": context.email,
                "scopes": ["read", "write"],
                "device_id": context.device_fingerprint
            }
            
            access_token = await self.token_manager.create_access_token(token_data)
            
            # Validate token structure
            assert access_token is not None
            assert isinstance(access_token, str)
            assert len(access_token.split('.')) == 3  # Header.Payload.Signature
            
            # Decode and validate claims
            decoded = jwt.decode(
                access_token, 
                self.token_manager.secret_key, 
                algorithms=["HS256"]
            )
            
            assert decoded["sub"] == context.user_id
            assert decoded["username"] == context.username
            assert decoded["scopes"] == ["read", "write"]
            assert "exp" in decoded
            assert "iat" in decoded
            assert "jti" in decoded  # JWT ID for tracking
            
            context.access_token = access_token
            
            self.metrics_collector.record_success(
                "jwt_generation", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("jwt_generation_failed", str(e))
            raise AssertionError(f"JWT generation failed: {e}")
    
    async def test_jwt_token_validation(self, context: AuthTestContext):
        """Test JWT token validation and verification"""
        start_time = time.time()
        
        try:
            # First generate a valid token
            if not context.access_token:
                await self.test_jwt_token_generation(context)
            
            # Validate token
            is_valid = await self.token_manager.validate_token(context.access_token)
            assert is_valid is True
            
            # Get user from token
            user_data = await self.token_manager.get_user_from_token(context.access_token)
            assert user_data["id"] == context.user_id
            assert user_data["username"] == context.username
            
            self.metrics_collector.record_success(
                "jwt_validation", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("jwt_validation_failed", str(e))
            raise AssertionError(f"JWT validation failed: {e}")
    
    async def test_jwt_token_expiration(self, context: AuthTestContext):
        """Test JWT token expiration handling"""
        start_time = time.time()
        
        try:
            # Create short-lived token (1 second)
            token_data = {
                "sub": context.user_id,
                "username": context.username,
                "exp": datetime.utcnow() + timedelta(seconds=1)
            }
            
            expired_token = await self.token_manager.create_access_token(
                token_data, 
                expires_delta=timedelta(seconds=1)
            )
            
            # Token should be valid initially
            assert await self.token_manager.validate_token(expired_token) is True
            
            # Wait for expiration
            await asyncio.sleep(2)
            
            # Token should now be expired
            assert await self.token_manager.validate_token(expired_token) is False
            
            # Verify proper exception is raised
            with pytest.raises(AuthenticationError, match="Token expired"):
                await self.token_manager.get_user_from_token(expired_token)
            
            self.metrics_collector.record_success(
                "jwt_expiration", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("jwt_expiration_failed", str(e))
            raise AssertionError(f"JWT expiration test failed: {e}")
    
    async def test_jwt_token_tampering_detection(self, context: AuthTestContext):
        """Test JWT token tampering detection"""
        start_time = time.time()
        
        try:
            if not context.access_token:
                await self.test_jwt_token_generation(context)
            
            original_token = context.access_token
            
            # Test 1: Modify signature
            parts = original_token.split('.')
            tampered_signature = parts[0] + '.' + parts[1] + '.tampered'
            
            assert await self.token_manager.validate_token(tampered_signature) is False
            
            # Test 2: Modify payload
            import base64
            payload = json.loads(base64.b64decode(parts[1] + '=='))
            payload['sub'] = 'malicious_user'
            tampered_payload = base64.b64encode(json.dumps(payload).encode()).decode().rstrip('=')
            tampered_token = parts[0] + '.' + tampered_payload + '.' + parts[2]
            
            assert await self.token_manager.validate_token(tampered_token) is False
            
            # Test 3: Use wrong secret
            wrong_secret_token = jwt.encode(
                {"sub": context.user_id}, 
                "wrong_secret", 
                algorithm="HS256"
            )
            
            assert await self.token_manager.validate_token(wrong_secret_token) is False
            
            self.metrics_collector.record_success(
                "jwt_tampering_detection", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("jwt_tampering_failed", str(e))
            raise AssertionError(f"JWT tampering detection failed: {e}")

    # ==================== MULTI-FACTOR AUTHENTICATION TESTS ====================
    
    async def test_mfa_totp_generation_validation(self, context: AuthTestContext):
        """Test TOTP MFA generation and validation"""
        start_time = time.time()
        
        try:
            # Generate TOTP token
            totp = pyotp.TOTP(context.mfa_secret)
            current_token = totp.now()
            
            # Validate TOTP token
            is_valid = await self.auth_service.validate_mfa_token(
                context.user_id, 
                current_token
            )
            assert is_valid is True
            
            # Test invalid token
            invalid_token = "123456"
            is_valid = await self.auth_service.validate_mfa_token(
                context.user_id, 
                invalid_token
            )
            assert is_valid is False
            
            # Test token reuse protection
            is_valid_reuse = await self.auth_service.validate_mfa_token(
                context.user_id, 
                current_token
            )
            assert is_valid_reuse is False  # Should reject reused token
            
            self.metrics_collector.record_success(
                "mfa_totp_validation", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("mfa_totp_failed", str(e))
            raise AssertionError(f"MFA TOTP validation failed: {e}")
    
    async def test_mfa_backup_codes(self, context: AuthTestContext):
        """Test MFA backup codes generation and usage"""
        start_time = time.time()
        
        try:
            # Generate backup codes
            backup_codes = await self.auth_service.generate_backup_codes(context.user_id)
            
            assert len(backup_codes) == 10  # Standard number of backup codes
            assert all(len(code) == 8 for code in backup_codes)  # 8-character codes
            assert all(code.isalnum() for code in backup_codes)  # Alphanumeric only
            
            # Use a backup code
            test_code = backup_codes[0]
            is_valid = await self.auth_service.validate_backup_code(
                context.user_id, 
                test_code
            )
            assert is_valid is True
            
            # Test that same code cannot be reused
            is_valid_reuse = await self.auth_service.validate_backup_code(
                context.user_id, 
                test_code
            )
            assert is_valid_reuse is False
            
            # Test invalid backup code
            is_valid_invalid = await self.auth_service.validate_backup_code(
                context.user_id, 
                "invalid123"
            )
            assert is_valid_invalid is False
            
            self.metrics_collector.record_success(
                "mfa_backup_codes", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("mfa_backup_codes_failed", str(e))
            raise AssertionError(f"MFA backup codes test failed: {e}")

    # ==================== RATE LIMITING & BRUTE FORCE PROTECTION ====================
    
    async def test_login_rate_limiting(self, context: AuthTestContext):
        """Test login rate limiting and brute force protection"""
        start_time = time.time()
        
        try:
            max_attempts = 5
            
            # Perform multiple failed login attempts
            for attempt in range(max_attempts + 2):
                try:
                    result = await self.auth_service.authenticate(
                        context.username,
                        "wrong_password",
                        context.ip_address
                    )
                    
                    if attempt < max_attempts:
                        assert result is False
                    else:
                        # Should be rate limited after max attempts
                        assert False, "Should have been rate limited"
                        
                except SecurityError as e:
                    if attempt >= max_attempts:
                        assert "rate limit" in str(e).lower()
                    else:
                        raise AssertionError(f"Unexpected rate limit at attempt {attempt}")
            
            # Verify account is locked
            user_status = await self.auth_service.get_user_status(context.user_id)
            assert user_status.get("locked") is True
            assert user_status.get("locked_until") is not None
            
            self.metrics_collector.record_success(
                "login_rate_limiting", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("login_rate_limiting_failed", str(e))
            raise AssertionError(f"Login rate limiting test failed: {e}")
    
    async def test_password_policy_enforcement(self, context: AuthTestContext):
        """Test password policy enforcement"""
        start_time = time.time()
        
        try:
            weak_passwords = [
                "123456",           # Too simple
                "password",         # Common password
                "abc",              # Too short
                "ALLUPPERCASE",     # No lowercase
                "alllowercase",     # No uppercase
                "NoNumbers!",       # No numbers
                "NoSpecialChars123" # No special characters
            ]
            
            for weak_password in weak_passwords:
                with pytest.raises(ValidationError):
                    await self.auth_service.validate_password_strength(weak_password)
            
            # Test strong password
            strong_password = "StrongP@ssw0rd123!"
            validation_result = await self.auth_service.validate_password_strength(strong_password)
            assert validation_result["is_valid"] is True
            assert validation_result["strength_score"] >= 80
            
            # Test password history prevention
            await self.auth_service.change_password(
                context.user_id, 
                context.password, 
                strong_password
            )
            
            # Try to reuse old password
            with pytest.raises(ValidationError, match="password history"):
                await self.auth_service.change_password(
                    context.user_id, 
                    strong_password, 
                    context.password
                )
            
            self.metrics_collector.record_success(
                "password_policy", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("password_policy_failed", str(e))
            raise AssertionError(f"Password policy test failed: {e}")

    # ==================== SESSION MANAGEMENT TESTS ====================
    
    async def test_session_creation_management(self, context: AuthTestContext):
        """Test session creation and management"""
        start_time = time.time()
        
        try:
            # Create session
            session_data = {
                "user_id": context.user_id,
                "ip_address": context.ip_address,
                "user_agent": context.user_agent,
                "device_fingerprint": context.device_fingerprint
            }
            
            session_id = await self.auth_service.create_session(session_data)
            context.session_id = session_id
            
            assert session_id is not None
            assert isinstance(session_id, str)
            assert len(session_id) >= 32  # Sufficient entropy
            
            # Validate session
            session = await self.auth_service.get_session(session_id)
            assert session["user_id"] == context.user_id
            assert session["ip_address"] == context.ip_address
            assert session["is_active"] is True
            
            # Test session timeout
            await self.auth_service.update_session_activity(session_id)
            updated_session = await self.auth_service.get_session(session_id)
            assert updated_session["last_activity"] > session["last_activity"]
            
            self.metrics_collector.record_success(
                "session_management", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("session_management_failed", str(e))
            raise AssertionError(f"Session management test failed: {e}")
    
    async def test_concurrent_session_limits(self, context: AuthTestContext):
        """Test concurrent session limits"""
        start_time = time.time()
        
        try:
            max_sessions = 3
            created_sessions = []
            
            # Create multiple sessions
            for i in range(max_sessions + 1):
                session_data = {
                    "user_id": context.user_id,
                    "ip_address": f"192.168.1.{i + 1}",
                    "user_agent": f"TestAgent_{i}",
                    "device_fingerprint": hashlib.sha256(f"device_{i}".encode()).hexdigest()
                }
                
                if i < max_sessions:
                    session_id = await self.auth_service.create_session(session_data)
                    created_sessions.append(session_id)
                else:
                    # Should enforce session limit
                    with pytest.raises(SecurityError, match="session limit"):
                        await self.auth_service.create_session(session_data)
            
            # Verify all allowed sessions are active
            for session_id in created_sessions:
                session = await self.auth_service.get_session(session_id)
                assert session["is_active"] is True
            
            self.metrics_collector.record_success(
                "concurrent_session_limits", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("concurrent_session_limits_failed", str(e))
            raise AssertionError(f"Concurrent session limits test failed: {e}")

    # ==================== OAUTH2 INTEGRATION TESTS ====================
    
    async def test_oauth2_authorization_flow(self, context: AuthTestContext):
        """Test OAuth2 authorization code flow"""
        start_time = time.time()
        
        try:
            # Mock OAuth2 provider
            oauth_provider = "google"
            client_id = "test_client_id"
            client_secret = "test_client_secret"
            redirect_uri = "https://ainflue.com/auth/callback"
            
            # Step 1: Generate authorization URL
            auth_url = await self.auth_service.generate_oauth_auth_url(
                oauth_provider,
                client_id,
                redirect_uri,
                ["email", "profile"]
            )
            
            assert oauth_provider in auth_url
            assert client_id in auth_url
            assert redirect_uri in auth_url
            assert "scope" in auth_url
            assert "state" in auth_url  # CSRF protection
            
            # Step 2: Mock authorization code callback
            auth_code = "mock_auth_code_12345"
            state = "csrf_state_token"
            
            # Step 3: Exchange code for tokens
            with patch.object(self.auth_service, '_exchange_oauth_code') as mock_exchange:
                mock_exchange.return_value = {
                    "access_token": "oauth_access_token",
                    "refresh_token": "oauth_refresh_token",
                    "expires_in": 3600,
                    "token_type": "Bearer"
                }
                
                tokens = await self.auth_service.handle_oauth_callback(
                    oauth_provider,
                    auth_code,
                    state,
                    client_id,
                    client_secret,
                    redirect_uri
                )
                
                assert tokens["access_token"] == "oauth_access_token"
                assert tokens["token_type"] == "Bearer"
                assert tokens["expires_in"] == 3600
            
            self.metrics_collector.record_success(
                "oauth2_flow", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("oauth2_flow_failed", str(e))
            raise AssertionError(f"OAuth2 flow test failed: {e}")

    # ==================== SECURITY VULNERABILITY TESTS ====================
    
    async def test_authentication_bypass_attempts(self, context: AuthTestContext):
        """Test authentication bypass prevention"""
        start_time = time.time()
        
        try:
            bypass_attempts = [
                # SQL injection attempts
                {"username": "admin' OR '1'='1", "password": "password"},
                {"username": "admin", "password": "' OR '1'='1"},
                
                # NoSQL injection attempts
                {"username": {"$ne": None}, "password": {"$ne": None}},
                
                # Header manipulation
                {"username": "admin", "password": "password", "headers": {"X-Forwarded-For": "127.0.0.1"}},
                
                # Empty/null values
                {"username": "", "password": ""},
                {"username": None, "password": None},
            ]
            
            for attempt in bypass_attempts:
                try:
                    result = await self.auth_service.authenticate(
                        attempt.get("username"),
                        attempt.get("password"),
                        context.ip_address,
                        headers=attempt.get("headers", {})
                    )
                    
                    # All bypass attempts should fail
                    assert result is False or result is None
                    
                except (ValidationError, SecurityError):
                    # Expected - security measures should catch these
                    pass
                except Exception as e:
                    # Unexpected error - potential vulnerability
                    raise AssertionError(f"Unexpected error with bypass attempt {attempt}: {e}")
            
            self.metrics_collector.record_success(
                "authentication_bypass_prevention", 
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("authentication_bypass_failed", str(e))
            raise AssertionError(f"Authentication bypass test failed: {e}")

    # ==================== PERFORMANCE & LOAD TESTING ====================
    
    async def test_authentication_performance(self, context: AuthTestContext):
        """Test authentication performance under load"""
        start_time = time.time()
        
        try:
            # Test concurrent authentication requests
            concurrent_requests = 50
            max_response_time = 1.0  # 1 second max
            
            async def authenticate_user():
                auth_start = time.time()
                result = await self.auth_service.authenticate(
                    context.username,
                    context.password,
                    context.ip_address
                )
                auth_time = time.time() - auth_start
                return result, auth_time
            
            # Run concurrent authentication tests
            tasks = [authenticate_user() for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_auths = 0
            total_auth_time = 0
            
            for result in results:
                if isinstance(result, tuple):
                    auth_result, auth_time = result
                    if auth_result:
                        successful_auths += 1
                        total_auth_time += auth_time
                        assert auth_time < max_response_time, f"Authentication took {auth_time}s (max: {max_response_time}s)"
            
            # Performance assertions
            success_rate = successful_auths / concurrent_requests
            avg_response_time = total_auth_time / successful_auths if successful_auths > 0 else 0
            
            assert success_rate >= 0.95, f"Success rate {success_rate} below 95%"
            assert avg_response_time < max_response_time / 2, f"Average response time {avg_response_time}s too high"
            
            self.metrics_collector.record_performance(
                "authentication_load_test",
                {
                    "concurrent_requests": concurrent_requests,
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "total_time": time.time() - start_time
                }
            )
            
        except Exception as e:
            self.metrics_collector.record_error("authentication_performance_failed", str(e))
            raise AssertionError(f"Authentication performance test failed: {e}")

    # ==================== COMPREHENSIVE TEST SUITE ====================
    
    async def run_comprehensive_authentication_tests(self) -> Dict[str, Any]:
        """Run complete authentication test suite"""
        print("🔒 Starting Comprehensive Authentication Security Testing...")
        
        context = await self.setup_test_environment()
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "performance_metrics": {},
            "security_score": 0
        }
        
        test_methods = [
            # JWT Tests
            self.test_jwt_token_generation,
            self.test_jwt_token_validation,
            self.test_jwt_token_expiration,
            self.test_jwt_token_tampering_detection,
            
            # MFA Tests
            self.test_mfa_totp_generation_validation,
            self.test_mfa_backup_codes,
            
            # Rate Limiting Tests
            self.test_login_rate_limiting,
            self.test_password_policy_enforcement,
            
            # Session Management Tests
            self.test_session_creation_management,
            self.test_concurrent_session_limits,
            
            # OAuth2 Tests
            self.test_oauth2_authorization_flow,
            
            # Security Tests
            self.test_authentication_bypass_attempts,
            
            # Performance Tests
            self.test_authentication_performance,
        ]
        
        for test_method in test_methods:
            test_results["total_tests"] += 1
            test_name = test_method.__name__
            
            try:
                print(f"  Running {test_name}...")
                await test_method(context)
                test_results["passed_tests"] += 1
                test_results["test_details"].append({
                    "name": test_name,
                    "status": "PASSED",
                    "error": None
                })
                print(f"  ✅ {test_name} PASSED")
                
            except Exception as e:
                test_results["failed_tests"] += 1
                test_results["test_details"].append({
                    "name": test_name,
                    "status": "FAILED",
                    "error": str(e)
                })
                print(f"  ❌ {test_name} FAILED: {e}")
        
        # Calculate security score
        security_score = (test_results["passed_tests"] / test_results["total_tests"]) * 100
        test_results["security_score"] = security_score
        
        # Collect performance metrics
        test_results["performance_metrics"] = self.metrics_collector.get_metrics()
        
        await self.teardown_test_environment(context)
        
        print(f"\n🔒 Authentication Testing Complete!")
        print(f"   Tests Passed: {test_results['passed_tests']}/{test_results['total_tests']}")
        print(f"   Security Score: {security_score:.1f}%")
        
        return test_results


# ==================== PYTEST INTEGRATION ====================

@pytest.fixture
async def auth_test_template():
    """Pytest fixture for authentication testing"""
    template = AuthenticationTestTemplate()
    yield template
    # Cleanup handled by template

@pytest.fixture
async def auth_context(auth_test_template):
    """Pytest fixture for authentication context"""
    context = await auth_test_template.setup_test_environment()
    yield context
    await auth_test_template.teardown_test_environment(context)

# Individual test functions for pytest discovery
@pytest.mark.asyncio
async def test_jwt_authentication(auth_test_template, auth_context):
    """Test JWT authentication functionality"""
    await auth_test_template.test_jwt_token_generation(auth_context)
    await auth_test_template.test_jwt_token_validation(auth_context)

@pytest.mark.asyncio
async def test_mfa_security(auth_test_template, auth_context):
    """Test multi-factor authentication security"""
    await auth_test_template.test_mfa_totp_generation_validation(auth_context)
    await auth_test_template.test_mfa_backup_codes(auth_context)

@pytest.mark.asyncio
async def test_brute_force_protection(auth_test_template, auth_context):
    """Test brute force protection mechanisms"""
    await auth_test_template.test_login_rate_limiting(auth_context)
    await auth_test_template.test_password_policy_enforcement(auth_context)

@pytest.mark.asyncio
async def test_session_security(auth_test_template, auth_context):
    """Test session management security"""
    await auth_test_template.test_session_creation_management(auth_context)
    await auth_test_template.test_concurrent_session_limits(auth_context)

@pytest.mark.asyncio
async def test_oauth2_integration(auth_test_template, auth_context):
    """Test OAuth2 integration security"""
    await auth_test_template.test_oauth2_authorization_flow(auth_context)

@pytest.mark.asyncio
async def test_security_vulnerabilities(auth_test_template, auth_context):
    """Test security vulnerability prevention"""
    await auth_test_template.test_authentication_bypass_attempts(auth_context)

@pytest.mark.asyncio
@pytest.mark.performance
async def test_authentication_performance(auth_test_template, auth_context):
    """Test authentication performance under load"""
    await auth_test_template.test_authentication_performance(auth_context)

@pytest.mark.asyncio
@pytest.mark.integration
async def test_comprehensive_authentication_suite(auth_test_template):
    """Run comprehensive authentication test suite"""
    results = await auth_test_template.run_comprehensive_authentication_tests()
    assert results["security_score"] >= 90, f"Security score {results['security_score']}% below minimum 90%"


if __name__ == "__main__":
    """
    Run authentication tests directly
    Usage: python authentication_test_template.py
    """
    async def main():
        template = AuthenticationTestTemplate()
        results = await template.run_comprehensive_authentication_tests()
        
        print("\n" + "="*80)
        print("🔒 AUTHENTICATION SECURITY TEST RESULTS")
        print("="*80)
        print(f"Security Score: {results['security_score']:.1f}%")
        print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
        
        if results['failed_tests'] > 0:
            print("\n❌ Failed Tests:")
            for test in results['test_details']:
                if test['status'] == 'FAILED':
                    print(f"  - {test['name']}: {test['error']}")
        
        return results['security_score'] >= 90
    
    # Run the tests
    import asyncio
    success = asyncio.run(main())
    exit(0 if success else 1)