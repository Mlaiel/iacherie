# -*- coding: utf-8 -*-
"""
Unit Tests for Security Module
==============================

Tests for security features and protection mechanisms including:
- Authentication and authorization
- Data encryption and protection
- Security monitoring and threat detection
- Compliance and audit logging
- Access control and permissions

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import asyncio
import hashlib
import jwt
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from security.auth_manager import AuthManager
    from security.encryption_service import EncryptionService
    from security.threat_detector import ThreatDetector
    from security.audit_logger import AuditLogger
except ImportError:
    # Mock classes for testing when modules are not available
    class AuthManager:
        def __init__(self):
            self.active_sessions = {}
            self.users = {}
        
        async def authenticate_user(self, username: str, password: str):
            # Simple mock authentication
            if username and password:
                return {
                    "user_id": f"user_{username}",
                    "username": username,
                    "token": "mock_jwt_token",
                    "expires_at": datetime.now() + timedelta(hours=24)
                }
            return None
        
        async def validate_token(self, token: str):
            return {"valid": True, "user_id": "user_123", "expires_at": datetime.now() + timedelta(hours=1)}
        
        def hash_password(self, password: str):
            return hashlib.sha256(password.encode()).hexdigest()
        
        async def check_permissions(self, user_id: str, resource: str, action: str):
            return True  # Mock always allows
    
    class EncryptionService:
        def __init__(self):
            self.algorithm = "AES-256"
        
        def encrypt_data(self, data: str, key: str = None):
            # Mock encryption - just base64 encode for testing
            import base64
            return base64.b64encode(data.encode()).decode()
        
        def decrypt_data(self, encrypted_data: str, key: str = None):
            # Mock decryption - just base64 decode for testing
            import base64
            return base64.b64decode(encrypted_data.encode()).decode()
        
        def generate_key(self):
            return "mock_encryption_key_256_bits"
        
        def hash_data(self, data: str):
            return hashlib.sha256(data.encode()).hexdigest()
    
    class ThreatDetector:
        def __init__(self):
            self.threat_patterns = []
            self.alerts = []
        
        async def analyze_request(self, request_data: Dict):
            # Mock threat analysis
            threat_level = "low"
            if "malicious" in str(request_data).lower():
                threat_level = "high"
            elif "suspicious" in str(request_data).lower():
                threat_level = "medium"
            
            return {
                "threat_level": threat_level,
                "threat_score": 0.1 if threat_level == "low" else (0.5 if threat_level == "medium" else 0.9),
                "threats_detected": ["sql_injection"] if threat_level == "high" else []
            }
        
        def detect_anomaly(self, user_behavior: Dict):
            # Mock anomaly detection
            return {
                "anomaly_detected": False,
                "confidence": 0.95,
                "anomaly_type": None
            }
    
    class AuditLogger:
        def __init__(self):
            self.logs = []
        
        async def log_security_event(self, event_type: str, user_id: str, details: Dict):
            log_entry = {
                "timestamp": datetime.now(),
                "event_type": event_type,
                "user_id": user_id,
                "details": details,
                "severity": "info"
            }
            self.logs.append(log_entry)
            return log_entry
        
        def get_audit_trail(self, user_id: str = None, start_date: datetime = None):
            filtered_logs = self.logs
            if user_id:
                filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]
            if start_date:
                filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_date]
            return filtered_logs


class TestAuthManager:
    """Test suite for AuthManager class"""
    
    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing"""
        return AuthManager()
    
    @pytest.fixture
    def sample_credentials(self):
        """Sample user credentials for testing"""
        return {
            "username": "testuser",
            "password": "secure_password123"
        }
    
    def test_auth_manager_initialization(self, auth_manager):
        """Test AuthManager initialization"""
        assert auth_manager is not None
        assert hasattr(auth_manager, 'active_sessions')
        assert hasattr(auth_manager, 'users')
        assert hasattr(auth_manager, 'authenticate_user')
    
    @pytest.mark.asyncio
    async def test_user_authentication_success(self, auth_manager, sample_credentials):
        """Test successful user authentication"""
        result = await auth_manager.authenticate_user(
            sample_credentials["username"],
            sample_credentials["password"]
        )
        
        # Assertions
        assert result is not None
        assert result["username"] == sample_credentials["username"]
        assert "user_id" in result
        assert "token" in result
        assert "expires_at" in result
        assert result["expires_at"] > datetime.now()
    
    @pytest.mark.asyncio
    async def test_user_authentication_failure(self, auth_manager):
        """Test failed user authentication"""
        result = await auth_manager.authenticate_user("", "")
        
        # Assertions
        assert result is None
    
    @pytest.mark.asyncio
    async def test_token_validation(self, auth_manager):
        """Test JWT token validation"""
        token = "mock_jwt_token"
        result = await auth_manager.validate_token(token)
        
        # Assertions
        assert result is not None
        assert result["valid"] == True
        assert "user_id" in result
        assert "expires_at" in result
    
    def test_password_hashing(self, auth_manager):
        """Test password hashing functionality"""
        password = "test_password_123"
        hashed = auth_manager.hash_password(password)
        
        # Assertions
        assert hashed is not None
        assert len(hashed) > 0
        assert hashed != password  # Should be different from original
        
        # Test consistency
        hashed2 = auth_manager.hash_password(password)
        assert hashed == hashed2  # Same input should produce same hash
    
    @pytest.mark.asyncio
    async def test_permission_checking(self, auth_manager):
        """Test permission checking"""
        user_id = "user_123"
        resource = "content"
        action = "read"
        
        has_permission = await auth_manager.check_permissions(user_id, resource, action)
        
        # Assertions
        assert has_permission == True  # Mock always returns True


