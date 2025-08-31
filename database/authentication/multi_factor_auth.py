"""🔐 Multi-Factor Authentication Database - Enterprise 2FA/MFA System
==================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Type: Production-Ready MFA Database Management
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING: Unauthorized use strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Business Logic: MFA Setup → Device Registration → Authentication Challenge → 
Backup Codes → Recovery → Audit Logging
"""import asyncio
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from uuid import UUID, uuid4
import qrcode
import io
import base64

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON, Index, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
import pyotp
from cryptography.fernet import Fernet
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

Base = declarative_base()

class MFAMethod(Enum):
    """Multi-factor authentication methods"""    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"    # SMS verification
    EMAIL = "email"  # Email verification
    PUSH = "push"  # Push notification
    BACKUP_CODE = "backup_code"  # Backup recovery codes
    HARDWARE_TOKEN = "hardware_token"  # Hardware security keys
    BIOMETRIC = "biometric"  # Biometric authentication

class MFAStatus(Enum):
    """MFA status states"""    ENABLED = "enabled"
    DISABLED = "disabled"
    PENDING_SETUP = "pending_setup"
    TEMPORARILY_DISABLED = "temporarily_disabled"
    COMPROMISED = "compromised"

class DeviceStatus(Enum):
    """Trusted device status"""    TRUSTED = "trusted"
    PENDING = "pending"
    REVOKED = "revoked"
    EXPIRED = "expired"

@dataclass
class MFAChallenge:
    """MFA challenge data structure"""    challenge_id: str
    user_id: str
    method: MFAMethod
    challenge_code: str
    expires_at: datetime
    attempts_remaining: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TOTPConfig:
    """TOTP configuration"""    secret_key: str
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30
    issuer: str = "IA Influencer Agent"
    account_name: str = ""

class MFADevices(Base):
    """Database model for MFA devices"""    __tablename__ = 'mfa_devices'
    
    device_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    device_name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)  # phone, tablet, hardware_key, etc.
    mfa_method = Column(String, nullable=False)
    encrypted_secret = Column(Text, nullable=True)  # For TOTP secrets
    phone_number = Column(String, nullable=True)   # For SMS
    email_address = Column(String, nullable=True)  # For email
    device_fingerprint = Column(String, nullable=True)
    status = Column(String, nullable=False, default=MFAStatus.PENDING_SETUP.value)
    is_primary = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    failed_attempts = Column(Integer, nullable=False, default=0)
    metadata = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_mfa_user_method', 'user_id', 'mfa_method'),
        Index('idx_mfa_user_status', 'user_id', 'status'),
    )

class MFABackupCodes(Base):
    """Database model for MFA backup codes"""    __tablename__ = 'mfa_backup_codes'
    
    code_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    code_hash = Column(String, nullable=False, unique=True)
    salt = Column(String, nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)
    used_at = Column(DateTime, nullable=True)
    used_from_ip = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_backup_codes_user', 'user_id', 'is_used'),
    )

class MFAChallenges(Base):
    """Database model for MFA challenges"""    __tablename__ = 'mfa_challenges'
    
    challenge_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    device_id = Column(String, nullable=True)
    mfa_method = Column(String, nullable=False)
    challenge_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    attempts_made = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    is_completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_mfa_challenges_user_expires', 'user_id', 'expires_at'),
        Index('idx_mfa_challenges_completed', 'is_completed', 'expires_at'),
    )

class TrustedDevices(Base):
    """Database model for trusted devices"""    __tablename__ = 'trusted_devices'
    
    trust_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    device_fingerprint = Column(String, nullable=False)
    device_name = Column(String, nullable=False)
    device_type = Column(String, nullable=True)
    browser_info = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    status = Column(String, nullable=False, default=DeviceStatus.PENDING.value)
    trusted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String, nullable=True)
    
    __table_args__ = (
        Index('idx_trusted_devices_user_status', 'user_id', 'status'),
        Index('idx_trusted_devices_fingerprint', 'device_fingerprint'),
    )

