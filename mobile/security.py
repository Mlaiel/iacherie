"""Mobile Security Framework
Device authentication, biometric auth, and mobile-specific security

Author: Fahed Mlaiel <mlaiel@live.de>
Business Logic: Secure mobile access and content protection for creators
"""
import asyncio
import hashlib
import hmac
import base64
import secrets
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt

# Internal imports
try:
    from core.config import get_settings
    from core.logging import get_logger
    from core.security import generate_secure_token
except ImportError:
    # Fallback for standalone operation
    def get_logger(name: str):
        return logging.getLogger(name)
    
    def get_settings():
        return {"secret_key": "mobile_security_key"}
    
    def generate_secure_token():
        return secrets.token_urlsafe(32)


class SecurityLevel(Enum):
    """Mobile security levels."""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BiometricType(Enum):
    """Biometric authentication types."""    FINGERPRINT = "fingerprint"
    FACE_ID = "face_id"
    VOICE_PRINT = "voice_print"
    TOUCH_ID = "touch_id"


@dataclass
class DeviceSecurityProfile:
    """Mobile device security profile."""    device_id: str
    platform: str  # android, ios
    security_level: SecurityLevel
    biometric_enabled: bool
    device_fingerprint: str
    encryption_key: str
    last_security_check: datetime
    security_violations: int = 0
    is_jailbroken: bool = False
    is_rooted: bool = False
    security_patches_current: bool = True
    app_integrity_verified: bool = True
    
    def __post_init__(self):
        if isinstance(self.security_level, str):
            self.security_level = SecurityLevel(self.security_level)


@dataclass
class BiometricData:
    """Biometric authentication data."""    biometric_id: str
    user_id: str
    device_id: str
    biometric_type: BiometricType
    template_hash: str  # Hashed biometric template
    created_at: datetime
    last_used: datetime
    usage_count: int = 0
    is_active: bool = True
    
    def __post_init__(self):
        if isinstance(self.biometric_type, str):
            self.biometric_type = BiometricType(self.biometric_type)


@dataclass
class SecurityEvent:
    """Security event logging."""    event_id: str
    device_id: str
    user_id: Optional[str]
    event_type: str  # login_attempt, security_violation, biometric_auth, etc.
    severity: SecurityLevel
    description: str
    metadata: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    
    def __post_init__(self):
        if isinstance(self.severity, str):
            self.severity = SecurityLevel(self.severity)


class MobileEncryptionManager:
    """Professional mobile encryption management."""    
    def __init__(self):
        self.logger = get_logger("mobile.encryption_manager")
        self.settings = get_settings()
    
    def generate_device_key(self, device_id: str, user_id: str) -> bytes:
        """Generate device-specific encryption key."""        
        # Combine device and user data for key derivation
        key_material = f"{device_id}:{user_id}:{self.settings.get('secret_key')}"
        
        # Use PBKDF2 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=device_id.encode()[:16].ljust(16, b'0'),
            iterations=100000,
        )
        
        key = kdf.derive(key_material.encode())
        
        self.logger.info(f"Device encryption key generated for {device_id}")
        
        return key
    
    def encrypt_mobile_data(self, data: Union[str, bytes], key: bytes) -> str:
        """Encrypt data for mobile storage."""        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Create Fernet cipher
        fernet = Fernet(base64.urlsafe_b64encode(key))
        
        # Encrypt data
        encrypted_data = fernet.encrypt(data)
        
        # Return base64 encoded string
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_mobile_data(self, encrypted_data: str, key: bytes) -> bytes:
        """Decrypt mobile data."""        
        # Decode from base64
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
        
        # Create Fernet cipher
        fernet = Fernet(base64.urlsafe_b64encode(key))
        
        # Decrypt data
        decrypted_data = fernet.decrypt(encrypted_bytes)
        
        return decrypted_data
    
    def generate_secure_hash(self, data: str, salt: Optional[str] = None) -> str:
        """Generate secure hash for mobile data."""        
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine data and salt
        hash_input = f"{data}:{salt}".encode('utf-8')
        
        # Generate SHA-256 hash
        hash_object = hashlib.sha256(hash_input)
        return f"{salt}:{hash_object.hexdigest()}"
    
    def verify_secure_hash(self, data: str, stored_hash: str) -> bool:
        """Verify secure hash."""        
        try:
            salt, expected_hash = stored_hash.split(':', 1)
            computed_hash = self.generate_secure_hash(data, salt)
            return hmac.compare_digest(computed_hash, stored_hash)
        except ValueError:
            return False


