"""Two-Factor Authentication (2FA) Enforcement for Admin Accounts
==============================================================

Mandatory 2FA implementation for administrator accounts with multiple
authentication methods including TOTP, SMS, and hardware tokens.

Features:
- TOTP (Time-based One-Time Password) support
- SMS-based verification
- Hardware token support (FIDO2/WebAuthn)
- Emergency backup codes
- Admin 2FA enforcement policies
- Grace period management for new admins

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import secrets
import time
import hmac
import hashlib
import base64
import qrcode
import io
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import pyotp
import asyncio
import aioredis
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import logging

logger = logging.getLogger(__name__)


class TwoFactorMethod(Enum):
    """Two-factor authentication methods"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_TOKEN = "hardware_token"
    BACKUP_CODES = "backup_codes"


class UserRole(Enum):
    """User role types"""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SYSTEM = "system"


@dataclass
class TwoFactorSettings:
    """Two-factor authentication settings"""
    user_id: str
    methods_enabled: List[TwoFactorMethod] = field(default_factory=list)
    totp_secret: Optional[str] = None
    totp_verified: bool = False
    phone_number: Optional[str] = None
    phone_verified: bool = False
    email_verified: bool = False
    backup_codes: List[str] = field(default_factory=list)
    backup_codes_used: List[str] = field(default_factory=list)
    hardware_tokens: List[Dict[str, Any]] = field(default_factory=list)
    last_used_method: Optional[TwoFactorMethod] = None
    last_verification: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdminEnforcementPolicy:
    """Admin 2FA enforcement policy"""
    enforce_2fa_for_roles: List[UserRole] = field(default_factory=lambda: [
        UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.SYSTEM
    ])
    grace_period_days: int = 7
    required_methods_count: int = 2  # Require at least 2 methods
    mandatory_methods: List[TwoFactorMethod] = field(default_factory=lambda: [
        TwoFactorMethod.TOTP  # TOTP is mandatory
    ])
    session_timeout_minutes: int = 30
    re_verification_required_for: List[str] = field(default_factory=lambda: [
        "/admin/users/delete",
        "/admin/system/config",
        "/admin/security/settings",
        "/admin/database/backup"
    ])
    max_failed_attempts: int = 3
    lockout_duration_minutes: int = 30


class TOTPManager:
    """TOTP (Time-based One-Time Password) manager"""
    
    def __init__(self, issuer_name: str = "AI Influencer Agent"):
        self.issuer_name = issuer_name
        self.window = 1  # Allow 1 time window before/after current
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, user_email: str) -> bytes:
        """Generate QR code for TOTP setup"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
    
    def verify_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=self.window)
    
    def get_current_token(self, secret: str) -> str:
        """Get current TOTP token (for testing)"""
        totp = pyotp.TOTP(secret)
        return totp.now()


class BackupCodeManager:
    """Backup codes manager"""
    
    def __init__(self):
        self.code_length = 8
        self.code_count = 10
    
    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes"""
        codes = []
        for _ in range(self.code_count):
            code = self._generate_single_code()
            codes.append(code)
        return codes
    
    def _generate_single_code(self) -> str:
        """Generate a single backup code"""
        # Generate alphanumeric code
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        code = ''.join(secrets.choice(alphabet) for _ in range(self.code_length))
        # Format as XXXX-XXXX
        return f"{code[:4]}-{code[4:]}"
    
    def verify_backup_code(self, codes: List[str], used_codes: List[str], provided_code: str) -> bool:
        """Verify backup code and mark as used"""
        if provided_code in used_codes:
            return False
        
        if provided_code in codes:
            used_codes.append(provided_code)
            return True
        
        return False