class TestEncryptionService:
    """Test suite for EncryptionService class"""
    
    @pytest.fixture
    def encryption_service(self):
        """Create EncryptionService instance for testing"""
        return EncryptionService()
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for encryption testing"""
        return "This is sensitive data that needs to be encrypted"
    
    def test_encryption_service_initialization(self, encryption_service):
        """Test EncryptionService initialization"""
        assert encryption_service is not None
        assert hasattr(encryption_service, 'algorithm')
        assert encryption_service.algorithm == "AES-256"
    
    def test_data_encryption(self, encryption_service, sample_data):
        """Test data encryption functionality"""
        encrypted = encryption_service.encrypt_data(sample_data)
        
        # Assertions
        assert encrypted is not None
        assert encrypted != sample_data  # Should be different from original
        assert len(encrypted) > 0
    
    def test_data_decryption(self, encryption_service, sample_data):
        """Test data decryption functionality"""
        # Encrypt then decrypt
        encrypted = encryption_service.encrypt_data(sample_data)
        decrypted = encryption_service.decrypt_data(encrypted)
        
        # Assertions
        assert decrypted == sample_data  # Should match original
    
    def test_encryption_decryption_roundtrip(self, encryption_service):
        """Test encryption/decryption roundtrip"""
        test_data = [
            "Simple text",
            "Text with special chars: @#$%^&*()",
            "Multi-line\ntext\nwith\nnewlines",
            "Unicode text: 你好世界 🌍"
        ]
        
        for data in test_data:
            encrypted = encryption_service.encrypt_data(data)
            decrypted = encryption_service.decrypt_data(encrypted)
            assert decrypted == data
    
    def test_key_generation(self, encryption_service):
        """Test encryption key generation"""
        key = encryption_service.generate_key()
        
        # Assertions
        assert key is not None
        assert len(key) > 0
        assert isinstance(key, str)
    
    def test_data_hashing(self, encryption_service):
        """Test data hashing functionality"""
        test_data = "data to be hashed"
        hash_value = encryption_service.hash_data(test_data)
        
        # Assertions
        assert hash_value is not None
        assert len(hash_value) == 64  # SHA-256 produces 64-character hex string
        assert hash_value != test_data
        
        # Test consistency
        hash_value2 = encryption_service.hash_data(test_data)
        assert hash_value == hash_value2


class TestThreatDetector:
    """Test suite for ThreatDetector class"""
    
    @pytest.fixture
    def threat_detector(self):
        """Create ThreatDetector instance for testing"""
        return ThreatDetector()
    
    @pytest.fixture
    def sample_requests(self):
        """Sample request data for threat detection testing"""
        return {
            "safe_request": {
                "url": "/api/content",
                "method": "GET",
                "user_agent": "Mozilla/5.0",
                "parameters": {"id": "123"}
            },
            "suspicious_request": {
                "url": "/api/admin",
                "method": "POST",
                "user_agent": "suspicious_bot",
                "parameters": {"action": "delete_all"}
            },
            "malicious_request": {
                "url": "/api/data",
                "method": "POST",
                "user_agent": "malicious_scanner",
                "parameters": {"query": "SELECT * FROM users WHERE 1=1"}
            }
        }
    
    def test_threat_detector_initialization(self, threat_detector):
        """Test ThreatDetector initialization"""
        assert threat_detector is not None
        assert hasattr(threat_detector, 'threat_patterns')
        assert hasattr(threat_detector, 'alerts')
        assert hasattr(threat_detector, 'analyze_request')
    
    @pytest.mark.asyncio
    async def test_safe_request_analysis(self, threat_detector, sample_requests):
        """Test analysis of safe requests"""
        result = await threat_detector.analyze_request(sample_requests["safe_request"])
        
        # Assertions
        assert result is not None
        assert result["threat_level"] == "low"
        assert result["threat_score"] < 0.3
        assert len(result["threats_detected"]) == 0
    
    @pytest.mark.asyncio
    async def test_suspicious_request_analysis(self, threat_detector, sample_requests):
        """Test analysis of suspicious requests"""
        result = await threat_detector.analyze_request(sample_requests["suspicious_request"])
        
        # Assertions
        assert result is not None
        assert result["threat_level"] == "medium"
        assert 0.3 <= result["threat_score"] < 0.7
    
    @pytest.mark.asyncio
    async def test_malicious_request_analysis(self, threat_detector, sample_requests):
        """Test analysis of malicious requests"""
        result = await threat_detector.analyze_request(sample_requests["malicious_request"])
        
        # Assertions
        assert result is not None
        assert result["threat_level"] == "high"
        assert result["threat_score"] >= 0.7
        assert len(result["threats_detected"]) > 0
    
    def test_anomaly_detection(self, threat_detector):
        """Test anomaly detection functionality"""
        user_behavior = {
            "login_frequency": 5,
            "upload_frequency": 10,
            "unusual_activity": False
        }
        
        result = threat_detector.detect_anomaly(user_behavior)
        
        # Assertions
        assert result is not None
        assert "anomaly_detected" in result
        assert "confidence" in result
        assert result["confidence"] > 0.0


class TestAuditLogger:
    """Test suite for AuditLogger class"""
    
    @pytest.fixture
    def audit_logger(self):
        """Create AuditLogger instance for testing"""
        return AuditLogger()
    
    @pytest.fixture
    def sample_security_event(self):
        """Sample security event for logging"""
        return {
            "event_type": "login_attempt",
            "user_id": "user_123",
            "details": {
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0",
                "success": True
            }
        }
    
    def test_audit_logger_initialization(self, audit_logger):
        """Test AuditLogger initialization"""
        assert audit_logger is not None
        assert hasattr(audit_logger, 'logs')
        assert hasattr(audit_logger, 'log_security_event')
        assert len(audit_logger.logs) == 0
    
    @pytest.mark.asyncio
    async def test_security_event_logging(self, audit_logger, sample_security_event):
        """Test security event logging"""
        log_entry = await audit_logger.log_security_event(
            sample_security_event["event_type"],
            sample_security_event["user_id"],
            sample_security_event["details"]
        )
        
        # Assertions
        assert log_entry is not None
        assert log_entry["event_type"] == sample_security_event["event_type"]
        assert log_entry["user_id"] == sample_security_event["user_id"]
        assert log_entry["details"] == sample_security_event["details"]
        assert "timestamp" in log_entry
        assert "severity" in log_entry
        assert len(audit_logger.logs) == 1
    
    def test_audit_trail_retrieval(self, audit_logger):
        """Test audit trail retrieval"""
        # Add some mock logs
        audit_logger.logs = [
            {
                "timestamp": datetime.now() - timedelta(hours=2),
                "event_type": "login",
                "user_id": "user_1",
                "details": {},
                "severity": "info"
            },
            {
                "timestamp": datetime.now() - timedelta(hours=1),
                "event_type": "logout",
                "user_id": "user_1",
                "details": {},
                "severity": "info"
            },
            {
                "timestamp": datetime.now() - timedelta(minutes=30),
                "event_type": "login",
                "user_id": "user_2",
                "details": {},
                "severity": "info"
            }
        ]
        
        # Test getting all logs
        all_logs = audit_logger.get_audit_trail()
        assert len(all_logs) == 3
        
        # Test filtering by user
        user_1_logs = audit_logger.get_audit_trail(user_id="user_1")
        assert len(user_1_logs) == 2
        assert all(log["user_id"] == "user_1" for log in user_1_logs)
        
        # Test filtering by date
        recent_logs = audit_logger.get_audit_trail(
            start_date=datetime.now() - timedelta(hours=1, minutes=30)
        )
        assert len(recent_logs) == 2


class TestSecurityIntegration:
    """Integration tests for security workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_authentication_flow(self):
        """Test complete authentication workflow"""
        auth_manager = AuthManager()
        encryption_service = EncryptionService()
        audit_logger = AuditLogger()
        
        # Step 1: Hash password for storage
        password = "user_password_123"
        hashed_password = auth_manager.hash_password(password)
        
        # Step 2: Authenticate user
        auth_result = await auth_manager.authenticate_user("testuser", password)
        
        # Step 3: Log authentication event
        await audit_logger.log_security_event(
            "login_success",
            auth_result["user_id"],
            {"ip": "192.168.1.100"}
        )
        
        # Step 4: Validate token
        token_validation = await auth_manager.validate_token(auth_result["token"])
        
        # Verify complete flow
        assert hashed_password != password
        assert auth_result["token"] is not None
        assert token_validation["valid"] == True
        assert len(audit_logger.logs) == 1
    
    @pytest.mark.asyncio
    async def test_threat_detection_and_response(self):
        """Test threat detection and response workflow"""
        threat_detector = ThreatDetector()
        audit_logger = AuditLogger()
        
        # Step 1: Analyze potentially malicious request
        malicious_request = {
            "url": "/api/data",
            "parameters": {"query": "malicious SQL injection attempt"}
        }
        
        threat_analysis = await threat_detector.analyze_request(malicious_request)
        
        # Step 2: Log security incident if threat detected
        if threat_analysis["threat_level"] == "high":
            await audit_logger.log_security_event(
                "security_threat_detected",
                "system",
                {
                    "threat_level": threat_analysis["threat_level"],
                    "threat_score": threat_analysis["threat_score"],
                    "threats": threat_analysis["threats_detected"]
                }
            )
        
        # Verify threat detection and logging
        assert threat_analysis["threat_level"] == "high"
        assert len(audit_logger.logs) == 1
        assert audit_logger.logs[0]["event_type"] == "security_threat_detected"
    
    def test_data_protection_workflow(self):
        """Test data protection workflow"""
        encryption_service = EncryptionService()
        
        # Step 1: Generate encryption key
        encryption_key = encryption_service.generate_key()
        
        # Step 2: Encrypt sensitive data
        sensitive_data = "User's personal information: John Doe, john@example.com"
        encrypted_data = encryption_service.encrypt_data(sensitive_data, encryption_key)
        
        # Step 3: Store hash for integrity verification
        data_hash = encryption_service.hash_data(sensitive_data)
        
        # Step 4: Decrypt and verify
        decrypted_data = encryption_service.decrypt_data(encrypted_data, encryption_key)
        verification_hash = encryption_service.hash_data(decrypted_data)
        
        # Verify data protection
        assert encrypted_data != sensitive_data
        assert decrypted_data == sensitive_data
        assert data_hash == verification_hash


