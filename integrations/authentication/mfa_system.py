"""
🔐📱 MFA SYSTEM - ENTERPRISE MULTI-FACTOR AUTHENTICATION MODULE 📱🔐
Enterprise Multi-Factor Authentication for IA Chérie Platform
Copyright (C) 2024 IA Chérie Platform. All Rights Reserved.
"""

import logging
import secrets
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import qrcode
import pyotp
import io
import base64

logger = logging.getLogger(__name__)

class MFAMethod(Enum):
    """🔐 MFA Methods"""
    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"
    HARDWARE_TOKEN = "hardware_token"
    BIOMETRIC = "biometric"

class MFAStatus(Enum):
    """📊 MFA Status"""
    DISABLED = "disabled"
    PENDING_SETUP = "pending_setup"
    ENABLED = "enabled"
    TEMPORARILY_DISABLED = "temporarily_disabled"

@dataclass
class MFAToken:
    """🎫 MFA Token Data"""
    user_id: str = ""
    method: MFAMethod = MFAMethod.TOTP
    secret: str = ""
    backup_codes: List[str] = None
    created_at: datetime = None
    last_used: Optional[datetime] = None
    is_verified: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.backup_codes is None:
            self.backup_codes = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MFAVerificationResult:
    """✅ MFA Verification Result"""
    is_valid: bool = False
    method_used: Optional[MFAMethod] = None
    token_info: Optional[MFAToken] = None
    error_message: str = ""
    remaining_attempts: int = 3
    backup_code_used: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MFASetupResult:
    """🔧 MFA Setup Result"""
    is_successful: bool = False
    secret: str = ""
    qr_code: str = ""  # Base64 encoded QR code
    backup_codes: List[str] = None
    setup_url: str = ""
    error_message: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.backup_codes is None:
            self.backup_codes = []
        if self.metadata is None:
            self.metadata = {}