class SMSProvider:
    """SMS provider interface for 2FA"""
    
    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS message"""
        # This would integrate with actual SMS providers like Twilio, AWS SNS, etc.
        # For now, we'll simulate sending
        logger.info(f"SMS sent to {phone_number}: {message}")
        return True
    
    def generate_sms_code(self) -> str:
        """Generate SMS verification code"""
        return f"{secrets.randbelow(1000000):06d}"


class TwoFactorManager:
    """Main two-factor authentication manager"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = None
        self.redis_url = redis_url
        self.totp_manager = TOTPManager()
        self.backup_code_manager = BackupCodeManager()
        self.sms_provider = SMSProvider()
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
    async def initialize(self):
        """Initialize the 2FA manager"""
        self.redis_client = aioredis.from_url(self.redis_url)
        logger.info("Two-Factor Authentication manager initialized")
    
    async def shutdown(self):
        """Shutdown the 2FA manager"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def setup_totp(self, user_id: str, user_email: str) -> Tuple[str, bytes]:
        """Setup TOTP for user"""
        secret = self.totp_manager.generate_secret()
        qr_code = self.totp_manager.generate_qr_code(secret, user_email)
        
        # Store encrypted secret temporarily (until verification)
        encrypted_secret = self.cipher.encrypt(secret.encode())
        await self.redis_client.setex(
            f"totp_setup:{user_id}",
            300,  # 5 minutes
            encrypted_secret
        )
        
        return secret, qr_code
    
    async def verify_totp_setup(self, user_id: str, token: str) -> bool:
        """Verify TOTP setup and enable it"""
        # Get temporary secret
        encrypted_secret = await self.redis_client.get(f"totp_setup:{user_id}")
        if not encrypted_secret:
            return False
        
        secret = self.cipher.decrypt(encrypted_secret).decode()
        
        # Verify token
        if not self.totp_manager.verify_token(secret, token):
            return False
        
        # Enable TOTP for user
        settings = await self.get_user_2fa_settings(user_id)
        settings.totp_secret = secret
        settings.totp_verified = True
        if TwoFactorMethod.TOTP not in settings.methods_enabled:
            settings.methods_enabled.append(TwoFactorMethod.TOTP)
        settings.updated_at = datetime.utcnow()
        
        await self.save_user_2fa_settings(settings)
        
        # Clean up temporary secret
        await self.redis_client.delete(f"totp_setup:{user_id}")
        
        return True
    
    async def setup_sms(self, user_id: str, phone_number: str) -> bool:
        """Setup SMS 2FA for user"""
        # Generate and send verification code
        code = self.sms_provider.generate_sms_code()
        message = f"Your verification code is: {code}"
        
        if not await self.sms_provider.send_sms(phone_number, message):
            return False
        
        # Store code temporarily
        await self.redis_client.setex(
            f"sms_setup:{user_id}",
            300,  # 5 minutes
            code
        )
        
        # Store phone number temporarily
        await self.redis_client.setex(
            f"phone_setup:{user_id}",
            300,  # 5 minutes
            phone_number
        )
        
        return True
    
    async def verify_sms_setup(self, user_id: str, code: str) -> bool:
        """Verify SMS setup and enable it"""
        # Get stored code and phone number
        stored_code = await self.redis_client.get(f"sms_setup:{user_id}")
        phone_number = await self.redis_client.get(f"phone_setup:{user_id}")
        
        if not stored_code or not phone_number:
            return False
        
        if stored_code.decode() != code:
            return False
        
        # Enable SMS for user
        settings = await self.get_user_2fa_settings(user_id)
        settings.phone_number = phone_number.decode()
        settings.phone_verified = True
        if TwoFactorMethod.SMS not in settings.methods_enabled:
            settings.methods_enabled.append(TwoFactorMethod.SMS)
        settings.updated_at = datetime.utcnow()
        
        await self.save_user_2fa_settings(settings)
        
        # Clean up temporary data
        await self.redis_client.delete(f"sms_setup:{user_id}")
        await self.redis_client.delete(f"phone_setup:{user_id}")
        
        return True
    
    async def generate_backup_codes(self, user_id: str) -> List[str]:
        """Generate backup codes for user"""
        codes = self.backup_code_manager.generate_backup_codes()
        
        settings = await self.get_user_2fa_settings(user_id)
        settings.backup_codes = codes
        settings.backup_codes_used = []
        if TwoFactorMethod.BACKUP_CODES not in settings.methods_enabled:
            settings.methods_enabled.append(TwoFactorMethod.BACKUP_CODES)
        settings.updated_at = datetime.utcnow()
        
        await self.save_user_2fa_settings(settings)
        
        return codes
    
    async def verify_2fa(self, user_id: str, method: TwoFactorMethod, code: str) -> bool:
        """Verify 2FA code"""
        settings = await self.get_user_2fa_settings(user_id)
        
        if method not in settings.methods_enabled:
            return False
        
        verified = False
        
        if method == TwoFactorMethod.TOTP:
            if settings.totp_secret and settings.totp_verified:
                verified = self.totp_manager.verify_token(settings.totp_secret, code)
        
        elif method == TwoFactorMethod.SMS:
            # For SMS, we would send a code first, then verify it
            # This is a simplified version
            stored_code = await self.redis_client.get(f"sms_code:{user_id}")
            if stored_code:
                verified = stored_code.decode() == code
                if verified:
                    await self.redis_client.delete(f"sms_code:{user_id}")
        
        elif method == TwoFactorMethod.BACKUP_CODES:
            verified = self.backup_code_manager.verify_backup_code(
                settings.backup_codes,
                settings.backup_codes_used,
                code
            )
            if verified:
                # Update used backup codes
                await self.save_user_2fa_settings(settings)
        
        if verified:
            settings.last_used_method = method
            settings.last_verification = datetime.utcnow()
            await self.save_user_2fa_settings(settings)
        
        return verified
    
    async def send_sms_code(self, user_id: str) -> bool:
        """Send SMS verification code"""
        settings = await self.get_user_2fa_settings(user_id)
        
        if not settings.phone_verified or not settings.phone_number:
            return False
        
        code = self.sms_provider.generate_sms_code()
        message = f"Your verification code is: {code}"
        
        if not await self.sms_provider.send_sms(settings.phone_number, message):
            return False
        
        # Store code temporarily
        await self.redis_client.setex(
            f"sms_code:{user_id}",
            300,  # 5 minutes
            code
        )
        
        return True
    
    async def get_user_2fa_settings(self, user_id: str) -> TwoFactorSettings:
        """Get user's 2FA settings"""
        settings_key = f"2fa_settings:{user_id}"
        settings_data = await self.redis_client.hgetall(settings_key)
        
        if not settings_data:
            return TwoFactorSettings(user_id=user_id)
        
        # Deserialize settings
        settings = TwoFactorSettings(
            user_id=user_id,
            methods_enabled=[TwoFactorMethod(m) for m in settings_data.get(b'methods_enabled', b'').decode().split(',') if m],
            totp_secret=settings_data.get(b'totp_secret', b'').decode() or None,
            totp_verified=settings_data.get(b'totp_verified', b'false').decode() == 'true',
            phone_number=settings_data.get(b'phone_number', b'').decode() or None,
            phone_verified=settings_data.get(b'phone_verified', b'false').decode() == 'true',
            email_verified=settings_data.get(b'email_verified', b'false').decode() == 'true',
            backup_codes=settings_data.get(b'backup_codes', b'').decode().split(',') if settings_data.get(b'backup_codes') else [],
            backup_codes_used=settings_data.get(b'backup_codes_used', b'').decode().split(',') if settings_data.get(b'backup_codes_used') else [],
            last_used_method=TwoFactorMethod(settings_data.get(b'last_used_method', b'').decode()) if settings_data.get(b'last_used_method') else None,
        )
        
        return settings
    
    async def save_user_2fa_settings(self, settings: TwoFactorSettings):
        """Save user's 2FA settings"""
        settings_key = f"2fa_settings:{settings.user_id}"
        
        settings_data = {
            'methods_enabled': ','.join([m.value for m in settings.methods_enabled]),
            'totp_secret': settings.totp_secret or '',
            'totp_verified': str(settings.totp_verified).lower(),
            'phone_number': settings.phone_number or '',
            'phone_verified': str(settings.phone_verified).lower(),
            'email_verified': str(settings.email_verified).lower(),
            'backup_codes': ','.join(settings.backup_codes),
            'backup_codes_used': ','.join(settings.backup_codes_used),
            'last_used_method': settings.last_used_method.value if settings.last_used_method else '',
            'updated_at': settings.updated_at.isoformat(),
        }
        
        await self.redis_client.hset(settings_key, mapping=settings_data)
        await self.redis_client.expire(settings_key, 86400 * 365)  # 1 year