class BiometricAuthManager:
    """Professional biometric authentication management."""    
    def __init__(self, encryption_manager: MobileEncryptionManager):
        self.logger = get_logger("mobile.biometric_auth")
        self.encryption_manager = encryption_manager
        self.biometric_data: Dict[str, BiometricData] = {}
    
    async def register_biometric(
        self,
        user_id: str,
        device_id: str,
        biometric_type: BiometricType,
        biometric_template: str  # Raw biometric data (should be hashed immediately)
    ) -> BiometricData:
        """Register biometric authentication."""        
        # Hash the biometric template immediately for security
        template_hash = self.encryption_manager.generate_secure_hash(biometric_template)
        
        biometric_id = str(uuid.uuid4())
        
        biometric_data = BiometricData(
            biometric_id=biometric_id,
            user_id=user_id,
            device_id=device_id,
            biometric_type=biometric_type,
            template_hash=template_hash,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow()
        )
        
        self.biometric_data[biometric_id] = biometric_data
        
        self.logger.info(
            f"Biometric registered: {biometric_type.value} for user {user_id} on device {device_id}"
        )
        
        return biometric_data
    
    async def authenticate_biometric(
        self,
        device_id: str,
        biometric_type: BiometricType,
        biometric_template: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate using biometric data."""        
        # Find matching biometric data for device and type
        for biometric in self.biometric_data.values():
            if (biometric.device_id == device_id and 
                biometric.biometric_type == biometric_type and 
                biometric.is_active):
                
                # Verify biometric template
                if self.encryption_manager.verify_secure_hash(
                    biometric_template, biometric.template_hash
                ):
                    # Update usage statistics
                    biometric.last_used = datetime.utcnow()
                    biometric.usage_count += 1
                    
                    self.logger.info(
                        f"Biometric authentication successful: {biometric_type.value} for user {biometric.user_id}"
                    )
                    
                    return {
                        "success": True,
                        "user_id": biometric.user_id,
                        "biometric_id": biometric.biometric_id,
                        "biometric_type": biometric_type.value
                    }
        
        self.logger.warning(
            f"Biometric authentication failed: {biometric_type.value} for device {device_id}"
        )
        
        return None
    
    async def deactivate_biometric(self, biometric_id: str) -> bool:
        """Deactivate biometric authentication."""        
        if biometric_id in self.biometric_data:
            self.biometric_data[biometric_id].is_active = False
            self.logger.info(f"Biometric deactivated: {biometric_id}")
            return True
        
        return False
    
    async def get_user_biometrics(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all biometric registrations for user."""        
        user_biometrics = []
        
        for biometric in self.biometric_data.values():
            if biometric.user_id == user_id and biometric.is_active:
                user_biometrics.append({
                    "biometric_id": biometric.biometric_id,
                    "device_id": biometric.device_id,
                    "biometric_type": biometric.biometric_type.value,
                    "created_at": biometric.created_at.isoformat(),
                    "last_used": biometric.last_used.isoformat(),
                    "usage_count": biometric.usage_count
                })
        
        return user_biometrics


class DeviceIntegrityChecker:
    """Professional device integrity and security validation."""    
    def __init__(self):
        self.logger = get_logger("mobile.device_integrity")
        self.known_rooting_indicators = [
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su"
        ]
        self.known_jailbreak_indicators = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate",
            "/usr/sbin/sshd",
            "/etc/apt"
        ]
    
    async def check_device_integrity(
        self,
        device_id: str,
        platform: str,
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Comprehensive device integrity check."""        
        integrity_result = {
            "device_id": device_id,
            "platform": platform,
            "integrity_score": 1.0,
            "is_compromised": False,
            "security_issues": [],
            "recommendations": [],
            "check_timestamp": datetime.utcnow().isoformat()
        }
        
        # Platform-specific checks
        if platform.lower() == "android":
            android_result = await self._check_android_integrity(device_info)
            integrity_result.update(android_result)
        
        elif platform.lower() == "ios":
            ios_result = await self._check_ios_integrity(device_info)
            integrity_result.update(ios_result)
        
        # Check app integrity
        app_integrity = await self._check_app_integrity(device_info)
        integrity_result["app_integrity"] = app_integrity
        
        # Calculate overall security score
        if integrity_result["security_issues"]:
            integrity_result["integrity_score"] = max(
                0.0, 1.0 - (len(integrity_result["security_issues"]) * 0.2)
            )
        
        integrity_result["is_compromised"] = integrity_result["integrity_score"] < 0.7
        
        self.logger.info(
            f"Device integrity check completed for {device_id}: "
            f"score {integrity_result['integrity_score']:.2f}"
        )
        
        return integrity_result
    
    async def _check_android_integrity(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check Android-specific integrity."""        
        result = {
            "is_rooted": False,
            "bootloader_unlocked": False,
            "security_patch_level": "unknown"
        }
        
        # Simulate root detection
        if device_info.get("debug_enabled", False):
            result["is_rooted"] = True
            result["security_issues"] = ["Device appears to be rooted"]
            result["recommendations"] = ["Use non-rooted device for enhanced security"]
        
        # Check security patch level
        patch_level = device_info.get("security_patch_level")
        if patch_level:
            result["security_patch_level"] = patch_level
            # Check if patch is recent (within 6 months)
            # This would be a real check in production
        
        return result
    
    async def _check_ios_integrity(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check iOS-specific integrity."""        
        result = {
            "is_jailbroken": False,
            "ios_version": device_info.get("ios_version", "unknown")
        }
        
        # Simulate jailbreak detection
        if device_info.get("third_party_apps_installed", False):
            result["is_jailbroken"] = True
            result["security_issues"] = ["Device appears to be jailbroken"]
            result["recommendations"] = ["Use non-jailbroken device for enhanced security"]
        
        return result
    
    async def _check_app_integrity(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check application integrity."""        
        return {
            "signature_valid": True,  # Would check actual app signature
            "tampered": False,
            "debug_mode": device_info.get("debug_enabled", False),
            "app_version": device_info.get("app_version", "unknown")
        }


class MobileSecurityManager:
    """Comprehensive mobile security management system."""    
    def __init__(self):
        self.logger = get_logger("mobile.security_manager")
        self.encryption_manager = MobileEncryptionManager()
        self.biometric_manager = BiometricAuthManager(self.encryption_manager)
        self.integrity_checker = DeviceIntegrityChecker()
        self.security_profiles: Dict[str, DeviceSecurityProfile] = {}
        self.security_events: List[SecurityEvent] = []
    
    async def create_security_profile(
        self,
        device_id: str,
        platform: str,
        device_info: Dict[str, Any]
    ) -> DeviceSecurityProfile:
        """Create comprehensive security profile for device."""        
        # Check device integrity
        integrity_result = await self.integrity_checker.check_device_integrity(
            device_id, platform, device_info
        )
        
        # Determine security level based on integrity
        if integrity_result["is_compromised"]:
            security_level = SecurityLevel.LOW
        elif integrity_result["integrity_score"] > 0.9:
            security_level = SecurityLevel.HIGH
        else:
            security_level = SecurityLevel.MEDIUM
        
        # Generate device fingerprint
        device_fingerprint = self._generate_device_fingerprint(device_id, device_info)
        
        # Generate encryption key
        encryption_key = base64.urlsafe_b64encode(
            self.encryption_manager.generate_device_key(device_id, "system")
        ).decode('utf-8')
        
        profile = DeviceSecurityProfile(
            device_id=device_id,
            platform=platform,
            security_level=security_level,
            biometric_enabled=device_info.get("biometric_capable", False),
            device_fingerprint=device_fingerprint,
            encryption_key=encryption_key,
            last_security_check=datetime.utcnow(),
            is_jailbroken=integrity_result.get("is_jailbroken", False),
            is_rooted=integrity_result.get("is_rooted", False),
            security_patches_current=True,  # Would check actual patch status
            app_integrity_verified=integrity_result["app_integrity"]["signature_valid"]
        )
        
        self.security_profiles[device_id] = profile
        
        # Log security event
        await self._log_security_event(
            device_id, None, "profile_created", SecurityLevel.MEDIUM,
            f"Security profile created with level {security_level.value}",
            {"integrity_score": integrity_result["integrity_score"]}
        )
        
        self.logger.info(
            f"Security profile created for device {device_id}: {security_level.value}"
        )
        
        return profile
    
    async def validate_device_access(
        self,
        device_id: str,
        user_id: str,
        requested_operation: str
    ) -> Dict[str, Any]:
        """Validate device access for specific operation."""        
        if device_id not in self.security_profiles:
            return {
                "allowed": False,
                "reason": "Device not registered",
                "security_level": "unknown"
            }
        
        profile = self.security_profiles[device_id]
        
        # Check security level requirements
        operation_requirements = {
            "content_upload": SecurityLevel.MEDIUM,
            "payment_processing": SecurityLevel.HIGH,
            "collaboration_request": SecurityLevel.MEDIUM,
            "admin_access": SecurityLevel.CRITICAL
        }
        
        required_level = operation_requirements.get(requested_operation, SecurityLevel.LOW)
        
        # Validate security level
        if profile.security_level.value == "low" and required_level != SecurityLevel.LOW:
            await self._log_security_event(
                device_id, user_id, "access_denied", SecurityLevel.MEDIUM,
                f"Insufficient security level for {requested_operation}",
                {"required": required_level.value, "current": profile.security_level.value}
            )
            
            return {
                "allowed": False,
                "reason": f"Insufficient security level: {profile.security_level.value}",
                "required_level": required_level.value,
                "current_level": profile.security_level.value
            }
        
        # Check for security violations
        if profile.security_violations > 3:
            return {
                "allowed": False,
                "reason": "Too many security violations",
                "violations_count": profile.security_violations
            }
        
        # Check device integrity
        if profile.is_jailbroken or profile.is_rooted:
            if required_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                return {
                    "allowed": False,
                    "reason": "Compromised device not allowed for this operation",
                    "security_level": profile.security_level.value
                }
        
        return {
            "allowed": True,
            "security_level": profile.security_level.value,
            "device_fingerprint": profile.device_fingerprint
        }
    
    async def update_security_check(self, device_id: str) -> Dict[str, Any]:
        """Update security check for device."""        
        if device_id not in self.security_profiles:
            raise ValueError(f"Security profile not found for device {device_id}")
        
        profile = self.security_profiles[device_id]
        profile.last_security_check = datetime.utcnow()
        
        # In production, this would perform actual security checks
        # For now, simulate the check
        
        return {
            "device_id": device_id,
            "last_check": profile.last_security_check.isoformat(),
            "security_level": profile.security_level.value,
            "status": "security_check_completed"
        }
    
    def _generate_device_fingerprint(
        self,
        device_id: str,
        device_info: Dict[str, Any]
    ) -> str:
        """Generate unique device fingerprint."""        
        fingerprint_data = {
            "device_id": device_id,
            "platform": device_info.get("platform"),
            "model": device_info.get("model"),
            "os_version": device_info.get("os_version"),
            "screen_resolution": device_info.get("screen_resolution"),
            "hardware_id": device_info.get("hardware_id")
        }
        
        # Create stable hash from device characteristics
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        fingerprint_hash = hashlib.sha256(fingerprint_string.encode()).hexdigest()
        
        return fingerprint_hash
    
    async def _log_security_event(
        self,
        device_id: str,
        user_id: Optional[str],
        event_type: str,
        severity: SecurityLevel,
        description: str,
        metadata: Dict[str, Any]
    ):
        """Log security event."""        
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            device_id=device_id,
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description=description,
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        
        self.security_events.append(event)
        
        # Log based on severity
        if severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            self.logger.warning(f"Security event: {description} (Device: {device_id})")
        else:
            self.logger.info(f"Security event: {description} (Device: {device_id})")


# Security utility functions
def generate_mobile_token(payload: Dict[str, Any], expiry_hours: int = 1) -> str:
    """Generate mobile-specific JWT token."""    
    settings = get_settings()
    
    # Add mobile-specific claims
    mobile_payload = {
        **payload,
        "token_type": "mobile",
        "exp": datetime.utcnow() + timedelta(hours=expiry_hours),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        mobile_payload,
        settings.get("secret_key"),
        algorithm="HS256"
    )
    
    return token


def verify_mobile_token(token: str) -> Dict[str, Any]:
    """Verify mobile JWT token."""    
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.get("secret_key"),
            algorithms=["HS256"]
        )
        
        # Verify mobile token type
        if payload.get("token_type") != "mobile":
            raise ValueError("Invalid token type")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


# Dependency injection functions
def get_mobile_security_manager() -> MobileSecurityManager:
    """Get mobile security manager instance."""    return MobileSecurityManager()


def get_encryption_manager() -> MobileEncryptionManager:
    """Get encryption manager instance.""" 
    return MobileEncryptionManager()


def get_biometric_manager(
    encryption_manager: MobileEncryptionManager = None
) -> BiometricAuthManager:
    """Get biometric auth manager instance."""    if encryption_manager is None:
        encryption_manager = get_encryption_manager()
    return BiometricAuthManager(encryption_manager)


# Main execution for testing
if __name__ == "__main__":
    import asyncio
    
    async def test_mobile_security():
        """Test mobile security functionality."""        
        # Test security manager
        security_manager = get_mobile_security_manager()
        
        # Test device profile creation
        device_info = {
            "platform": "android",
            "model": "Galaxy S21",
            "os_version": "12.0",
            "biometric_capable": True,
            "debug_enabled": False
        }
        
        profile = await security_manager.create_security_profile(
            "device123", "android", device_info
        )
        
        print(f"Security profile created: {profile.security_level.value}")
        
        # Test access validation
        access_result = await security_manager.validate_device_access(
            "device123", "user456", "content_upload"
        )
        
        print(f"Access validation: {access_result}")
        
        # Test biometric authentication
        biometric_manager = get_biometric_manager()
        
        biometric_data = await biometric_manager.register_biometric(
            "user456", "device123", BiometricType.FINGERPRINT, "sample_fingerprint_data"
        )
        
        print(f"Biometric registered: {biometric_data.biometric_id}")
        
        auth_result = await biometric_manager.authenticate_biometric(
            "device123", BiometricType.FINGERPRINT, "sample_fingerprint_data"
        )
        
        print(f"Biometric auth result: {auth_result}")
    
    # Run tests
    asyncio.run(test_mobile_security())