class MFASystem:
    """🔐📱 Enterprise MFA System"""
    
    def __init__(self, app_name: str = "IA Chérie", issuer_name: str = "IA Chérie Platform"):
        self.initialized = False
        self.app_name = app_name
        self.issuer_name = issuer_name
        self.user_mfa_tokens: Dict[str, List[MFAToken]] = {}
        self.verification_attempts: Dict[str, int] = {}
        self.lockout_times: Dict[str, datetime] = {}
        self.pending_setups: Dict[str, MFAToken] = {}
        self.logger = logging.getLogger(f"{__name__}.MFASystem")
        
        # MFA configuration
        self.totp_window = 1  # Allow 1 time step tolerance
        self.max_verification_attempts = 3
        self.lockout_duration_minutes = 15
        self.backup_codes_count = 10
        
        self._initialize_system()
        
    def _initialize_system(self):
        """🔧 Initialize MFA System"""
        try:
            # Test TOTP functionality
            test_secret = pyotp.random_base32()
            test_totp = pyotp.TOTP(test_secret)
            test_token = test_totp.now()
            
            if test_totp.verify(test_token):
                self.initialized = True
                self.logger.info("🔐 MFA System initialized successfully")
            else:
                raise Exception("TOTP test verification failed")
            
        except Exception as e:
            self.logger.error(f"❌ MFA System initialization failed: {e}")
            self.initialized = False
    
    def setup_totp(self, user_id: str, username: str) -> MFASetupResult:
        """🔧 Setup TOTP for User"""
        try:
            # Generate secret
            secret = pyotp.random_base32()
            
            # Create TOTP instance
            totp = pyotp.TOTP(secret)
            
            # Generate setup URL
            provisioning_uri = totp.provisioning_uri(
                name=username,
                issuer_name=self.issuer_name
            )
            
            # Generate QR code
            qr_code_b64 = self._generate_qr_code(provisioning_uri)
            
            # Generate backup codes
            backup_codes = self._generate_backup_codes()
            
            # Create pending MFA token
            mfa_token = MFAToken(
                user_id=user_id,
                method=MFAMethod.TOTP,
                secret=secret,
                backup_codes=backup_codes,
                is_verified=False,
                metadata={
                    'username': username,
                    'setup_uri': provisioning_uri
                }
            )
            
            # Store as pending setup
            self.pending_setups[user_id] = mfa_token
            
            result = MFASetupResult(
                is_successful=True,
                secret=secret,
                qr_code=qr_code_b64,
                backup_codes=backup_codes,
                setup_url=provisioning_uri,
                metadata={
                    'method': MFAMethod.TOTP.value,
                    'issuer': self.issuer_name
                }
            )
            
            self.logger.info(f"🔧 TOTP setup initiated for user: {user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ TOTP setup failed: {e}")
            return MFASetupResult(
                is_successful=False,
                error_message=f"TOTP setup error: {str(e)}"
            )
    
    def _generate_qr_code(self, data: str) -> str:
        """📱 Generate QR Code for TOTP Setup"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            self.logger.error(f"❌ QR code generation failed: {e}")
            return ""
    
    def _generate_backup_codes(self) -> List[str]:
        """🔑 Generate Backup Codes"""
        try:
            backup_codes = []
            for _ in range(self.backup_codes_count):
                # Generate 8-character alphanumeric code
                code = ''.join(secrets.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(8))
                # Format as XXXX-XXXX
                formatted_code = f"{code[:4]}-{code[4:]}"
                backup_codes.append(formatted_code)
            
            return backup_codes
            
        except Exception as e:
            self.logger.error(f"❌ Backup codes generation failed: {e}")
            return []
    
    def verify_totp_setup(self, user_id: str, token: str) -> MFAVerificationResult:
        """✅ Verify TOTP Setup Token"""
        try:
            if user_id not in self.pending_setups:
                return MFAVerificationResult(
                    is_valid=False,
                    error_message="No pending TOTP setup found"
                )
            
            pending_token = self.pending_setups[user_id]
            
            # Verify TOTP token
            totp = pyotp.TOTP(pending_token.secret)
            
            if totp.verify(token, valid_window=self.totp_window):
                # Setup verified, activate MFA
                pending_token.is_verified = True
                pending_token.last_used = datetime.utcnow()
                
                # Move from pending to active
                if user_id not in self.user_mfa_tokens:
                    self.user_mfa_tokens[user_id] = []
                
                self.user_mfa_tokens[user_id].append(pending_token)
                del self.pending_setups[user_id]
                
                result = MFAVerificationResult(
                    is_valid=True,
                    method_used=MFAMethod.TOTP,
                    token_info=pending_token,
                    metadata={'setup_completed': True}
                )
                
                self.logger.info(f"✅ TOTP setup verified for user: {user_id}")
                return result
            else:
                return MFAVerificationResult(
                    is_valid=False,
                    error_message="Invalid TOTP token"
                )
            
        except Exception as e:
            self.logger.error(f"❌ TOTP setup verification failed: {e}")
            return MFAVerificationResult(
                is_valid=False,
                error_message=f"Verification error: {str(e)}"
            )
    
    def verify_mfa_token(self, user_id: str, token: str, 
                        method: Optional[MFAMethod] = None) -> MFAVerificationResult:
        """✅ Verify MFA Token"""
        try:
            # Check if user is locked out
            if self._is_locked_out(user_id):
                return MFAVerificationResult(
                    is_valid=False,
                    error_message="User is temporarily locked out due to failed attempts",
                    remaining_attempts=0
                )
            
            if user_id not in self.user_mfa_tokens:
                return MFAVerificationResult(
                    is_valid=False,
                    error_message="MFA not enabled for user"
                )
            
            # Try to verify against each enabled method
            for mfa_token in self.user_mfa_tokens[user_id]:
                if method and mfa_token.method != method:
                    continue
                
                verification_result = self._verify_token_by_method(mfa_token, token)
                
                if verification_result.is_valid:
                    # Update last used time
                    mfa_token.last_used = datetime.utcnow()
                    
                    # Clear failed attempts
                    if user_id in self.verification_attempts:
                        del self.verification_attempts[user_id]
                    
                    self.logger.info(f"✅ MFA verification successful for user: {user_id}")
                    return verification_result
            
            # All verification attempts failed
            self._record_failed_attempt(user_id)
            remaining_attempts = max(0, self.max_verification_attempts - self.verification_attempts.get(user_id, 0))
            
            return MFAVerificationResult(
                is_valid=False,
                error_message="Invalid MFA token",
                remaining_attempts=remaining_attempts
            )
            
        except Exception as e:
            self.logger.error(f"❌ MFA token verification failed: {e}")
            return MFAVerificationResult(
                is_valid=False,
                error_message=f"Verification error: {str(e)}"
            )
    
    def _verify_token_by_method(self, mfa_token: MFAToken, token: str) -> MFAVerificationResult:
        """✅ Verify Token by Specific Method"""
        try:
            if mfa_token.method == MFAMethod.TOTP:
                totp = pyotp.TOTP(mfa_token.secret)
                
                if totp.verify(token, valid_window=self.totp_window):
                    return MFAVerificationResult(
                        is_valid=True,
                        method_used=MFAMethod.TOTP,
                        token_info=mfa_token
                    )
                
            elif mfa_token.method == MFAMethod.BACKUP_CODES:
                # Check if token is a valid backup code
                if token in mfa_token.backup_codes:
                    # Remove used backup code
                    mfa_token.backup_codes.remove(token)
                    
                    return MFAVerificationResult(
                        is_valid=True,
                        method_used=MFAMethod.BACKUP_CODES,
                        token_info=mfa_token,
                        backup_code_used=True,
                        metadata={'remaining_backup_codes': len(mfa_token.backup_codes)}
                    )
            
            # Method-specific verification failed
            return MFAVerificationResult(
                is_valid=False,
                method_used=mfa_token.method
            )
            
        except Exception as e:
            self.logger.error(f"❌ Token verification by method failed: {e}")
            return MFAVerificationResult(
                is_valid=False,
                error_message=str(e)
            )
    
    def verify_backup_code(self, user_id: str, backup_code: str) -> MFAVerificationResult:
        """🔑 Verify Backup Code"""
        try:
            if user_id not in self.user_mfa_tokens:
                return MFAVerificationResult(
                    is_valid=False,
                    error_message="MFA not enabled for user"
                )
            
            for mfa_token in self.user_mfa_tokens[user_id]:
                if backup_code in mfa_token.backup_codes:
                    # Remove used backup code
                    mfa_token.backup_codes.remove(backup_code)
                    mfa_token.last_used = datetime.utcnow()
                    
                    # Clear failed attempts
                    if user_id in self.verification_attempts:
                        del self.verification_attempts[user_id]
                    
                    self.logger.info(f"🔑 Backup code used for user: {user_id}")
                    
                    return MFAVerificationResult(
                        is_valid=True,
                        method_used=MFAMethod.BACKUP_CODES,
                        token_info=mfa_token,
                        backup_code_used=True,
                        metadata={
                            'remaining_backup_codes': len(mfa_token.backup_codes)
                        }
                    )
            
            return MFAVerificationResult(
                is_valid=False,
                error_message="Invalid backup code"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Backup code verification failed: {e}")
            return MFAVerificationResult(
                is_valid=False,
                error_message=f"Verification error: {str(e)}"
            )
    
    def _record_failed_attempt(self, user_id: str):
        """❌ Record Failed MFA Attempt"""
        try:
            if user_id not in self.verification_attempts:
                self.verification_attempts[user_id] = 0
            
            self.verification_attempts[user_id] += 1
            
            if self.verification_attempts[user_id] >= self.max_verification_attempts:
                # Lock out user
                self.lockout_times[user_id] = datetime.utcnow() + timedelta(minutes=self.lockout_duration_minutes)
                self.logger.warning(f"🔒 User locked out due to failed MFA attempts: {user_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed attempt recording failed: {e}")
    
    def _is_locked_out(self, user_id: str) -> bool:
        """🔒 Check if User is Locked Out"""
        try:
            if user_id in self.lockout_times:
                if datetime.utcnow() < self.lockout_times[user_id]:
                    return True
                else:
                    # Lockout expired
                    del self.lockout_times[user_id]
                    if user_id in self.verification_attempts:
                        del self.verification_attempts[user_id]
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Lockout check failed: {e}")
            return False
    
    def get_user_mfa_status(self, user_id: str) -> Dict[str, Any]:
        """📋 Get User MFA Status"""
        try:
            if user_id in self.pending_setups:
                return {
                    'status': MFAStatus.PENDING_SETUP.value,
                    'methods': [self.pending_setups[user_id].method.value],
                    'is_locked_out': self._is_locked_out(user_id),
                    'failed_attempts': self.verification_attempts.get(user_id, 0)
                }
            
            if user_id in self.user_mfa_tokens and self.user_mfa_tokens[user_id]:
                methods = [token.method.value for token in self.user_mfa_tokens[user_id]]
                last_used = max((token.last_used for token in self.user_mfa_tokens[user_id] if token.last_used), default=None)
                
                backup_codes_count = sum(len(token.backup_codes) for token in self.user_mfa_tokens[user_id])
                
                return {
                    'status': MFAStatus.ENABLED.value,
                    'methods': methods,
                    'last_used': last_used.isoformat() if last_used else None,
                    'backup_codes_remaining': backup_codes_count,
                    'is_locked_out': self._is_locked_out(user_id),
                    'failed_attempts': self.verification_attempts.get(user_id, 0)
                }
            
            return {
                'status': MFAStatus.DISABLED.value,
                'methods': [],
                'is_locked_out': False,
                'failed_attempts': 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ MFA status retrieval failed: {e}")
            return {
                'status': MFAStatus.DISABLED.value,
                'error': str(e)
            }
    
    def disable_mfa(self, user_id: str) -> bool:
        """🚫 Disable MFA for User"""
        try:
            if user_id in self.user_mfa_tokens:
                del self.user_mfa_tokens[user_id]
            
            if user_id in self.pending_setups:
                del self.pending_setups[user_id]
            
            if user_id in self.verification_attempts:
                del self.verification_attempts[user_id]
            
            if user_id in self.lockout_times:
                del self.lockout_times[user_id]
            
            self.logger.info(f"🚫 MFA disabled for user: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ MFA disable failed: {e}")
            return False
    
    def regenerate_backup_codes(self, user_id: str) -> List[str]:
        """🔄 Regenerate Backup Codes"""
        try:
            if user_id not in self.user_mfa_tokens:
                return []
            
            new_backup_codes = self._generate_backup_codes()
            
            # Update backup codes for all MFA tokens
            for mfa_token in self.user_mfa_tokens[user_id]:
                mfa_token.backup_codes = new_backup_codes.copy()
            
            self.logger.info(f"🔄 Backup codes regenerated for user: {user_id}")
            return new_backup_codes
            
        except Exception as e:
            self.logger.error(f"❌ Backup codes regeneration failed: {e}")
            return []
    
    def is_initialized(self) -> bool:
        """✅ Check Initialization Status"""
        return self.initialized

# Instance globale
mfa_system = MFASystem()

if mfa_system.is_initialized():
    logger.info("🚀💯🔥 MFA SYSTEM MODULE LOADED - AUTHENTICATION SECURITY! 🔥💯🚀")
    logger.info("✅ Enterprise multi-factor authentication with TOTP and backup codes operational!")
    logger.info("🏆 CRITICAL MFA MODULE FOR 100% SUCCESS ACHIEVED!")

__all__ = [
    'MFASystem',
    'MFAToken',
    'MFAVerificationResult',
    'MFASetupResult',
    'MFAMethod',
    'MFAStatus',
    'mfa_system',
]