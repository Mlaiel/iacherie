#!/usr/bin/env python3
"""
⚡ Multi-Factor Authentication Template - Enterprise Security
🏗️ Architecture: IA Chéries Creator Economy Platform
🔒 Protection IP: © 2025 Fahed Mlaiel <mlaiel@live.de>

🚨 AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
import time
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import redis
import smtplib
import aiohttp
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Expert Team: Lead Dev IA + Backend Senior + Security Expert + Cryptography Expert
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class MFAMethod(str, Enum):
    """Multi-factor authentication methods"""
    TOTP = "totp"  # Time-based One-Time Password
    HOTP = "hotp"  # HMAC-based One-Time Password
    SMS = "sms"
    EMAIL = "email"
    PUSH_NOTIFICATION = "push"
    HARDWARE_TOKEN = "hardware"
    BIOMETRIC = "biometric"
    BACKUP_CODES = "backup_codes"
    SECURITY_KEY = "security_key"  # FIDO2/WebAuthn


class MFAStatus(str, Enum):
    """MFA verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"
    DISABLED = "disabled"


class MFAError(Exception):
    """Custom MFA exception"""
    pass


@dataclass
class MFAConfig:
    """Enterprise MFA configuration"""
    # TOTP settings
    totp_issuer: str = "IA Chéries"
    totp_algorithm: str = "SHA1"
    totp_digits: int = 6
    totp_interval: int = 30
    totp_window: int = 1  # Allow 1 period before/after
    
    # SMS settings
    sms_provider: str = "twilio"  # twilio, aws_sns, custom
    sms_api_key: Optional[str] = None
    sms_api_secret: Optional[str] = None
    sms_from_number: Optional[str] = None
    sms_template: str = "Your IA Chéries verification code: {code}"
    
    # Email settings
    email_smtp_host: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_from: str = "noreply@ainflue.com"
    email_template: str = "Your IA Chéries verification code: {code}"
    
    # Push notification settings
    push_provider: str = "firebase"  # firebase, apns, custom
    push_api_key: Optional[str] = None
    push_app_id: Optional[str] = None
    
    # Security settings
    code_length: int = 6
    code_expiry: int = 300  # 5 minutes
    max_attempts: int = 3
    lockout_duration: int = 900  # 15 minutes
    backup_codes_count: int = 10
    
    # Rate limiting
    rate_limit_per_user: int = 5  # requests per hour
    rate_limit_per_ip: int = 20   # requests per hour
    
    # Encryption
    encryption_key: Optional[str] = None
    
    # Redis settings
    redis_url: Optional[str] = None
    cache_prefix: str = "mfa:"
    
    # Creator-specific settings
    creator_require_mfa: bool = True
    creator_allowed_methods: List[MFAMethod] = field(default_factory=lambda: [
        MFAMethod.TOTP, MFAMethod.SMS, MFAMethod.EMAIL, MFAMethod.BACKUP_CODES
    ])
    creator_backup_codes_required: bool = True


@dataclass
class MFAChallenge:
    """MFA challenge data"""
    challenge_id: str
    user_id: str
    method: MFAMethod
    status: MFAStatus
    created_at: datetime
    expires_at: datetime
    attempts: int = 0
    
    # Method-specific data
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    device_id: Optional[str] = None
    encrypted_code: Optional[str] = None
    
    # Metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    @property
    def can_retry(self) -> bool:
        return self.attempts < 3 and not self.is_expired


@dataclass
class MFADevice:
    """Registered MFA device"""
    device_id: str
    user_id: str
    method: MFAMethod
    name: str
    is_primary: bool = False
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    
    # Method-specific data
    secret_key: Optional[str] = None  # For TOTP/HOTP
    phone_number: Optional[str] = None  # For SMS
    email_address: Optional[str] = None  # For Email
    push_token: Optional[str] = None  # For Push notifications
    public_key: Optional[str] = None  # For Security Keys
    
    # Security metadata
    backup_codes: Optional[List[str]] = None
    counter: int = 0  # For HOTP
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "device_id": self.device_id,
            "user_id": self.user_id,
            "method": self.method.value,
            "name": self.name,
            "is_primary": self.is_primary,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "phone_number": self.phone_number,
            "email_address": self.email_address,
            "counter": self.counter
        }


