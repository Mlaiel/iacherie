# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Security Integration Tests

Tests for security features including authentication, authorization,
rate limiting, data protection, and security headers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import aiohttp
import jwt
import json
import time
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import patch, MagicMock
import uuid
from cryptography.fernet import Fernet
import bcrypt

# Test configuration
TEST_BASE_URL = "http://localhost:8000"
TEST_JWT_SECRET = "test_jwt_secret_key_for_testing"
TEST_ENCRYPTION_KEY = Fernet.generate_key()


class SecurityTestClient:
    """Enhanced test client for security testing."""
    
    def __init__(self, base_url: str = TEST_BASE_URL):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[str] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            logger.info(f"Executing __aexit__")
            
            # Implementation for __aexit__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__aexit__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__aexit__ failed: {e}")
            raise
            await self.session.close()
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Register a new user."""
        response = await self.session.post(
            f"{self.base_url}/auth/register",
            json=user_data
        )
        
        if response.status not in [200, 201]:
        try:
            logger.info(f"Executing login")
            
            # Implementation for login
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"login completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"login failed: {e}")
            raise
            json=login_data
        )
        
        if response.status != 200:
            error_data = await response.text()
            raise Exception(f"Login failed: {error_data}")
        
        data = await response.json()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        self.user_id = data.get("user_id")
        
        return data
    
    def get_auth_headers(self, include_bearer: bool = True) -> Dict[str, str]:
        """Get authorization headers."""
        headers = {"Content-Type": "application/json"}
        if self.access_token and include_bearer:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif self.access_token and not include_bearer:
            headers["Authorization"] = self.access_token  # No Bearer prefix
        return headers
    
    async def make_authenticated_request(
        self, method: str, endpoint: str, **kwargs
    ) -> aiohttp.ClientResponse:
        """Make authenticated request."""
        headers = kwargs.pop("headers", {})
        headers.update(self.get_auth_headers())
        
        return await self.session.request(
            method, f"{self.base_url}{endpoint}", headers=headers, **kwargs
        )


@pytest.fixture
async def security_client():
        try:
            logger.info(f"Executing authenticated_user")
            
            # Implementation for authenticated_user
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"authenticated_user completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"authenticated_user failed: {e}")
        try:
            logger.info(f"Executing test_password_hashing_security")
            
            # Implementation for test_password_hashing_security
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_password_hashing_security completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_password_hashing_security failed: {e}")
            raise
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_password_hashing_security(self, security_client):
        """