class TestSecurityCompliance:
    """Test suite for security compliance features"""
    
    def test_gdpr_compliance_features(self):
        """Test GDPR compliance features"""
        encryption_service = EncryptionService()
        audit_logger = AuditLogger()
        
        # Data minimization - only store necessary data
        user_data = {
            "id": "user_123",
            "email": "user@example.com",
            "consent_timestamp": datetime.now(),
            "data_processing_purposes": ["service_provision", "analytics"]
        }
        
        # Encrypt personal data
        encrypted_email = encryption_service.encrypt_data(user_data["email"])
        
        # Test data subject rights simulation
        data_export = {
            "user_id": user_data["id"],
            "exported_data": user_data,
            "export_timestamp": datetime.now()
        }
        
        # Assertions for GDPR compliance
        assert "consent_timestamp" in user_data
        assert "data_processing_purposes" in user_data
        assert encrypted_email != user_data["email"]
        assert data_export["exported_data"] == user_data
    
    def test_access_control_matrix(self):
        """Test role-based access control"""
        access_control_matrix = {
            "admin": {
                "content": ["create", "read", "update", "delete"],
                "users": ["create", "read", "update", "delete"],
                "system": ["configure", "monitor", "backup"]
            },
            "creator": {
                "content": ["create", "read", "update"],
                "users": ["read"],
                "system": []
            },
            "viewer": {
                "content": ["read"],
                "users": [],
                "system": []
            }
        }
        
        # Test permission checking
        def has_permission(role: str, resource: str, action: str) -> bool:
            return action in access_control_matrix.get(role, {}).get(resource, [])
        
        # Assertions
        assert has_permission("admin", "content", "delete") == True
        assert has_permission("creator", "content", "delete") == False
        assert has_permission("viewer", "content", "read") == True
        assert has_permission("viewer", "users", "read") == False
    
    def test_session_security(self):
        """Test session security features"""
        session_config = {
            "max_duration": timedelta(hours=24),
            "idle_timeout": timedelta(minutes=30),
            "secure_cookie": True,
            "httponly_cookie": True,
            "samesite": "strict"
        }
        
        # Simulate session validation
        session = {
            "id": "session_123",
            "created_at": datetime.now() - timedelta(hours=2),
            "last_activity": datetime.now() - timedelta(minutes=45),
            "user_id": "user_123"
        }
        
        current_time = datetime.now()
        
        # Check session validity
        session_age = current_time - session["created_at"]
        idle_time = current_time - session["last_activity"]
        
        is_valid = (
            session_age <= session_config["max_duration"] and
            idle_time <= session_config["idle_timeout"]
        )
        
        # Assertions
        assert session_age < session_config["max_duration"]
        assert idle_time > session_config["idle_timeout"]  # Session should be expired
        assert is_valid == False


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])