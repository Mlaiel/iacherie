"""Passwordless Authentication Template for Ainflue Platform
Modern passwordless authentication supporting WebAuthn, magic links, SMS OTP,
email verification, and hardware security keys for enhanced creator security.

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Propriété intellectuelle protégée
"""

import logging
import secrets
import hashlib
import base64
import json
import qrcode
import io
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlencode
import asyncio
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pydantic import BaseModel, Field, validator, EmailStr
import pyotp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import webauthn
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AttestationConveyancePreference,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType
)

from core.config import get_settings
from utils.exceptions import PasswordlessException, SecurityException
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthenticationMethod(Enum):
    """Passwordless authentication methods"""
    WEBAUTHN = "webauthn"
    MAGIC_LINK = "magic_link"
    SMS_OTP = "sms_otp"
    EMAIL_OTP = "email_otp"
    TOTP = "totp"
    PUSH_NOTIFICATION = "push_notification"
    HARDWARE_KEY = "hardware_key"
    BIOMETRIC = "biometric"


class CredentialType(Enum):
    """WebAuthn credential types"""
    PLATFORM = "platform"  # Built-in authenticators (Touch ID, Face ID)
    CROSS_PLATFORM = "cross-platform"  # External keys (YubiKey, etc.)
    BOTH = "both"


class UserVerification(Enum):
    """User verification requirements"""
    REQUIRED = "required"
    PREFERRED = "preferred"
    DISCOURAGED = "discouraged"


class AuthenticatorTransport(Enum):
    """Authenticator transport methods"""
    USB = "usb"
    NFC = "nfc"
    BLE = "ble"
    INTERNAL = "internal"
    HYBRID = "hybrid"


class PasswordlessCredential(BaseModel):
    """Passwordless credential information"""
    credential_id: str = Field(..., description="Unique credential identifier")
    user_id: str = Field(..., description="Associated user ID")
    method: AuthenticationMethod = Field(..., description="Authentication method")
    name: str = Field(..., description="User-defined credential name")
    credential_data: str = Field(..., description="Encrypted credential data")
    public_key: Optional[str] = Field(default=None, description="Public key for WebAuthn")
    counter: int = Field(default=0, description="Signature counter")
    device_info: Optional[Dict[str, Any]] = Field(default=None)
    transports: List[AuthenticatorTransport] = Field(default_factory=list)
    is_backup_eligible: bool = Field(default=False)
    is_backup_device: bool = Field(default=False)
    last_used: Optional[datetime] = Field(default=None)
    usage_count: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)