Test that passwords are properly hashed and stored."""
        user_data = {
            "email": f"hash_test_{uuid.uuid4()}@example.com",
            "password": "test_password_123!",
            "first_name": "Hash",
            "last_name": "Test",
            "creator_type": "musician"
        }
        
        # Register user
        registration_result = await security_client.register_user(user_data)
        assert "user_id" in registration_result
        
        # Verify login works with correct password
        login_result = await security_client.login(
            user_data["email"], user_data["password"]
        )
        assert "access_token" in login_result
        
        # Verify login fails with incorrect password
        with pytest.raises(Exception):
        try:
            logger.info(f"Executing test_password_strength_requirements")
            
            # Implementation for test_password_strength_requirements
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_password_strength_requirements completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_password_strength_requirements failed: {e}")
        try:
            logger.info(f"Executing test_account_lockout_after_failed_attempts")
            
            # Implementation for test_account_lockout_after_failed_attempts
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_account_lockout_after_failed_attempts completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_account_lockout_after_failed_attempts failed: {e}")
            raise
            with pytest.raises(Exception):  # Should reject weak passwords
                await security_client.register_user(user_data)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_account_lockout_after_failed_attempts(self, security_client):
        """Test account lockout after multiple failed login attempts."""
        user_data = {
            "email": f"lockout_test_{uuid.uuid4()}@example.com",
            "password": "correct_password_123!",
            "first_name": "Lockout",
            "last_name": "Test",
            "creator_type": "musician"
        }
        
        # Register user
        await security_client.register_user(user_data)
        
        # Attempt multiple failed logins
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                await security_client.login(user_data["email"], "wrong_password")
            except Exception:
                pass  # Expected to fail
        
        # Account should now be locked
        with pytest.raises(Exception) as exc_info:
            await security_client.login(user_data["email"], user_data["password"])
        
        # Verify the error indicates account lockout
        assert "locked" in str(exc_info.value).lower() or "suspended" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_session_timeout(self, security_client, authenticated_user):
        """Test session timeout functionality."""
        # Make initial authenticated request
        response = await security_client.make_authenticated_request("GET", "/user/profile")
        assert response.status == 200
        
        # Simulate token expiration by using an expired token
        expired_payload = {
            "user_id": security_client.user_id,
            "exp": int(time.time()) - 3600,  # Expired 1 hour ago
            "iat": int(time.time()) - 7200   # Issued 2 hours ago
        }
        
        expired_token = jwt.encode(expired_payload, TEST_JWT_SECRET, algorithm="HS256")
        security_client.access_token = expired_token
        
        # Request should fail with expired token
        response = await security_client.make_authenticated_request("GET", "/user/profile")
        assert response.status == 401  # Unauthorized
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_token_refresh_security(self, security_client, authenticated_user):
        """Test token refresh mechanism security."""
        # Get initial tokens
        original_access_token = security_client.access_token
        original_refresh_token = security_client.refresh_token
        
        # Refresh tokens
        refresh_response = await security_client.session.post(
            f"{security_client.base_url}/auth/refresh",
            json={"refresh_token": original_refresh_token}
        )
        
        assert refresh_response.status == 200
        refresh_data = await refresh_response.json()
        
        assert "access_token" in refresh_data
        assert refresh_data["access_token"] != original_access_token  # New token
        
        # Old access token should be invalidated
        security_client.access_token = original_access_token
        response = await security_client.make_authenticated_request("GET", "/user/profile")
        assert response.status == 401
        
        # New token should work
        security_client.access_token = refresh_data["access_token"]
        response = await security_client.make_authenticated_request("GET", "/user/profile")
        assert response.status == 200


class TestAuthorizationSecurity:
        try:
            logger.info(f"Executing test_role_based_access_control")
            
            # Implementation for test_role_based_access_control
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_role_based_access_control completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_role_based_access_control failed: {e}")
            raise
            "email": f"regular_{uuid.uuid4()}@example.com",
        try:
            logger.info(f"Executing test_resource_ownership_authorization")
            
            # Implementation for test_resource_ownership_authorization
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_resource_ownership_authorization completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_resource_ownership_authorization failed: {e}")
            raise
        user2_data = {
            "email": f"user2_{uuid.uuid4()}@example.com",
            "password": "user2_password_123!",
            "first_name": "User",
            "last_name": "Two",
            "creator_type": "musician"
        }
        
        # Register and login as user1
        await security_client.register_user(user1_data)
        login_result = await security_client.login(user1_data["email"], user1_data["password"])
        user1_id = login_result.get("user_id")
        
        # Create content as user1
        content_data = {
            "title": "User1 Content",
            "description": "Content owned by user1",
            "content_type": "text"
        }
        
        content_response = await security_client.make_authenticated_request(
            "POST", "/content/create", json=content_data
        )
        
        if content_response.status == 201:
            content_result = await content_response.json()
            content_id = content_result.get("content_id")
            
            # Register and login as user2
            await security_client.register_user(user2_data)
            await security_client.login(user2_data["email"], user2_data["password"])
            
            # User2 should not access user1's content
            access_response = await security_client.make_authenticated_request(
                "GET", f"/content/{content_id}"
            )
            assert access_response.status == 403  # Forbidden
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_api_key_authorization(self, security_client, authenticated_user):
        """Test API key-based authorization."""
        # Generate API key
        api_key_response = await security_client.make_authenticated_request(
            "POST", "/auth/api-key/generate",
            json={"name": "Test API Key", "permissions": ["read", "write"]}
        )
        
        if api_key_response.status == 201:
            api_key_data = await api_key_response.json()
            api_key = api_key_data["api_key"]
            
            # Use API key for authentication
            headers = {"X-API-Key": api_key}
            api_response = await security_client.session.get(
                f"{security_client.base_url}/user/profile",
                headers=headers
            )
            
            assert api_response.status == 200
            
            # Invalid API key should fail
            headers = {"X-API-Key": "invalid_api_key"}
            invalid_response = await security_client.session.get(
                f"{security_client.base_url}/user/profile",
                headers=headers
            )
            
            assert invalid_response.status == 401


class TestRateLimitingSecurity:
    """Test rate limiting and DDoS protection."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_api_rate_limiting(self, security_client, authenticated_user):
        """
Test API rate limiting enforcement."""
        # Make rapid requests to trigger rate limiting
        responses = []
        request_count = 100
        
        for i in range(request_count):
            response = await security_client.make_authenticated_request("GET", "/user/profile")
            responses.append(response.status)
            
            # Small delay to avoid overwhelming the test
            if i % 10 == 0:
                await asyncio.sleep(0.1)
        
        # Should eventually hit rate limit
        rate_limited_responses = [status for status in responses if status == 429]
        assert len(rate_limited_responses) > 0, "Rate limiting should be triggered"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_login_rate_limiting(self, security_client):
        try:
            logger.info(f"Executing test_login_rate_limiting")
            
            # Implementation for test_login_rate_limiting
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_login_rate_limiting completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_login_rate_limiting failed: {e}")
            raise
            responses.append(login_response.status)
        
        # Should hit rate limit
        assert 429 in responses, "Login rate limiting should be enforced"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_per_user_rate_limiting(self, security_client):
        """Test per-user rate limiting."""
        # Create two users
        user1_data = {
            "email": f"user1_rate_{uuid.uuid4()}@example.com",
            "password": "password_123!",
            "first_name": "User1",
        try:
            logger.info(f"Executing test_per_user_rate_limiting")
            
            # Implementation for test_per_user_rate_limiting
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_per_user_rate_limiting completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_per_user_rate_limiting failed: {e}")
            raise
    @pytest.mark.integration
    @pytest.mark.security
    async def test_sensitive_data_encryption(self, security_client, authenticated_user):
        """
Test that sensitive data is encrypted in transit and at rest."""
        # Test payment information encryption
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": "12",
            "exp_year": "2025",
            "cvc": "123",
            "cardholder_name": "Test User"
        }
        
        # Payment data should be encrypted before storage
        payment_response = await security_client.make_authenticated_request(
            "POST", "/payments/methods/add",
            json=payment_data
        )
        
        if payment_response.status == 201:
            # Verify that raw card data is not returned
            payment_result = await payment_response.json()
            assert "card_number" not in payment_result or "*" in payment_result.get("card_number", "")
            assert "cvc" not in payment_result
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_pii_data_protection(self, security_client, authenticated_user):
        """Test protection of personally identifiable information (PII)."""
        # Update profile with sensitive information
        sensitive_data = {
            "ssn": "123-45-6789",
            "phone": "+1234567890",
            "address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345"
            }
        }
        
        profile_response = await security_client.make_authenticated_request(
            "PUT", "/user/profile/sensitive",
            json=sensitive_data
        )
        
        if profile_response.status == 200:
            # Retrieve profile and verify sensitive data is masked/encrypted
            get_response = await security_client.make_authenticated_request(
                "GET", "/user/profile"
            )
            
            assert get_response.status == 200
            profile_data = await get_response.json()
            
            # SSN should be masked
            if "ssn" in profile_data:
                assert "*" in profile_data["ssn"] or profile_data["ssn"] != "123-45-6789"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_content_encryption(self, security_client, authenticated_user):
        """Test content encryption for sensitive uploads."""
        # Upload sensitive content
        sensitive_content = {
            "title": "Confidential Content",
            "description": "This content should be encrypted",
            "content_type": "document",
            "sensitivity_level": "confidential",
            "encryption_required": True
        }
        
        content_response = await security_client.make_authenticated_request(
            "POST", "/content/upload/secure",
            json=sensitive_content
        )
        
        if content_response.status == 201:
            content_result = await content_response.json()
            
            # Content should have encryption metadata
            assert "encrypted" in content_result
            assert content_result["encrypted"] is True
            assert "encryption_key_id" in content_result