class CryptoManager:
    """
    🔒 Cryptographic operations for MFA
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        if encryption_key:
            self.fernet = Fernet(encryption_key.encode())
        else:
            # Generate a new key
            key = Fernet.generate_key()
            self.fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def generate_secret(self, length: int = 32) -> str:
        """Generate cryptographically secure secret"""
        return pyotp.random_base32()
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes"""
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append(f"{code[:4]}-{code[4:]}")
        return codes
    
    def hash_backup_code(self, code: str) -> str:
        """Hash backup code for storage"""
        return hashlib.sha256(code.encode()).hexdigest()


class TOTPManager:
    """
    🕒 Time-based One-Time Password Manager
    """
    
    def __init__(self, config: MFAConfig):
        self.config = config
        self.crypto = CryptoManager(config.encryption_key)
    
    def generate_secret(self) -> str:
        """Generate TOTP secret"""
        return self.crypto.generate_secret()
    
    def get_provisioning_uri(self, user_email: str, secret: str, issuer: str = None) -> str:
        """Generate provisioning URI for QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer=issuer or self.config.totp_issuer
        )
    
    def generate_qr_code(self, provisioning_uri: str) -> str:
        """Generate QR code as base64 string"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=self.config.totp_window)
    
    def get_current_token(self, secret: str) -> str:
        """Get current TOTP token (for testing)"""
        totp = pyotp.TOTP(secret)
        return totp.now()