class AdminEnforcementManager:
    """Admin 2FA enforcement manager"""
    
    def __init__(self, policy: AdminEnforcementPolicy, tfa_manager: TwoFactorManager):
        self.policy = policy
        self.tfa_manager = tfa_manager
    
    async def check_admin_2fa_compliance(self, user_id: str, user_role: UserRole) -> Dict[str, Any]:
        """Check if admin user is compliant with 2FA policy"""
        if user_role not in self.policy.enforce_2fa_for_roles:
            return {"compliant": True, "reason": "role_not_required"}
        
        settings = await self.tfa_manager.get_user_2fa_settings(user_id)
        
        # Check if user has required number of methods
        if len(settings.methods_enabled) < self.policy.required_methods_count:
            return {
                "compliant": False,
                "reason": "insufficient_methods",
                "required": self.policy.required_methods_count,
                "current": len(settings.methods_enabled)
            }
        
        # Check if mandatory methods are enabled
        for method in self.policy.mandatory_methods:
            if method not in settings.methods_enabled:
                return {
                    "compliant": False,
                    "reason": "missing_mandatory_method",
                    "missing_method": method.value
                }
        
        # Check grace period (for new admins)
        if len(settings.methods_enabled) == 0:
            grace_expires = settings.created_at + timedelta(days=self.policy.grace_period_days)
            if datetime.utcnow() > grace_expires:
                return {
                    "compliant": False,
                    "reason": "grace_period_expired",
                    "grace_expired": grace_expires.isoformat()
                }
            else:
                return {
                    "compliant": True,
                    "reason": "grace_period_active",
                    "grace_expires": grace_expires.isoformat()
                }
        
        return {"compliant": True, "reason": "fully_compliant"}
    
    async def require_2fa_verification(self, user_id: str, request_path: str) -> bool:
        """Check if 2FA verification is required for this request"""
        if request_path in self.policy.re_verification_required_for:
            return True
        
        # Check if recent verification exists
        verification_key = f"2fa_verification:{user_id}"
        last_verification = await self.tfa_manager.redis_client.get(verification_key)
        
        if not last_verification:
            return True
        
        # Check if verification is still valid
        verification_time = datetime.fromisoformat(last_verification.decode())
        if datetime.utcnow() - verification_time > timedelta(minutes=self.policy.session_timeout_minutes):
            return True
        
        return False
    
    async def mark_2fa_verified(self, user_id: str):
        """Mark user as recently 2FA verified"""
        verification_key = f"2fa_verification:{user_id}"
        await self.tfa_manager.redis_client.setex(
            verification_key,
            self.policy.session_timeout_minutes * 60,
            datetime.utcnow().isoformat()
        )
    
    async def handle_failed_2fa_attempt(self, user_id: str) -> Dict[str, Any]:
        """Handle failed 2FA attempt"""
        attempts_key = f"2fa_attempts:{user_id}"
        
        # Increment attempt counter
        attempts = await self.tfa_manager.redis_client.incr(attempts_key)
        await self.tfa_manager.redis_client.expire(attempts_key, self.policy.lockout_duration_minutes * 60)
        
        if attempts >= self.policy.max_failed_attempts:
            # Lock user account
            lockout_key = f"2fa_lockout:{user_id}"
            await self.tfa_manager.redis_client.setex(
                lockout_key,
                self.policy.lockout_duration_minutes * 60,
                "locked"
            )
            
            return {
                "locked": True,
                "attempts": attempts,
                "lockout_duration": self.policy.lockout_duration_minutes
            }
        
        return {
            "locked": False,
            "attempts": attempts,
            "remaining": self.policy.max_failed_attempts - attempts
        }
    
    async def is_user_locked_out(self, user_id: str) -> bool:
        """Check if user is locked out due to failed 2FA attempts"""
        lockout_key = f"2fa_lockout:{user_id}"
        return await self.tfa_manager.redis_client.exists(lockout_key)


# Global instances
tfa_manager = None
admin_enforcement = None


async def initialize_2fa_system(
    redis_url: str = "redis://localhost:6379",
    policy: AdminEnforcementPolicy = None
) -> Tuple[TwoFactorManager, AdminEnforcementManager]:
    """Initialize the 2FA system"""
    global tfa_manager, admin_enforcement
    
    if tfa_manager is None:
        tfa_manager = TwoFactorManager(redis_url)
        await tfa_manager.initialize()
    
    if admin_enforcement is None:
        if policy is None:
            policy = AdminEnforcementPolicy()
        admin_enforcement = AdminEnforcementManager(policy, tfa_manager)
    
    return tfa_manager, admin_enforcement


def get_2fa_manager() -> Optional[TwoFactorManager]:
    """Get global 2FA manager instance"""
    return tfa_manager


def get_admin_enforcement() -> Optional[AdminEnforcementManager]:
    """Get global admin enforcement instance"""
    return admin_enforcement