class TestInputValidationSecurity:
    """Test input validation and sanitization."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_sql_injection_prevention(self, security_client, authenticated_user):
        """
Test prevention of SQL injection attacks."""
        # Attempt SQL injection in various inputs
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in sql_injection_payloads:
            # Try injection in search endpoint
            search_response = await security_client.make_authenticated_request(
                "GET", "/search", params={"q": payload}
            )
            
            # Should not return error indicating SQL injection worked
            assert search_response.status in [200, 400, 422]  # Normal or validation error
            
            if search_response.status == 200:
                search_data = await search_response.json()
                # Should not contain database error messages
                search_text = json.dumps(search_data).lower()
                dangerous_keywords = ["syntax error", "mysql", "postgresql", "database error"]
                assert not any(keyword in search_text for keyword in dangerous_keywords)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_xss_prevention(self, security_client, authenticated_user):
        """Test prevention of Cross-Site Scripting (XSS) attacks."""
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            # Try XSS in profile update
            profile_data = {
                "bio": payload,
                "website": f"https://example.com/{payload}"
            }
            
            profile_response = await security_client.make_authenticated_request(
                "PUT", "/user/profile",
                json=profile_data
            )
            
            if profile_response.status == 200:
                # Retrieve profile and verify XSS is sanitized
                get_response = await security_client.make_authenticated_request(
                    "GET", "/user/profile"
                )
                
                profile_result = await get_response.json()
                
                # XSS should be escaped or removed
                if "bio" in profile_result:
                    assert "<script>" not in profile_result["bio"]
                    assert "javascript:" not in profile_result["bio"]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_file_upload_validation(self, security_client, authenticated_user):
        """Test file upload validation and security."""
        # Test malicious file uploads
        malicious_files = [
            ("malware.exe", b"MZ\x90\x00"),  # PE executable header
            ("script.php", b"<?php system($_GET['cmd']); ?>"),
            ("shell.jsp", b"<%@ page import=\"java.io.*\" %>"),
        ]
        
        for filename, content in malicious_files:
            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=filename, delete=False) as f:
                f.write(content)
                f.flush()
                
                # Attempt upload
                with open(f.name, 'rb') as upload_file:
                    data = aiohttp.FormData()
                    data.add_field('file', upload_file, filename=filename)
                    data.add_field('title', 'Test Upload')
                    data.add_field('content_type', 'document')
                    
                    upload_response = await security_client.session.post(
                        f"{security_client.base_url}/content/upload",
                        data=data,
                        headers={"Authorization": f"Bearer {security_client.access_token}"}
                    )
                
                # Malicious files should be rejected
                assert upload_response.status in [400, 422, 415]  # Bad request or unsupported
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_request_size_limits(self, security_client, authenticated_user):
        """Test request size limits to prevent DoS."""
        # Attempt large payload
        large_data = {
            "description": "x" * 1000000,  # 1MB description
            "metadata": {"large_field": "y" * 500000}
        }
        
        large_response = await security_client.make_authenticated_request(
            "POST", "/content/create",
            json=large_data
        )
        
        # Should reject oversized requests
        assert large_response.status in [413, 400, 422]  # Payload too large or validation error


class TestSecurityHeadersAndCORS:
    """Test security headers and CORS configuration."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_security_headers(self, security_client):
        """
Test that proper security headers are set."""
        response = await security_client.session.get(f"{security_client.base_url}/")
        
        # Check for important security headers
        headers = response.headers
        
        # Content Security Policy
        assert "Content-Security-Policy" in headers or "X-Content-Security-Policy" in headers
        
        # X-Frame-Options (clickjacking protection)
        assert "X-Frame-Options" in headers
        
        # X-Content-Type-Options (MIME sniffing protection)
        assert "X-Content-Type-Options" in headers
        
        # X-XSS-Protection
        assert "X-XSS-Protection" in headers
        
        # Strict-Transport-Security (if HTTPS)
        if response.url.scheme == "https":
            assert "Strict-Transport-Security" in headers
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_cors_configuration(self, security_client):
        """Test CORS configuration."""
        # Test preflight request
        preflight_response = await security_client.session.options(
            f"{security_client.base_url}/auth/login",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization"
            }
        )
        
        # Should handle preflight properly
        assert preflight_response.status in [200, 204]
        
        if preflight_response.status in [200, 204]:
            cors_headers = preflight_response.headers
            
            # Check CORS headers
            assert "Access-Control-Allow-Origin" in cors_headers
            assert "Access-Control-Allow-Methods" in cors_headers
            assert "Access-Control-Allow-Headers" in cors_headers
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_content_type_validation(self, security_client):
        """Test content type validation."""
        # Send request with wrong content type
        wrong_content_response = await security_client.session.post(
            f"{security_client.base_url}/auth/login",
            data="email=test@example.com&password=password",  # Form data instead of JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should reject or handle gracefully
        assert wrong_content_response.status in [400, 415, 422]


class TestAuditingAndLogging:
    """Test security auditing and logging."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.security
    async def test_security_event_logging(self, security_client):
        """
Test that security events are properly logged."""
        # Perform actions that should be logged
        user_data = {
            "email": f"audit_test_{uuid.uuid4()}@example.com",
            "password": "audit_password_123!",
            "first_name": "Audit",
            "last_name": "Test",
            "creator_type": "musician"
        }
        
        # Registration should be logged
        await security_client.register_user(user_data)
        
        # Login should be logged
        await security_client.login(user_data["email"], user_data["password"])
        
        # Failed login should be logged
        try:
        try:
            logger.info(f"Executing test_content_type_validation")
            
            # Implementation for test_content_type_validation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_content_type_validation completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing test_security_event_logging")
            
            # Implementation for test_security_event_logging
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_security_event_logging completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_security_event_logging failed: {e}")
            raise
            "new_password": "new_secure_password_456!"
        }
        
        password_response = await security_client.make_authenticated_request(
            "PUT", "/auth/password/change",
            json=password_change_data
        )
        
        # Even if password change fails, it shouldn't expose passwords in logs
        # This is more of a code review item, but we can at least verify
        # that the response doesn't contain the passwords
        if password_response.status in [200, 400, 422]:
            response_text = await password_response.text()
            assert "secure_password_123!" not in response_text
            assert "new_secure_password_456!" not in response_text


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--asyncio-mode=auto"])
        try:
            logger.info(f"Executing test_sensitive_data_not_logged")
            
            # Implementation for test_sensitive_data_not_logged
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_sensitive_data_not_logged completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_sensitive_data_not_logged failed: {e}")
            raise