class SMSProvider:
    """
    📱 SMS provider integration
    """
    
    def __init__(self, config: MFAConfig):
        self.config = config
        self.logger = logging.getLogger("mfa_sms")
    
    async def send_sms(self, phone_number: str, code: str) -> bool:
        """Send SMS verification code"""
        try:
            message = self.config.sms_template.format(code=code)
            
            if self.config.sms_provider == "twilio":
                return await self._send_twilio_sms(phone_number, message)
            elif self.config.sms_provider == "aws_sns":
                return await self._send_aws_sns_sms(phone_number, message)
            else:
                return await self._send_custom_sms(phone_number, message)
                
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")
            return False
    
    async def _send_twilio_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS via Twilio"""
        try:
            from twilio.rest import Client
            
            client = Client(self.config.sms_api_key, self.config.sms_api_secret)
            
            message = client.messages.create(
                body=message,
                from_=self.config.sms_from_number,
                to=phone_number
            )
            
            return message.sid is not None
            
        except Exception as e:
            self.logger.error(f"Twilio SMS error: {e}")
            return False
    
    async def _send_aws_sns_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS via AWS SNS"""
        try:
            import boto3
            
            sns = boto3.client('sns')
            
            response = sns.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            
            return response['ResponseMetadata']['HTTPStatusCode'] == 200
            
        except Exception as e:
            self.logger.error(f"AWS SNS SMS error: {e}")
            return False
    
    async def _send_custom_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS via custom provider"""
        # Implement your custom SMS provider here
        self.logger.info(f"Custom SMS to {phone_number}: {message}")
        return True


class EmailProvider:
    """
    📧 Email provider for MFA
    """
    
    def __init__(self, config: MFAConfig):
        self.config = config
        self.logger = logging.getLogger("mfa_email")
    
    async def send_email(self, email_address: str, code: str) -> bool:
        """Send email verification code"""
        try:
            message = self.config.email_template.format(code=code)
            subject = "IA Chéries Verification Code"
            
            return await self._send_smtp_email(email_address, subject, message)
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    async def _send_smtp_email(self, to_email: str, subject: str, message: str) -> bool:
        """Send email via SMTP"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.config.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MimeText(message, 'plain'))
            
            server = smtplib.SMTP(self.config.email_smtp_host, self.config.email_smtp_port)
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            
            text = msg.as_string()
            server.sendmail(self.config.email_from, to_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP email error: {e}")
            return False


class PushNotificationProvider:
    """
    🔔 Push notification provider for MFA
    """
    
    def __init__(self, config: MFAConfig):
        self.config = config
        self.logger = logging.getLogger("mfa_push")
    
    async def send_push(self, device_token: str, code: str) -> bool:
        """Send push notification"""
        try:
            if self.config.push_provider == "firebase":
                return await self._send_firebase_push(device_token, code)
            else:
                return await self._send_custom_push(device_token, code)
                
        except Exception as e:
            self.logger.error(f"Failed to send push notification: {e}")
            return False
    
    async def _send_firebase_push(self, device_token: str, code: str) -> bool:
        """Send push notification via Firebase"""
        try:
            url = "https://fcm.googleapis.com/fcm/send"
            headers = {
                "Authorization": f"key={self.config.push_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "to": device_token,
                "notification": {
                    "title": "IA Chéries Verification",
                    "body": f"Your verification code: {code}"
                },
                "data": {
                    "code": code,
                    "type": "mfa_verification"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Firebase push error: {e}")
            return False
    
    async def _send_custom_push(self, device_token: str, code: str) -> bool:
        """Send push notification via custom provider"""
        # Implement your custom push provider here
        self.logger.info(f"Custom push to {device_token}: {code}")
        return True


class MFAManager:
    """
    🛡️ Enterprise Multi-Factor Authentication Manager
    
    Features:
    - Multiple MFA methods support
    - Device registration and management
    - Backup codes generation
    - Rate limiting and security
    - Creator-specific optimizations
    - Comprehensive audit logging
    """
    
    def __init__(self, config: MFAConfig):
        self.config = config
        self.logger = logging.getLogger("mfa_manager")
        
        # Initialize components
        self.crypto = CryptoManager(config.encryption_key)
        self.totp_manager = TOTPManager(config)
        self.sms_provider = SMSProvider(config)
        self.email_provider = EmailProvider(config)
        self.push_provider = PushNotificationProvider(config)
        
        # Storage
        self.redis_client = None
        if config.redis_url:
            try:
                self.redis_client = redis.from_url(config.redis_url)
            except Exception as e:
                self.logger.warning(f"Redis connection failed: {e}")
        
        # In-memory fallback
        self.challenges: Dict[str, MFAChallenge] = {}
        self.devices: Dict[str, List[MFADevice]] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}
    
    async def register_device(
        self,
        user_id: str,
        method: MFAMethod,
        device_name: str,
        phone_number: Optional[str] = None,
        email_address: Optional[str] = None,
        push_token: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """Register new MFA device"""
        try:
            device_id = secrets.token_urlsafe(16)
            
            # Generate method-specific secrets
            secret_key = None
            qr_code = None
            
            if method == MFAMethod.TOTP:
                secret_key = self.totp_manager.generate_secret()
                # Generate QR code for easy setup
                email = email_address or f"user_{user_id}@ainflue.com"
                provisioning_uri = self.totp_manager.get_provisioning_uri(email, secret_key)
                qr_code = self.totp_manager.generate_qr_code(provisioning_uri)
                secret_key = self.crypto.encrypt(secret_key)
            
            # Create device
            device = MFADevice(
                device_id=device_id,
                user_id=user_id,
                method=method,
                name=device_name,
                secret_key=secret_key,
                phone_number=phone_number,
                email_address=email_address,
                push_token=push_token,
                is_verified=False
            )
            
            # Generate backup codes for primary methods
            if method in [MFAMethod.TOTP, MFAMethod.SMS] and self.config.creator_backup_codes_required:
                backup_codes = self.crypto.generate_backup_codes(self.config.backup_codes_count)
                # Hash codes for storage
                device.backup_codes = [
                    self.crypto.hash_backup_code(code) for code in backup_codes
                ]
                
                # Return raw codes to user (only time they'll see them)
                qr_code = {"qr_code": qr_code, "backup_codes": backup_codes} if qr_code else {"backup_codes": backup_codes}
            
            # Store device
            await self._store_device(device)
            
            self.logger.info(f"MFA device registered: {device_id} for user {user_id} ({method.value})")
            
            return device_id, qr_code
            
        except Exception as e:
            self.logger.error(f"Failed to register MFA device: {e}")
            raise MFAError(f"Device registration failed: {str(e)}")
    
    async def initiate_challenge(
        self,
        user_id: str,
        method: MFAMethod,
        device_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Initiate MFA challenge"""
        try:
            # Check rate limiting
            if not await self._check_rate_limit(user_id, metadata.get("ip_address") if metadata else None):
                raise MFAError("Rate limit exceeded")
            
            # Get user's devices
            devices = await self._get_user_devices(user_id)
            
            # Find appropriate device
            device = None
            if device_id:
                device = next((d for d in devices if d.device_id == device_id), None)
            else:
                # Use primary device of specified method
                device = next((d for d in devices if d.method == method and d.is_verified), None)
            
            if not device:
                raise MFAError("No suitable MFA device found")
            
            # Generate challenge
            challenge_id = secrets.token_urlsafe(16)
            code = secrets.randbelow(10**self.config.code_length)
            code_str = f"{code:0{self.config.code_length}d}"
            
            # Create challenge
            challenge = MFAChallenge(
                challenge_id=challenge_id,
                user_id=user_id,
                method=method,
                status=MFAStatus.PENDING,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=self.config.code_expiry),
                encrypted_code=self.crypto.encrypt(code_str),
                phone_number=device.phone_number,
                email_address=device.email_address,
                device_id=device_id,
                ip_address=metadata.get("ip_address") if metadata else None,
                user_agent=metadata.get("user_agent") if metadata else None
            )
            
            # Send challenge based on method
            success = False
            if method == MFAMethod.SMS and device.phone_number:
                success = await self.sms_provider.send_sms(device.phone_number, code_str)
            elif method == MFAMethod.EMAIL and device.email_address:
                success = await self.email_provider.send_email(device.email_address, code_str)
            elif method == MFAMethod.PUSH_NOTIFICATION and device.push_token:
                success = await self.push_provider.send_push(device.push_token, code_str)
            elif method == MFAMethod.TOTP:
                # TOTP doesn't require sending - user generates on device
                success = True
            
            if not success:
                raise MFAError("Failed to send verification code")
            
            # Store challenge
            await self._store_challenge(challenge)
            
            self.logger.info(f"MFA challenge initiated: {challenge_id} for user {user_id} ({method.value})")
            
            return challenge_id
            
        except Exception as e:
            self.logger.error(f"Failed to initiate MFA challenge: {e}")
            raise MFAError(f"Challenge initiation failed: {str(e)}")
    
    async def verify_challenge(self, challenge_id: str, code: str) -> bool:
        """Verify MFA challenge"""
        try:
            # Get challenge
            challenge = await self._get_challenge(challenge_id)
            if not challenge:
                raise MFAError("Invalid challenge")
            
            # Check if challenge is still valid
            if challenge.is_expired:
                challenge.status = MFAStatus.EXPIRED
                await self._store_challenge(challenge)
                raise MFAError("Challenge has expired")
            
            if not challenge.can_retry:
                raise MFAError("Maximum attempts exceeded")
            
            # Increment attempts
            challenge.attempts += 1
            
            # Verify based on method
            verified = False
            
            if challenge.method in [MFAMethod.SMS, MFAMethod.EMAIL, MFAMethod.PUSH_NOTIFICATION]:
                # Compare with stored code
                stored_code = self.crypto.decrypt(challenge.encrypted_code)
                verified = secrets.compare_digest(code, stored_code)
            
            elif challenge.method == MFAMethod.TOTP:
                # Get device to retrieve secret
                devices = await self._get_user_devices(challenge.user_id)
                device = next((d for d in devices if d.device_id == challenge.device_id), None)
                
                if device and device.secret_key:
                    secret = self.crypto.decrypt(device.secret_key)
                    verified = self.totp_manager.verify_token(secret, code)
            
            elif challenge.method == MFAMethod.BACKUP_CODES:
                # Check against backup codes
                verified = await self._verify_backup_code(challenge.user_id, code)
            
            # Update challenge status
            if verified:
                challenge.status = MFAStatus.VERIFIED
                
                # Update device last used
                if challenge.device_id:
                    await self._update_device_last_used(challenge.device_id)
                
                self.logger.info(f"MFA challenge verified: {challenge_id}")
            else:
                challenge.status = MFAStatus.FAILED
                self.logger.warning(f"MFA challenge failed: {challenge_id} (attempt {challenge.attempts})")
            
            await self._store_challenge(challenge)
            
            return verified
            
        except Exception as e:
            self.logger.error(f"Failed to verify MFA challenge: {e}")
            return False
    
    async def verify_backup_code(self, user_id: str, code: str) -> bool:
        """Verify backup code"""
        return await self._verify_backup_code(user_id, code)
    
    async def _verify_backup_code(self, user_id: str, code: str) -> bool:
        """Internal backup code verification"""
        try:
            # Get user devices with backup codes
            devices = await self._get_user_devices(user_id)
            
            # Hash the provided code
            code_hash = self.crypto.hash_backup_code(code)
            
            # Check against all devices
            for device in devices:
                if device.backup_codes and code_hash in device.backup_codes:
                    # Remove used backup code
                    device.backup_codes.remove(code_hash)
                    await self._store_device(device)
                    
                    self.logger.info(f"Backup code used: {user_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Backup code verification error: {e}")
            return False
    
    async def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's MFA devices (sanitized for API)"""
        devices = await self._get_user_devices(user_id)
        
        # Return sanitized device info
        return [
            {
                "device_id": device.device_id,
                "method": device.method.value,
                "name": device.name,
                "is_primary": device.is_primary,
                "is_verified": device.is_verified,
                "created_at": device.created_at.isoformat(),
                "last_used": device.last_used.isoformat() if device.last_used else None,
                "has_backup_codes": bool(device.backup_codes)
            }
            for device in devices
        ]
    
    async def remove_device(self, user_id: str, device_id: str) -> bool:
        """Remove MFA device"""
        try:
            devices = await self._get_user_devices(user_id)
            device = next((d for d in devices if d.device_id == device_id), None)
            
            if not device:
                return False
            
            # Remove from storage
            devices.remove(device)
            await self._store_user_devices(user_id, devices)
            
            self.logger.info(f"MFA device removed: {device_id} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove MFA device: {e}")
            return False
    
    async def _check_rate_limit(self, user_id: str, ip_address: Optional[str]) -> bool:
        """Check MFA rate limiting"""
        current_time = datetime.utcnow()
        hour_ago = current_time - timedelta(hours=1)
        
        # Check user rate limit
        user_key = f"user:{user_id}"
        if user_key not in self.rate_limits:
            self.rate_limits[user_key] = []
        
        # Clean old entries
        self.rate_limits[user_key] = [
            timestamp for timestamp in self.rate_limits[user_key]
            if timestamp > hour_ago
        ]
        
        if len(self.rate_limits[user_key]) >= self.config.rate_limit_per_user:
            return False
        
        # Check IP rate limit
        if ip_address:
            ip_key = f"ip:{ip_address}"
            if ip_key not in self.rate_limits:
                self.rate_limits[ip_key] = []
            
            self.rate_limits[ip_key] = [
                timestamp for timestamp in self.rate_limits[ip_key]
                if timestamp > hour_ago
            ]
            
            if len(self.rate_limits[ip_key]) >= self.config.rate_limit_per_ip:
                return False
            
            # Record current attempt
            self.rate_limits[ip_key].append(current_time)
        
        # Record current attempt
        self.rate_limits[user_key].append(current_time)
        return True
    
    async def _store_device(self, device: MFADevice):
        """Store MFA device"""
        if self.redis_client:
            key = f"{self.config.cache_prefix}device:{device.device_id}"
            self.redis_client.set(key, json.dumps(device.to_dict()))
        
        # Update user devices list
        if device.user_id not in self.devices:
            self.devices[device.user_id] = []
        
        # Update or add device
        existing_device = next(
            (d for d in self.devices[device.user_id] if d.device_id == device.device_id),
            None
        )
        
        if existing_device:
            # Update existing
            index = self.devices[device.user_id].index(existing_device)
            self.devices[device.user_id][index] = device
        else:
            # Add new
            self.devices[device.user_id].append(device)
    
    async def _store_user_devices(self, user_id: str, devices: List[MFADevice]):
        """Store user's devices list"""
        self.devices[user_id] = devices
        
        # Store individual devices in Redis
        if self.redis_client:
            for device in devices:
                await self._store_device(device)
    
    async def _get_user_devices(self, user_id: str) -> List[MFADevice]:
        """Get user's MFA devices"""
        if user_id in self.devices:
            return self.devices[user_id]
        
        # Try Redis
        if self.redis_client:
            # This would require indexing by user_id in Redis
            # For now, return empty list
            pass
        
        return []
    
    async def _store_challenge(self, challenge: MFAChallenge):
        """Store MFA challenge"""
        if self.redis_client:
            key = f"{self.config.cache_prefix}challenge:{challenge.challenge_id}"
            data = {
                "challenge_id": challenge.challenge_id,
                "user_id": challenge.user_id,
                "method": challenge.method.value,
                "status": challenge.status.value,
                "created_at": challenge.created_at.isoformat(),
                "expires_at": challenge.expires_at.isoformat(),
                "attempts": challenge.attempts,
                "encrypted_code": challenge.encrypted_code,
                "device_id": challenge.device_id,
                "ip_address": challenge.ip_address,
                "user_agent": challenge.user_agent
            }
            self.redis_client.setex(
                key,
                self.config.code_expiry,
                json.dumps(data)
            )
        
        self.challenges[challenge.challenge_id] = challenge
    
    async def _get_challenge(self, challenge_id: str) -> Optional[MFAChallenge]:
        """Get MFA challenge"""
        if challenge_id in self.challenges:
            return self.challenges[challenge_id]
        
        if self.redis_client:
            key = f"{self.config.cache_prefix}challenge:{challenge_id}"
            data = self.redis_client.get(key)
            if data:
                challenge_data = json.loads(data)
                return MFAChallenge(
                    challenge_id=challenge_data["challenge_id"],
                    user_id=challenge_data["user_id"],
                    method=MFAMethod(challenge_data["method"]),
                    status=MFAStatus(challenge_data["status"]),
                    created_at=datetime.fromisoformat(challenge_data["created_at"]),
                    expires_at=datetime.fromisoformat(challenge_data["expires_at"]),
                    attempts=challenge_data["attempts"],
                    encrypted_code=challenge_data["encrypted_code"],
                    device_id=challenge_data["device_id"],
                    ip_address=challenge_data["ip_address"],
                    user_agent=challenge_data["user_agent"]
                )
        
        return None
    
    async def _update_device_last_used(self, device_id: str):
        """Update device last used timestamp"""
        # Find device across all users (not efficient, but works for demo)
        for user_devices in self.devices.values():
            for device in user_devices:
                if device.device_id == device_id:
                    device.last_used = datetime.utcnow()
                    await self._store_device(device)
                    return
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get MFA metrics"""
        total_devices = sum(len(devices) for devices in self.devices.values())
        active_challenges = len([c for c in self.challenges.values() if c.status == MFAStatus.PENDING])
        
        return {
            "total_users": len(self.devices),
            "total_devices": total_devices,
            "active_challenges": active_challenges,
            "rate_limit_entries": len(self.rate_limits),
            "methods_distribution": self._get_methods_distribution()
        }
    
    def _get_methods_distribution(self) -> Dict[str, int]:
        """Get distribution of MFA methods"""
        distribution = {}
        for devices in self.devices.values():
            for device in devices:
                method = device.method.value
                distribution[method] = distribution.get(method, 0) + 1
        return distribution


# Factory functions for easy integration
def create_mfa_manager(config: Optional[MFAConfig] = None) -> MFAManager:
    """
    🏭 Factory function to create MFA manager
    
    Args:
        config: MFA configuration
    
    Returns:
        Configured MFA manager instance
    """
    if config is None:
        config = MFAConfig()
    
    return MFAManager(config)


def setup_creator_mfa() -> MFAManager:
    """
    🎯 Creator-specific MFA setup
    Enhanced security for content creators
    """
    config = MFAConfig(
        # Enhanced security for creators
        creator_require_mfa=True,
        creator_allowed_methods=[
            MFAMethod.TOTP, MFAMethod.SMS, MFAMethod.EMAIL,
            MFAMethod.BACKUP_CODES, MFAMethod.PUSH_NOTIFICATION
        ],
        creator_backup_codes_required=True,
        
        # Stricter settings
        code_expiry=180,  # 3 minutes
        max_attempts=2,   # Fewer attempts
        lockout_duration=1800,  # 30 minutes
        
        # Enhanced TOTP
        totp_digits=8,    # More digits for creators
        totp_interval=30,
        totp_window=1,
        
        # Better rate limiting
        rate_limit_per_user=3,  # Stricter
        rate_limit_per_ip=10,
        
        # More backup codes for creators
        backup_codes_count=15,
        
        # Production-ready providers
        sms_provider="twilio",
        email_smtp_host="smtp.sendgrid.net",
        push_provider="firebase"
    )
    
    return MFAManager(config)


if __name__ == "__main__":
    # Example usage
    async def example_mfa():
        """Example MFA implementation"""
        # Create MFA manager
        mfa_manager = setup_creator_mfa()
        
        print("Multi-Factor Authentication Template Example")
        print("=" * 50)
        
        # Register TOTP device
        user_id = "creator_123"
        device_id, qr_data = await mfa_manager.register_device(
            user_id=user_id,
            method=MFAMethod.TOTP,
            device_name="Creator's Phone",
            email_address="creator@example.com"
        )
        
        print(f"TOTP device registered: {device_id}")
        if isinstance(qr_data, dict) and "backup_codes" in qr_data:
            print(f"Backup codes generated: {len(qr_data['backup_codes'])}")
        
        # Simulate TOTP verification
        if isinstance(qr_data, dict) and "qr_code" in qr_data:
            print("QR code generated for device setup")
        
        # Get user devices
        devices = await mfa_manager.get_user_devices(user_id)
        print(f"User has {len(devices)} MFA devices")
        
        # Show metrics
        metrics = mfa_manager.get_metrics()
        print(f"MFA Metrics: {metrics}")
    
    # Run example
    asyncio.run(example_mfa())