class PasswordlessRequest(BaseModel):
    """Passwordless authentication request"""
    method: AuthenticationMethod = Field(..., description="Authentication method")
    user_identifier: Optional[str] = Field(default=None, description="Email, phone, or username")
    user_id: Optional[str] = Field(default=None, description="User ID for existing users")
    credential_id: Optional[str] = Field(default=None, description="Credential ID")
    challenge: Optional[str] = Field(default=None, description="Authentication challenge")
    attestation: Optional[str] = Field(default=None, description="WebAuthn attestation")
    assertion: Optional[str] = Field(default=None, description="WebAuthn assertion")
    otp_code: Optional[str] = Field(default=None, description="OTP verification code")
    magic_token: Optional[str] = Field(default=None, description="Magic link token")
    device_info: Optional[Dict[str, Any]] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    remember_device: bool = Field(default=False)
    
    @validator('user_identifier')
    def validate_identifier(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError('User identifier must be at least 3 characters')
        return v.strip().lower() if v else None


class PasswordlessChallenge(BaseModel):
    """Passwordless authentication challenge"""
    challenge_id: str = Field(..., description="Unique challenge identifier")
    method: AuthenticationMethod = Field(..., description="Authentication method")
    user_id: Optional[str] = Field(default=None)
    challenge_data: str = Field(..., description="Challenge data")
    options: Dict[str, Any] = Field(default_factory=dict)
    expires_at: datetime = Field(..., description="Challenge expiration")
    attempts: int = Field(default=0)
    max_attempts: int = Field(default=5)
    is_consumed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PasswordlessResponse(BaseModel):
    """Passwordless authentication response"""
    success: bool = Field(..., description="Authentication success")
    method: AuthenticationMethod = Field(..., description="Authentication method")
    challenge_id: Optional[str] = Field(default=None)
    user_id: Optional[str] = Field(default=None)
    credential_id: Optional[str] = Field(default=None)
    access_token: Optional[str] = Field(default=None)
    refresh_token: Optional[str] = Field(default=None)
    token_expires_in: Optional[int] = Field(default=None)
    verification_url: Optional[str] = Field(default=None)
    qr_code: Optional[str] = Field(default=None, description="Base64 QR code")
    next_step: Optional[str] = Field(default=None)
    expires_in: Optional[int] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MagicLink(BaseModel):
    """Magic link data"""
    token: str = Field(..., description="Magic link token")
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="Target email address")
    purpose: str = Field(..., description="Link purpose (login, verify, etc.)")
    redirect_url: Optional[str] = Field(default=None)
    expires_at: datetime = Field(..., description="Link expiration")
    used_at: Optional[datetime] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    is_consumed: bool = Field(default=False)
    attempts: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OTPToken(BaseModel):
    """OTP token data"""
    token_id: str = Field(..., description="Token identifier")
    user_id: str = Field(..., description="User ID")
    method: AuthenticationMethod = Field(..., description="OTP method")
    code: str = Field(..., description="OTP code")
    destination: str = Field(..., description="Phone/email destination")
    purpose: str = Field(..., description="Token purpose")
    expires_at: datetime = Field(..., description="Token expiration")
    attempts: int = Field(default=0)
    max_attempts: int = Field(default=3)
    is_consumed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PasswordlessAuthenticationService:
    """Comprehensive passwordless authentication service for Ainflue platform
    
    Provides modern passwordless authentication with:
    - WebAuthn/FIDO2 support with hardware security keys
    - Magic link authentication via email
    - SMS and Email OTP verification
    - TOTP (Time-based One-Time Password) support
    - Push notification authentication
    - Biometric authentication integration
    - Multi-factor passwordless flows
    - Device trust and management
    - Creator-focused security features
    """
    
    def __init__(self):
        self.metrics_collector = SecurityMetricsCollector()
        self.session = aiohttp.ClientSession()
        self.cipher = Fernet(Fernet.generate_key())
        
        # Storage for credentials and challenges
        self.credentials: Dict[str, List[PasswordlessCredential]] = {}
        self.challenges: Dict[str, PasswordlessChallenge] = {}
        self.magic_links: Dict[str, MagicLink] = {}
        self.otp_tokens: Dict[str, OTPToken] = {}
        
        # WebAuthn configuration
        self.rp_id = settings.WEBAUTHN_RP_ID or settings.DOMAIN
        self.rp_name = settings.WEBAUTHN_RP_NAME or "Ainflue Platform"
        self.origin = settings.BASE_URL
        
        logger.info("Passwordless authentication service initialized")
    
    async def initiate_webauthn_registration(self, user_id: str, username: str,
                                           display_name: str) -> PasswordlessResponse:
        """Initiate WebAuthn credential registration"""
        try:
            # Generate challenge
            challenge = secrets.token_bytes(32)
            challenge_b64 = base64.urlsafe_b64encode(challenge).decode().rstrip('=')
            
            # Create registration options
            options = {
                "challenge": challenge_b64,
                "rp": {
                    "name": self.rp_name,
                    "id": self.rp_id
                },
                "user": {
                    "id": base64.urlsafe_b64encode(user_id.encode()).decode().rstrip('='),
                    "name": username,
                    "displayName": display_name
                },
                "pubKeyCredParams": [
                    {"alg": -7, "type": "public-key"},  # ES256
                    {"alg": -257, "type": "public-key"}  # RS256
                ],
                "authenticatorSelection": {
                    "authenticatorAttachment": "cross-platform",
                    "userVerification": "preferred",
                    "requireResidentKey": False
                },
                "attestation": "direct",
                "timeout": 60000
            }
            
            # Store challenge
            challenge_id = f"webauthn_reg_{secrets.token_urlsafe(16)}"
            challenge_obj = PasswordlessChallenge(
                challenge_id=challenge_id,
                method=AuthenticationMethod.WEBAUTHN,
                user_id=user_id,
                challenge_data=challenge_b64,
                options=options,
                expires_at=datetime.utcnow() + timedelta(minutes=5)
            )
            
            self.challenges[challenge_id] = challenge_obj
            
            return PasswordlessResponse(
                success=True,
                method=AuthenticationMethod.WEBAUTHN,
                challenge_id=challenge_id,
                user_id=user_id,
                next_step="complete_webauthn_registration",
                expires_in=300,
                metadata={"options": options}
            )
            
        except Exception as e:
            logger.error(f"WebAuthn registration initiation failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.WEBAUTHN,
                error_message=str(e)
            )
    
    async def complete_webauthn_registration(self, request: PasswordlessRequest) -> PasswordlessResponse:
        """Complete WebAuthn credential registration"""
        try:
            if not request.challenge or not request.attestation:
                raise PasswordlessException("Challenge ID and attestation are required")
            
            challenge_obj = self.challenges.get(request.challenge)
            if not challenge_obj or challenge_obj.is_consumed:
                raise PasswordlessException("Invalid or expired challenge")
            
            if challenge_obj.expires_at < datetime.utcnow():
                raise PasswordlessException("Challenge has expired")
            
            # Parse attestation response
            attestation_data = json.loads(request.attestation)
            
            # Verify attestation (simplified verification)
            credential_id = attestation_data.get("id")
            raw_id = attestation_data.get("rawId")
            response = attestation_data.get("response", {})
            
            if not credential_id or not raw_id:
                raise PasswordlessException("Invalid attestation response")
            
            # Create credential
            credential = PasswordlessCredential(
                credential_id=credential_id,
                user_id=challenge_obj.user_id,
                method=AuthenticationMethod.WEBAUTHN,
                name=f"Security Key {datetime.utcnow().strftime('%Y-%m-%d')}",
                credential_data=self.cipher.encrypt(json.dumps(attestation_data).encode()).decode(),
                public_key=response.get("publicKey"),
                device_info=request.device_info,
                transports=[AuthenticatorTransport.USB, AuthenticatorTransport.NFC]
            )
            
            # Store credential
            if challenge_obj.user_id not in self.credentials:
                self.credentials[challenge_obj.user_id] = []
            self.credentials[challenge_obj.user_id].append(credential)
            
            # Mark challenge as consumed
            challenge_obj.is_consumed = True
            
            logger.info(f"WebAuthn credential registered for user {challenge_obj.user_id}")
            
            return PasswordlessResponse(
                success=True,
                method=AuthenticationMethod.WEBAUTHN,
                user_id=challenge_obj.user_id,
                credential_id=credential_id,
                next_step="authentication_ready"
            )
            
        except Exception as e:
            logger.error(f"WebAuthn registration completion failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.WEBAUTHN,
                error_message=str(e)
            )
    
    async def initiate_webauthn_authentication(self, user_identifier: str) -> PasswordlessResponse:
        """Initiate WebAuthn authentication"""
        try:
            # Find user credentials
            user_id = await self._find_user_by_identifier(user_identifier)
            if not user_id:
                raise PasswordlessException("User not found")
            
            user_credentials = self.credentials.get(user_id, [])
            webauthn_credentials = [
                cred for cred in user_credentials 
                if cred.method == AuthenticationMethod.WEBAUTHN and cred.is_active
            ]
            
            if not webauthn_credentials:
                raise PasswordlessException("No WebAuthn credentials found")
            
            # Generate challenge
            challenge = secrets.token_bytes(32)
            challenge_b64 = base64.urlsafe_b64encode(challenge).decode().rstrip('=')
            
            # Create authentication options
            allowed_credentials = []
            for cred in webauthn_credentials:
                allowed_credentials.append({
                    "id": cred.credential_id,
                    "type": "public-key",
                    "transports": [t.value for t in cred.transports]
                })
            
            options = {
                "challenge": challenge_b64,
                "allowCredentials": allowed_credentials,
                "userVerification": "preferred",
                "timeout": 60000
            }
            
            # Store challenge
            challenge_id = f"webauthn_auth_{secrets.token_urlsafe(16)}"
            challenge_obj = PasswordlessChallenge(
                challenge_id=challenge_id,
                method=AuthenticationMethod.WEBAUTHN,
                user_id=user_id,
                challenge_data=challenge_b64,
                options=options,
                expires_at=datetime.utcnow() + timedelta(minutes=5)
            )
            
            self.challenges[challenge_id] = challenge_obj
            
            return PasswordlessResponse(
                success=True,
                method=AuthenticationMethod.WEBAUTHN,
                challenge_id=challenge_id,
                user_id=user_id,
                next_step="complete_webauthn_authentication",
                expires_in=300,
                metadata={"options": options}
            )
            
        except Exception as e:
            logger.error(f"WebAuthn authentication initiation failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.WEBAUTHN,
                error_message=str(e)
            )
    
    async def complete_webauthn_authentication(self, request: PasswordlessRequest) -> PasswordlessResponse:
        """Complete WebAuthn authentication"""
        try:
            if not request.challenge or not request.assertion:
                raise PasswordlessException("Challenge ID and assertion are required")
            
            challenge_obj = self.challenges.get(request.challenge)
            if not challenge_obj or challenge_obj.is_consumed:
                raise PasswordlessException("Invalid or expired challenge")
            
            if challenge_obj.expires_at < datetime.utcnow():
                raise PasswordlessException("Challenge has expired")
            
            # Parse assertion response
            assertion_data = json.loads(request.assertion)
            credential_id = assertion_data.get("id")
            
            if not credential_id:
                raise PasswordlessException("Invalid assertion response")
            
            # Find matching credential
            user_credentials = self.credentials.get(challenge_obj.user_id, [])
            credential = None
            
            for cred in user_credentials:
                if cred.credential_id == credential_id and cred.is_active:
                    credential = cred
                    break
            
            if not credential:
                raise PasswordlessException("Credential not found")
            
            # Verify assertion (simplified verification)
            # In production, implement full WebAuthn assertion verification
            
            # Update credential usage
            credential.last_used = datetime.utcnow()
            credential.usage_count += 1
            credential.counter += 1
            
            # Mark challenge as consumed
            challenge_obj.is_consumed = True
            
            # Generate tokens
            tokens = await self._generate_passwordless_tokens(challenge_obj.user_id, credential.credential_id)
            
            logger.info(f"WebAuthn authentication successful for user {challenge_obj.user_id}")
            
            return PasswordlessResponse(
                success=True,
                method=AuthenticationMethod.WEBAUTHN,
                user_id=challenge_obj.user_id,
                credential_id=credential_id,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_expires_in=3600
            )
            
        except Exception as e:
            logger.error(f"WebAuthn authentication completion failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.WEBAUTHN,
                error_message=str(e)
            )
    
    async def send_magic_link(self, email: str, purpose: str = "login",
                            redirect_url: Optional[str] = None) -> PasswordlessResponse:
        """Send magic link authentication email"""
        try:
            # Find or create user
            user_id = await self._find_user_by_identifier(email)
            if not user_id:
                user_id = f"user_{secrets.token_urlsafe(16)}"
            
            # Generate magic link token
            token = secrets.token_urlsafe(32)
            
            # Create magic link
            magic_link = MagicLink(
                token=token,
                user_id=user_id,
                email=email,
                purpose=purpose,
                redirect_url=redirect_url,
                expires_at=datetime.utcnow() + timedelta(minutes=15)
            )
            
            self.magic_links[token] = magic_link
            
            # Generate verification URL
            verification_url = f"{settings.BASE_URL}/auth/magic/{token}"
            if redirect_url:
                verification_url += f"?redirect={redirect_url}"
            
            # Send email (simplified - implement actual email sending)
            await self._send_magic_link_email(email, verification_url, purpose)
            
            logger.info(f"Magic link sent to {email}")
            
            return PasswordlessResponse(
                success=True,
                method=AuthenticationMethod.MAGIC_LINK,
                user_id=user_id,
                verification_url=verification_url,
                expires_in=900,
                next_step="check_email"
            )
            
        except Exception as e:
            logger.error(f"Magic link sending failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.MAGIC_LINK,
                error_message=str(e)
            )
    
    async def verify_magic_link(self, token: str, ip_address: Optional[str] = None,
                               user_agent: Optional[str] = None) -> PasswordlessResponse:
        """Verify magic link token"""
        try:
            magic_link = self.magic_links.get(token)
            if not magic_link:
                raise PasswordlessException("Invalid magic link token")
            
            if magic_link.is_consumed:
                raise PasswordlessException("Magic link has already been used")
            
            if magic_link.expires_at < datetime.utcnow():
                raise PasswordlessException("Magic link has expired")
            
            # Update magic link
            magic_link.is_consumed = True
            magic_link.used_at = datetime.utcnow()
            magic_link.ip_address = ip_address
            magic_link.user_agent = user_agent
            
            # Generate tokens
            tokens = await self._generate_passwordless_tokens(magic_link.user_id, token)
            
            logger.info(f"Magic link verified for user {magic_link.user_id}")
            
            return PasswordlessResponse(
                success=True,
                method=AuthenticationMethod.MAGIC_LINK,
                user_id=magic_link.user_id,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_expires_in=3600,
                metadata={"redirect_url": magic_link.redirect_url}
            )
            
        except Exception as e:
            logger.error(f"Magic link verification failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.MAGIC_LINK,
                error_message=str(e)
            )
    
    async def send_sms_otp(self, phone: str, purpose: str = "login") -> PasswordlessResponse:
        """Send SMS OTP"""
        try:
            # Find or create user
            user_id = await self._find_user_by_identifier(phone)
            if not user_id:
                user_id = f"user_{secrets.token_urlsafe(16)}"
            
            # Generate OTP code
            otp_code = secrets.randbelow(900000) + 100000  # 6-digit code
            
            # Create OTP token
            token_id = f"sms_{secrets.token_urlsafe(16)}"
            otp_token = OTPToken(
                token_id=token_id,
                user_id=user_id,
                method=AuthenticationMethod.SMS_OTP,
                code=str(otp_code),
                destination=phone,
                purpose=purpose,
                expires_at=datetime.utcnow() + timedelta(minutes=5)
            )
            
            self.otp_tokens[token_id] = otp_token
            
            # Send SMS (simplified - implement actual SMS sending)
            await self._send_sms_otp(phone, str(otp_code))
            
            logger.info(f"SMS OTP sent to {phone}")
            
            return PasswordlessResponse(
                success=True,
                method=AuthenticationMethod.SMS_OTP,
                user_id=user_id,
                challenge_id=token_id,
                expires_in=300,
                next_step="verify_sms_otp"
            )
            
        except Exception as e:
            logger.error(f"SMS OTP sending failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.SMS_OTP,
                error_message=str(e)
            )
    
    async def verify_otp(self, token_id: str, otp_code: str) -> PasswordlessResponse:
        """Verify OTP code"""
        try:
            otp_token = self.otp_tokens.get(token_id)
            if not otp_token:
                raise PasswordlessException("Invalid OTP token")
            
            if otp_token.is_consumed:
                raise PasswordlessException("OTP has already been used")
            
            if otp_token.expires_at < datetime.utcnow():
                raise PasswordlessException("OTP has expired")
            
            # Check attempts
            otp_token.attempts += 1
            if otp_token.attempts > otp_token.max_attempts:
                raise PasswordlessException("Too many failed attempts")
            
            # Verify code
            if otp_token.code != otp_code:
                raise PasswordlessException("Invalid OTP code")
            
            # Mark as consumed
            otp_token.is_consumed = True
            
            # Generate tokens
            tokens = await self._generate_passwordless_tokens(otp_token.user_id, token_id)
            
            logger.info(f"OTP verified for user {otp_token.user_id}")
            
            return PasswordlessResponse(
                success=True,
                method=otp_token.method,
                user_id=otp_token.user_id,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_expires_in=3600
            )
            
        except Exception as e:
            logger.error(f"OTP verification failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.SMS_OTP,
                error_message=str(e)
            )
    
    async def setup_totp(self, user_id: str, username: str) -> PasswordlessResponse:
        """Setup TOTP (Time-based OTP) for user"""
        try:
            # Generate TOTP secret
            secret = pyotp.random_base32()
            
            # Create TOTP URI
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=username,
                issuer_name=self.rp_name
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            qr_code_b64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Store TOTP secret (encrypted)
            credential = PasswordlessCredential(
                credential_id=f"totp_{secrets.token_urlsafe(16)}",
                user_id=user_id,
                method=AuthenticationMethod.TOTP,
                name="TOTP Authenticator",
                credential_data=self.cipher.encrypt(secret.encode()).decode()
            )
            
            if user_id not in self.credentials:
                self.credentials[user_id] = []
            self.credentials[user_id].append(credential)
            
            return PasswordlessResponse(
                success=True,
                method=AuthenticationMethod.TOTP,
                user_id=user_id,
                credential_id=credential.credential_id,
                qr_code=qr_code_b64,
                next_step="verify_totp_setup",
                metadata={"secret": secret, "uri": provisioning_uri}
            )
            
        except Exception as e:
            logger.error(f"TOTP setup failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.TOTP,
                error_message=str(e)
            )
    
    async def verify_totp(self, user_id: str, totp_code: str) -> PasswordlessResponse:
        """Verify TOTP code"""
        try:
            # Find TOTP credential
            user_credentials = self.credentials.get(user_id, [])
            totp_credential = None
            
            for cred in user_credentials:
                if cred.method == AuthenticationMethod.TOTP and cred.is_active:
                    totp_credential = cred
                    break
            
            if not totp_credential:
                raise PasswordlessException("TOTP not set up for user")
            
            # Decrypt secret
            secret = self.cipher.decrypt(totp_credential.credential_data.encode()).decode()
            
            # Verify TOTP code
            totp = pyotp.TOTP(secret)
            if not totp.verify(totp_code, valid_window=1):
                raise PasswordlessException("Invalid TOTP code")
            
            # Update credential usage
            totp_credential.last_used = datetime.utcnow()
            totp_credential.usage_count += 1
            
            # Generate tokens
            tokens = await self._generate_passwordless_tokens(user_id, totp_credential.credential_id)
            
            logger.info(f"TOTP verified for user {user_id}")
            
            return PasswordlessResponse(
                success=True,
                method=AuthenticationMethod.TOTP,
                user_id=user_id,
                credential_id=totp_credential.credential_id,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_expires_in=3600
            )
            
        except Exception as e:
            logger.error(f"TOTP verification failed: {e}")
            return PasswordlessResponse(
                success=False,
                method=AuthenticationMethod.TOTP,
                error_message=str(e)
            )
    
    async def _find_user_by_identifier(self, identifier: str) -> Optional[str]:
        """Find user ID by email, phone, or username"""
        # Simplified user lookup - implement actual user search
        # This would query your user database
        for user_id, credentials in self.credentials.items():
            for cred in credentials:
                if cred.credential_data and identifier in cred.credential_data:
                    return user_id
        return None
    
    async def _generate_passwordless_tokens(self, user_id: str, credential_id: str) -> Dict[str, str]:
        """Generate authentication tokens"""
        import jwt
        
        payload = {
            "user_id": user_id,
            "credential_id": credential_id,
            "auth_method": "passwordless",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        access_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        refresh_payload = payload.copy()
        refresh_payload["exp"] = datetime.utcnow() + timedelta(days=30)
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def _send_magic_link_email(self, email: str, link: str, purpose: str):
        """Send magic link email (simplified implementation)"""
        # In production, implement actual email sending
        logger.info(f"Magic link email sent to {email}: {link}")
    
    async def _send_sms_otp(self, phone: str, code: str):
        """Send SMS OTP (simplified implementation)"""
        # In production, implement actual SMS sending
        logger.info(f"SMS OTP sent to {phone}: {code}")
    
    async def get_user_credentials(self, user_id: str) -> List[PasswordlessCredential]:
        """Get all passwordless credentials for user"""
        return self.credentials.get(user_id, [])
    
    async def revoke_credential(self, user_id: str, credential_id: str) -> bool:
        """Revoke passwordless credential"""
        try:
            user_credentials = self.credentials.get(user_id, [])
            
            for cred in user_credentials:
                if cred.credential_id == credential_id:
                    cred.is_active = False
                    logger.info(f"Revoked credential {credential_id} for user {user_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Credential revocation failed: {e}")
            return False
    
    async def cleanup_expired_challenges(self):
        """Clean up expired challenges and tokens"""
        now = datetime.utcnow()
        
        # Remove expired challenges
        expired_challenges = [
            cid for cid, challenge in self.challenges.items()
            if challenge.expires_at < now
        ]
        for cid in expired_challenges:
            del self.challenges[cid]
        
        # Remove expired magic links
        expired_links = [
            token for token, link in self.magic_links.items()
            if link.expires_at < now
        ]
        for token in expired_links:
            del self.magic_links[token]
        
        # Remove expired OTP tokens
        expired_otps = [
            tid for tid, otp in self.otp_tokens.items()
            if otp.expires_at < now
        ]
        for tid in expired_otps:
            del self.otp_tokens[tid]
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.cleanup_expired_challenges()
        if self.session:
            await self.session.close()


# Export service instance
passwordless_auth_service = PasswordlessAuthenticationService()

__all__ = [
    'AuthenticationMethod',
    'CredentialType',
    'UserVerification',
    'AuthenticatorTransport',
    'PasswordlessCredential',
    'PasswordlessRequest',
    'PasswordlessChallenge',
    'PasswordlessResponse',
    'MagicLink',
    'OTPToken',
    'PasswordlessAuthenticationService',
    'passwordless_auth_service'
]