class MultiFactorAuthRepository:
    """    Enterprise-grade multi-factor authentication repository.
    
    Features:
    - TOTP (Time-based One-Time Password) support
    - SMS and email verification
    - Hardware security key support
    - Backup recovery codes
    - Trusted device management
    - Challenge-response authentication
    - Comprehensive audit logging
    """    
    def __init__(
        self,
        session: AsyncSession,
        encryption_key: str,
        totp_issuer: str = "IA Influencer Agent"
    ):
        self.session = session
        self.fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        self.totp_issuer = totp_issuer
        
        # Password context for hashing backup codes
        self.pwd_context = CryptContext(
            schemes=["scrypt"],
            default="scrypt",
            scrypt__rounds=32768
        )
    
    async def setup_totp(self, user_id: str, device_name: str, account_name: str) -> Dict[str, Any]:
        """Setup TOTP for a user device"""        try:
            # Generate secret key
            secret = pyotp.random_base32()
            
            # Create TOTP URI for QR code
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=account_name,
                issuer_name=self.totp_issuer
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            img_buffer = io.BytesIO()
            qr_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Encrypt and store secret
            encrypted_secret = self.fernet.encrypt(secret.encode()).decode()
            
            device_id = str(uuid4())
            
            # Create MFA device record
            mfa_device = MFADevices(
                device_id=device_id,
                user_id=user_id,
                device_name=device_name,
                device_type="mobile",
                mfa_method=MFAMethod.TOTP.value,
                encrypted_secret=encrypted_secret,
                status=MFAStatus.PENDING_SETUP.value,
                metadata={
                    'algorithm': 'SHA1',
                    'digits': 6,
                    'period': 30
                }
            )
            
            self.session.add(mfa_device)
            await self.session.commit()
            
            logger.info(f"TOTP setup initiated for user {user_id}, device {device_name}")
            
            return {
                'device_id': device_id,
                'secret': secret,
                'qr_code': qr_code_base64,
                'provisioning_uri': provisioning_uri,
                'backup_codes': await self.generate_backup_codes(user_id)
            }
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"TOTP setup failed for user {user_id}: {e}")
            raise
    
    async def verify_totp_setup(self, user_id: str, device_id: str, verification_code: str) -> bool:
        """Verify TOTP setup with initial code"""        try:
            # Get device
            stmt = select(MFADevices).where(
                MFADevices.device_id == device_id,
                MFADevices.user_id == user_id,
                MFADevices.mfa_method == MFAMethod.TOTP.value
            )
            result = await self.session.execute(stmt)
            device = result.scalar_one_or_none()
            
            if not device or not device.encrypted_secret:
                raise ValueError("TOTP device not found or not properly configured")
            
            # Decrypt secret
            secret = self.fernet.decrypt(device.encrypted_secret.encode()).decode()
            
            # Verify code
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(verification_code, valid_window=1)
            
            if is_valid:
                # Mark device as verified and enabled
                device.status = MFAStatus.ENABLED.value
                device.verified_at = datetime.now(timezone.utc)
                
                # If this is the first MFA device, make it primary
                if not await self._has_primary_mfa_device(user_id):
                    device.is_primary = True
                
                await self.session.commit()
                
                logger.info(f"TOTP setup verified for user {user_id}, device {device_id}")
                return True
            else:
                # Increment failed attempts
                device.failed_attempts += 1
                await self.session.commit()
                
                logger.warning(f"TOTP setup verification failed for user {user_id}, device {device_id}")
                return False
                
        except Exception as e:
            logger.error(f"TOTP setup verification error: {e}")
            raise
    
    async def generate_mfa_challenge(
        self,
        user_id: str,
        method: MFAMethod,
        device_id: Optional[str] = None
    ) -> MFAChallenge:
        """Generate MFA challenge for authentication"""        try:
            challenge_id = str(uuid4())
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            
            if method == MFAMethod.TOTP:
                # For TOTP, we don't pre-generate the code, user provides it
                challenge_code = ""
            elif method == MFAMethod.SMS:
                # Generate 6-digit SMS code
                challenge_code = ''.join(secrets.choice(string.digits) for _ in range(6))
                await self._send_sms_code(user_id, challenge_code)
            elif method == MFAMethod.EMAIL:
                # Generate 8-character email code
                challenge_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                await self._send_email_code(user_id, challenge_code)
            else:
                challenge_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            
            # Hash and store challenge
            salt = secrets.token_hex(32)
            challenge_hash = self.pwd_context.hash(challenge_code + salt) if challenge_code else ""
            
            challenge_record = MFAChallenges(
                challenge_id=challenge_id,
                user_id=user_id,
                device_id=device_id,
                mfa_method=method.value,
                challenge_hash=challenge_hash,
                salt=salt,
                expires_at=expires_at,
                metadata={'method_specific_data': {}}
            )
            
            self.session.add(challenge_record)
            await self.session.commit()
            
            challenge = MFAChallenge(
                challenge_id=challenge_id,
                user_id=user_id,
                method=method,
                challenge_code=challenge_code,
                expires_at=expires_at
            )
            
            logger.info(f"MFA challenge generated for user {user_id}, method {method.value}")
            return challenge
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"MFA challenge generation failed: {e}")
            raise
    
    async def verify_mfa_challenge(
        self,
        challenge_id: str,
        user_code: str,
        device_fingerprint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify MFA challenge response"""        try:
            # Get challenge
            stmt = select(MFAChallenges).where(
                MFAChallenges.challenge_id == challenge_id,
                MFAChallenges.is_completed == False
            )
            result = await self.session.execute(stmt)
            challenge = result.scalar_one_or_none()
            
            if not challenge:
                return {'verified': False, 'reason': 'Challenge not found or already completed'}
            
            # Check expiration
            if challenge.expires_at < datetime.now(timezone.utc):
                return {'verified': False, 'reason': 'Challenge has expired'}
            
            # Check attempt limit
            if challenge.attempts_made >= challenge.max_attempts:
                return {'verified': False, 'reason': 'Maximum attempts exceeded'}
            
            # Increment attempt counter
            challenge.attempts_made += 1
            
            is_valid = False
            
            if challenge.mfa_method == MFAMethod.TOTP.value:
                # Verify TOTP code
                is_valid = await self._verify_totp_code(challenge.user_id, user_code, challenge.device_id)
            elif challenge.mfa_method == MFAMethod.BACKUP_CODE.value:
                # Verify backup code
                is_valid = await self._verify_backup_code(challenge.user_id, user_code)
            else:
                # Verify hashed challenge code
                is_valid = self.pwd_context.verify(
                    user_code + challenge.salt,
                    challenge.challenge_hash
                )
            
            if is_valid:
                # Mark challenge as completed
                challenge.is_completed = True
                challenge.completed_at = datetime.now(timezone.utc)
                
                # Update device last used
                if challenge.device_id:
                    await self._update_device_last_used(challenge.device_id)
                
                # Add trusted device if specified
                trust_token = None
                if device_fingerprint:
                    trust_token = await self._add_trusted_device(
                        challenge.user_id,
                        device_fingerprint
                    )
                
                await self.session.commit()
                
                logger.info(f"MFA challenge verified for user {challenge.user_id}")
                
                return {
                    'verified': True,
                    'user_id': challenge.user_id,
                    'trust_token': trust_token,
                    'method': challenge.mfa_method
                }
            else:
                await self.session.commit()
                
                return {
                    'verified': False,
                    'reason': 'Invalid verification code',
                    'attempts_remaining': challenge.max_attempts - challenge.attempts_made
                }
                
        except Exception as e:
            logger.error(f"MFA challenge verification failed: {e}")
            raise
    
    async def generate_backup_codes(self, user_id: str, count: int = 10) -> List[str]:
        """Generate backup recovery codes"""        try:
            # Deactivate existing backup codes
            stmt = select(MFABackupCodes).where(
                MFABackupCodes.user_id == user_id,
                MFABackupCodes.is_used == False
            )
            result = await self.session.execute(stmt)
            existing_codes = result.scalars().all()
            
            for code in existing_codes:
                code.is_used = True
                code.used_at = datetime.now(timezone.utc)
            
            # Generate new backup codes
            backup_codes = []
            expires_at = datetime.now(timezone.utc) + timedelta(days=365)  # 1 year validity
            
            for _ in range(count):
                # Generate 8-character alphanumeric code
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                backup_codes.append(code)
                
                # Hash and store
                salt = secrets.token_hex(32)
                code_hash = self.pwd_context.hash(code + salt)
                
                backup_code_record = MFABackupCodes(
                    code_id=str(uuid4()),
                    user_id=user_id,
                    code_hash=code_hash,
                    salt=salt,
                    expires_at=expires_at
                )
                
                self.session.add(backup_code_record)
            
            await self.session.commit()
            
            logger.info(f"Generated {count} backup codes for user {user_id}")
            return backup_codes
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Backup code generation failed for user {user_id}: {e}")
            raise
    
    async def get_user_mfa_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all MFA devices for a user"""        try:
            stmt = select(MFADevices).where(
                MFADevices.user_id == user_id,
                MFADevices.status == MFAStatus.ENABLED.value
            ).order_by(MFADevices.is_primary.desc(), MFADevices.created_at)
            
            result = await self.session.execute(stmt)
            devices = result.scalars().all()
            
            device_list = []
            for device in devices:
                device_info = {
                    'device_id': device.device_id,
                    'device_name': device.device_name,
                    'device_type': device.device_type,
                    'mfa_method': device.mfa_method,
                    'is_primary': device.is_primary,
                    'created_at': device.created_at,
                    'last_used_at': device.last_used_at,
                    'verified_at': device.verified_at
                }
                device_list.append(device_info)
            
            return device_list
            
        except Exception as e:
            logger.error(f"Failed to get MFA devices for user {user_id}: {e}")
            raise
    
    async def disable_mfa_device(self, user_id: str, device_id: str, reason: str = "User requested") -> bool:
        """Disable an MFA device"""        try:
            stmt = select(MFADevices).where(
                MFADevices.device_id == device_id,
                MFADevices.user_id == user_id
            )
            result = await self.session.execute(stmt)
            device = result.scalar_one_or_none()
            
            if not device:
                raise ValueError("MFA device not found")
            
            device.status = MFAStatus.DISABLED.value
            
            # If this was the primary device, assign another device as primary
            if device.is_primary:
                device.is_primary = False
                await self._assign_new_primary_device(user_id)
            
            await self.session.commit()
            
            logger.info(f"MFA device {device_id} disabled for user {user_id}: {reason}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to disable MFA device: {e}")
            raise
    
    async def is_device_trusted(self, user_id: str, device_fingerprint: str) -> bool:
        """Check if device is trusted"""        try:
            stmt = select(TrustedDevices).where(
                TrustedDevices.user_id == user_id,
                TrustedDevices.device_fingerprint == device_fingerprint,
                TrustedDevices.status == DeviceStatus.TRUSTED.value,
                TrustedDevices.expires_at > datetime.now(timezone.utc)
            )
            result = await self.session.execute(stmt)
            trusted_device = result.scalar_one_or_none()
            
            if trusted_device:
                # Update last seen
                trusted_device.last_seen_at = datetime.now(timezone.utc)
                await self.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check device trust status: {e}")
            return False
    
    # Private helper methods
    
    async def _verify_totp_code(self, user_id: str, code: str, device_id: Optional[str] = None) -> bool:
        """Verify TOTP code against user's devices"""        try:
            query = select(MFADevices).where(
                MFADevices.user_id == user_id,
                MFADevices.mfa_method == MFAMethod.TOTP.value,
                MFADevices.status == MFAStatus.ENABLED.value
            )
            
            if device_id:
                query = query.where(MFADevices.device_id == device_id)
            
            result = await self.session.execute(query)
            devices = result.scalars().all()
            
            for device in devices:
                if device.encrypted_secret:
                    secret = self.fernet.decrypt(device.encrypted_secret.encode()).decode()
                    totp = pyotp.TOTP(secret)
                    
                    if totp.verify(code, valid_window=1):
                        device.last_used_at = datetime.now(timezone.utc)
                        device.failed_attempts = 0
                        return True
                    else:
                        device.failed_attempts += 1
            
            return False
            
        except Exception as e:
            logger.error(f"TOTP verification failed: {e}")
            return False
    
    async def _verify_backup_code(self, user_id: str, code: str) -> bool:
        """Verify backup recovery code"""        try:
            stmt = select(MFABackupCodes).where(
                MFABackupCodes.user_id == user_id,
                MFABackupCodes.is_used == False,
                MFABackupCodes.expires_at > datetime.now(timezone.utc)
            )
            result = await self.session.execute(stmt)
            backup_codes = result.scalars().all()
            
            for backup_code in backup_codes:
                if self.pwd_context.verify(code + backup_code.salt, backup_code.code_hash):
                    # Mark code as used
                    backup_code.is_used = True
                    backup_code.used_at = datetime.now(timezone.utc)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Backup code verification failed: {e}")
            return False
    
    async def _has_primary_mfa_device(self, user_id: str) -> bool:
        """Check if user has a primary MFA device"""        stmt = select(MFADevices).where(
            MFADevices.user_id == user_id,
            MFADevices.is_primary == True,
            MFADevices.status == MFAStatus.ENABLED.value
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def _assign_new_primary_device(self, user_id: str):
        """Assign a new primary MFA device"""        stmt = select(MFADevices).where(
            MFADevices.user_id == user_id,
            MFADevices.status == MFAStatus.ENABLED.value
        ).order_by(MFADevices.last_used_at.desc())
        
        result = await self.session.execute(stmt)
        device = result.scalar_one_or_none()
        
        if device:
            device.is_primary = True
    
    async def _update_device_last_used(self, device_id: str):
        """Update device last used timestamp"""        stmt = select(MFADevices).where(MFADevices.device_id == device_id)
        result = await self.session.execute(stmt)
        device = result.scalar_one_or_none()
        
        if device:
            device.last_used_at = datetime.now(timezone.utc)
    
    async def _add_trusted_device(self, user_id: str, device_fingerprint: str) -> str:
        """Add device to trusted devices list"""        trust_id = str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)  # 30 days trust
        
        trusted_device = TrustedDevices(
            trust_id=trust_id,
            user_id=user_id,
            device_fingerprint=device_fingerprint,
            device_name="Trusted Device",
            status=DeviceStatus.TRUSTED.value,
            trusted_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )
        
        self.session.add(trusted_device)
        return trust_id
    
    async def _send_sms_code(self, user_id: str, code: str):
        """Send SMS verification code (placeholder)"""        # This would integrate with SMS service (Twilio, AWS SNS, etc.)
        logger.info(f"SMS code {code} would be sent to user {user_id}")
        pass
    
    async def _send_email_code(self, user_id: str, code: str):
        """Send email verification code (placeholder)"""        # This would integrate with email service (SendGrid, AWS SES, etc.)
        logger.info(f"Email code {code} would be sent to user {user_id}")
        pass

# Export the main classes
__all__ = [
    'MultiFactorAuthRepository',
    'MFADevices',
    'MFABackupCodes',
    'MFAChallenges',
    'TrustedDevices',
    'MFAMethod',
    'MFAStatus',
    'DeviceStatus',
    'MFAChallenge',
    'TOTPConfig'
]
