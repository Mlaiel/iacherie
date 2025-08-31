"""🔐 User Credentials Management - Enterprise Password & Security System
======================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Type: Production-Ready Credential Management System
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING: Unauthorized use strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Business Logic: User Registration → Credential Encryption → Security Policy Enforcement → 
Password History → Account Protection → Audit Logging
"""import asyncio
import hashlib
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON, Index, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from passlib.hash import bcrypt, scrypt
import pyotp
from cryptography.fernet import Fernet
import zxcvbn

logger = logging.getLogger(__name__)

Base = declarative_base()

class CredentialType(Enum):
    """Credential type classifications"""    PASSWORD = "password"
    PIN = "pin"
    BIOMETRIC = "biometric"
    API_KEY = "api_key"
    RECOVERY_CODE = "recovery_code"
    BACKUP_CODE = "backup_code"

class SecurityLevel(Enum):
    """Security level classifications"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

class AccountStatus(Enum):
    """Account status states"""    ACTIVE = "active"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    DISABLED = "disabled"
    COMPROMISED = "compromised"

@dataclass
class PasswordPolicy:
    """Password policy configuration"""    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    min_special_chars: int = 2
    require_non_dictionary: bool = True
    min_entropy_score: int = 3
    password_history_count: int = 12
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    require_change_interval_days: int = 90

@dataclass
class SecurityQuestion:
    """Security question structure"""    question_id: str
    question_text: str
    answer_hash: str
    salt: str
    created_at: datetime
    last_updated: datetime

@dataclass
class CredentialMetadata:
    """Credential metadata"""    created_by: str = ""
    created_from_ip: str = ""
    created_from_device: str = ""
    strength_score: int = 0
    entropy_bits: float = 0.0
    contains_personal_info: bool = False
    is_common_password: bool = False
    source: str = "manual"

class UserCredentials(Base):
    """Database model for user credentials"""    __tablename__ = 'user_credentials'
    
    credential_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    credential_type = Column(String, nullable=False)
    credential_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    algorithm = Column(String, nullable=False, default="scrypt")
    iterations = Column(Integer, nullable=False, default=32768)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_updated = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_temporary = Column(Boolean, nullable=False, default=False)
    failed_attempts = Column(Integer, nullable=False, default=0)
    last_failed_attempt = Column(DateTime, nullable=True)
    last_successful_use = Column(DateTime, nullable=True)
    security_level = Column(String, nullable=False, default=SecurityLevel.MEDIUM.value)
    metadata = Column(JSON, nullable=True)
    encrypted_recovery_hint = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('idx_user_cred_type', 'user_id', 'credential_type'),
        Index('idx_user_cred_active', 'user_id', 'is_active'),
    )

class PasswordHistory(Base):
    """Database model for password history"""    __tablename__ = 'password_history'
    
    history_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    algorithm = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    changed_from_ip = Column(String, nullable=True)
    changed_reason = Column(String, nullable=True)
    
    __table_args__ = (
        Index('idx_password_history_user_date', 'user_id', 'created_at'),
    )

class SecurityQuestions(Base):
    """Database model for security questions"""    __tablename__ = 'security_questions'
    
    question_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    question_type = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    answer_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_updated = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, nullable=False, default=True)
    failed_attempts = Column(Integer, nullable=False, default=0)
    
    __table_args__ = (
        Index('idx_security_questions_user', 'user_id', 'is_active'),
    )

class AccountSecurity(Base):
    """Database model for account security settings"""    __tablename__ = 'account_security'
    
    security_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, unique=True, index=True)
    account_status = Column(String, nullable=False, default=AccountStatus.ACTIVE.value)
    security_level = Column(String, nullable=False, default=SecurityLevel.MEDIUM.value)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    last_failed_login = Column(DateTime, nullable=True)
    lockout_until = Column(DateTime, nullable=True)
    last_successful_login = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, nullable=True)
    password_change_required = Column(Boolean, nullable=False, default=False)
    two_factor_enabled = Column(Boolean, nullable=False, default=False)
    two_factor_backup_codes = Column(JSON, nullable=True)
    security_questions_set = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, nullable=True)

class UserCredentialsRepository:
    """    Enterprise-grade user credentials management repository.
    
    Features:
    - Secure password storage with multiple hashing algorithms
    - Password policy enforcement and strength validation
    - Password history management and reuse prevention
    - Account lockout and security policies
    - Security questions and recovery mechanisms
    - Comprehensive audit logging
    """    
    def __init__(
        self,
        session: AsyncSession,
        encryption_key: str,
        password_policy: Optional[PasswordPolicy] = None
    ):
        self.session = session
        self.fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        self.policy = password_policy or PasswordPolicy()
        
        # Password context for hashing
        self.pwd_context = CryptContext(
            schemes=["scrypt", "bcrypt"],
            default="scrypt",
            scrypt__rounds=32768,
            bcrypt__rounds=12,
            deprecated="auto"
        )
        
        # Predefined security questions
        self.security_questions = [
            "What was the name of your first pet?",
            "What city were you born in?",
            "What was your childhood nickname?",
            "What was the make of your first car?",
            "What elementary school did you attend?",
            "What was your mother's maiden name?",
            "What street did you grow up on?",
            "What was your favorite food as a child?",
            "What was the name of your best friend in high school?",
            "What was your first job?"
        ]
    
    async def create_credentials(
        self,
        user_id: str,
        password: str,
        credential_type: CredentialType = CredentialType.PASSWORD,
        metadata: Optional[CredentialMetadata] = None
    ) -> str:
        """Create new user credentials with policy validation"""        try:
            # Validate password against policy
            if credential_type == CredentialType.PASSWORD:
                validation_result = await self.validate_password_policy(password, user_id)
                if not validation_result['is_valid']:
                    raise ValueError(f"Password policy violation: {', '.join(validation_result['errors'])}")
            
            # Check password history
            if await self._is_password_reused(user_id, password):
                raise ValueError("Password has been used recently and cannot be reused")
            
            # Generate salt and hash
            salt = secrets.token_hex(32)
            password_hash = self.pwd_context.hash(password + salt)
            
            # Calculate password strength
            strength_analysis = zxcvbn.zxcvbn(password)
            
            credential_id = str(uuid4())
            
            # Create credential record
            credential = UserCredentials(
                credential_id=credential_id,
                user_id=user_id,
                credential_type=credential_type.value,
                credential_hash=password_hash,
                salt=salt,
                algorithm="scrypt",
                security_level=self._determine_security_level(strength_analysis['score']).value,
                metadata={
                    'strength_score': strength_analysis['score'],
                    'entropy_bits': strength_analysis['guesses_log10'],
                    'feedback': strength_analysis['feedback'],
                    'created_by': metadata.created_by if metadata else "",
                    'created_from_ip': metadata.created_from_ip if metadata else "",
                    'created_from_device': metadata.created_from_device if metadata else ""
                }
            )
            
            self.session.add(credential)
            
            # Add to password history
            await self._add_to_password_history(
                user_id=user_id,
                password_hash=password_hash,
                salt=salt,
                changed_from_ip=metadata.created_from_ip if metadata else None,
                changed_reason="Account creation"
            )
            
            # Update account security settings
            await self._update_account_security(user_id, last_password_change=True)
            
            await self.session.commit()
            
            logger.info(f"Credentials created successfully for user {user_id}")
            return credential_id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create credentials for user {user_id}: {e}")
            raise
    
    async def verify_credentials(
        self,
        user_id: str,
        password: str,
        credential_type: CredentialType = CredentialType.PASSWORD
    ) -> Dict[str, Any]:
        """Verify user credentials with security checks"""        try:
            # Check account status and lockout
            account_status = await self._check_account_status(user_id)
            if not account_status['can_authenticate']:
                return {
                    'verified': False,
                    'reason': account_status['reason'],
                    'lockout_until': account_status.get('lockout_until')
                }
            
            # Get active credentials
            stmt = select(UserCredentials).where(
                UserCredentials.user_id == user_id,
                UserCredentials.credential_type == credential_type.value,
                UserCredentials.is_active == True
            ).order_by(UserCredentials.created_at.desc())
            
            result = await self.session.execute(stmt)
            credential = result.scalar_one_or_none()
            
            if not credential:
                await self._record_failed_attempt(user_id, "No credentials found")
                return {'verified': False, 'reason': 'Invalid credentials'}
            
            # Verify password
            is_valid = self.pwd_context.verify(
                password + credential.salt,
                credential.credential_hash
            )
            
            if is_valid:
                # Successful authentication
                await self._record_successful_authentication(user_id, credential.credential_id)
                
                # Check if password change is required
                password_age = datetime.now(timezone.utc) - credential.last_updated
                change_required = password_age.days >= self.policy.password_change_interval_days
                
                return {
                    'verified': True,
                    'credential_id': credential.credential_id,
                    'security_level': credential.security_level,
                    'password_change_required': change_required,
                    'password_age_days': password_age.days
                }
            else:
                # Failed authentication
                await self._record_failed_attempt(user_id, "Invalid password")
                return {'verified': False, 'reason': 'Invalid credentials'}
                
        except Exception as e:
            logger.error(f"Credential verification failed for user {user_id}: {e}")
            raise
    
    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str,
        metadata: Optional[CredentialMetadata] = None
    ) -> bool:
        """Change user password with validation"""        try:
            # Verify old password
            verification = await self.verify_credentials(user_id, old_password)
            if not verification['verified']:
                raise ValueError("Current password is incorrect")
            
            # Validate new password
            validation_result = await self.validate_password_policy(new_password, user_id)
            if not validation_result['is_valid']:
                raise ValueError(f"New password policy violation: {', '.join(validation_result['errors'])}")
            
            # Check password history
            if await self._is_password_reused(user_id, new_password):
                raise ValueError("New password has been used recently and cannot be reused")
            
            # Deactivate old credentials
            stmt = select(UserCredentials).where(
                UserCredentials.user_id == user_id,
                UserCredentials.credential_type == CredentialType.PASSWORD.value,
                UserCredentials.is_active == True
            )
            result = await self.session.execute(stmt)
            old_credentials = result.scalars().all()
            
            for old_cred in old_credentials:
                old_cred.is_active = False
            
            # Create new credentials
            await self.create_credentials(
                user_id=user_id,
                password=new_password,
                metadata=metadata
            )
            
            logger.info(f"Password changed successfully for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Password change failed for user {user_id}: {e}")
            raise
    
    async def validate_password_policy(self, password: str, user_id: str) -> Dict[str, Any]:
        """Validate password against security policy"""        errors = []
        
        # Length checks
        if len(password) < self.policy.min_length:
            errors.append(f"Password must be at least {self.policy.min_length} characters long")
        
        if len(password) > self.policy.max_length:
            errors.append(f"Password must not exceed {self.policy.max_length} characters")
        
        # Character composition checks
        if self.policy.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.policy.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.policy.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if self.policy.require_special_chars:
            special_chars = set(string.punctuation)
            special_count = sum(1 for c in password if c in special_chars)
            if special_count < self.policy.min_special_chars:
                errors.append(f"Password must contain at least {self.policy.min_special_chars} special characters")
        
        # Entropy and strength analysis
        strength_analysis = zxcvbn.zxcvbn(password)
        if strength_analysis['score'] < self.policy.min_entropy_score:
            errors.append(f"Password is too weak (score: {strength_analysis['score']}/{self.policy.min_entropy_score})")
            if strength_analysis['feedback']['suggestions']:
                errors.extend(strength_analysis['feedback']['suggestions'])
        
        # Check for personal information (simplified)
        if self.policy.require_non_dictionary:
            if any(part.lower() in password.lower() for part in [user_id, user_id.split('@')[0]]):
                errors.append("Password should not contain personal information")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'strength_score': strength_analysis['score'],
            'entropy_bits': strength_analysis['guesses_log10'],
            'feedback': strength_analysis['feedback']
        }
    
    async def setup_security_questions(
        self,
        user_id: str,
        questions_and_answers: List[Tuple[str, str]]
    ) -> bool:
        """Setup security questions for account recovery"""        try:
            if len(questions_and_answers) < 3:
                raise ValueError("At least 3 security questions are required")
            
            # Deactivate existing questions
            stmt = select(SecurityQuestions).where(
                SecurityQuestions.user_id == user_id,
                SecurityQuestions.is_active == True
            )
            result = await self.session.execute(stmt)
            existing_questions = result.scalars().all()
            
            for question in existing_questions:
                question.is_active = False
            
            # Create new security questions
            for question_text, answer in questions_and_answers:
                salt = secrets.token_hex(32)
                answer_hash = self.pwd_context.hash(answer.lower().strip() + salt)
                
                security_question = SecurityQuestions(
                    question_id=str(uuid4()),
                    user_id=user_id,
                    question_type="custom",
                    question_text=question_text,
                    answer_hash=answer_hash,
                    salt=salt
                )
                
                self.session.add(security_question)
            
            # Update account security
            await self._update_account_security(user_id, security_questions_set=True)
            
            await self.session.commit()
            
            logger.info(f"Security questions setup completed for user {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to setup security questions for user {user_id}: {e}")
            raise
    
    async def generate_recovery_codes(self, user_id: str, count: int = 10) -> List[str]:
        """Generate backup recovery codes"""        try:
            recovery_codes = []
            
            for _ in range(count):
                # Generate a secure random code
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                recovery_codes.append(code)
            
            # Hash and store codes
            hashed_codes = []
            for code in recovery_codes:
                salt = secrets.token_hex(16)
                code_hash = self.pwd_context.hash(code + salt)
                hashed_codes.append({'hash': code_hash, 'salt': salt, 'used': False})
            
            # Update account security with backup codes
            stmt = select(AccountSecurity).where(AccountSecurity.user_id == user_id)
            result = await self.session.execute(stmt)
            account_security = result.scalar_one_or_none()
            
            if account_security:
                account_security.two_factor_backup_codes = hashed_codes
                account_security.updated_at = datetime.now(timezone.utc)
            else:
                account_security = AccountSecurity(
                    security_id=str(uuid4()),
                    user_id=user_id,
                    two_factor_backup_codes=hashed_codes
                )
                self.session.add(account_security)
            
            await self.session.commit()
            
            logger.info(f"Recovery codes generated for user {user_id}")
            return recovery_codes
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to generate recovery codes for user {user_id}: {e}")
            raise
    
    # Private helper methods
    
    async def _is_password_reused(self, user_id: str, password: str) -> bool:
        """Check if password was recently used"""        try:
            stmt = select(PasswordHistory).where(
                PasswordHistory.user_id == user_id
            ).order_by(PasswordHistory.created_at.desc()).limit(self.policy.password_history_count)
            
            result = await self.session.execute(stmt)
            history = result.scalars().all()
            
            for entry in history:
                if self.pwd_context.verify(password + entry.salt, entry.password_hash):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check password reuse: {e}")
            return False
    
    async def _add_to_password_history(
        self,
        user_id: str,
        password_hash: str,
        salt: str,
        changed_from_ip: Optional[str] = None,
        changed_reason: str = ""
    ):
        """Add password to history"""        history_entry = PasswordHistory(
            history_id=str(uuid4()),
            user_id=user_id,
            password_hash=password_hash,
            salt=salt,
            algorithm="scrypt",
            changed_from_ip=changed_from_ip,
            changed_reason=changed_reason
        )
        
        self.session.add(history_entry)
    
    def _determine_security_level(self, strength_score: int) -> SecurityLevel:
        """Determine security level based on password strength"""        if strength_score >= 4:
            return SecurityLevel.ULTRA
        elif strength_score >= 3:
            return SecurityLevel.HIGH
        elif strength_score >= 2:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
    
    async def _check_account_status(self, user_id: str) -> Dict[str, Any]:
        """Check if account can authenticate"""        try:
            stmt = select(AccountSecurity).where(AccountSecurity.user_id == user_id)
            result = await self.session.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                return {'can_authenticate': True}
            
            # Check if account is locked
            if account.lockout_until and account.lockout_until > datetime.now(timezone.utc):
                return {
                    'can_authenticate': False,
                    'reason': 'Account is locked due to failed login attempts',
                    'lockout_until': account.lockout_until
                }
            
            # Check account status
            if account.account_status != AccountStatus.ACTIVE.value:
                return {
                    'can_authenticate': False,
                    'reason': f'Account status: {account.account_status}'
                }
            
            return {'can_authenticate': True}
            
        except Exception as e:
            logger.error(f"Failed to check account status: {e}")
            return {'can_authenticate': False, 'reason': 'System error'}
    
    async def _record_failed_attempt(self, user_id: str, reason: str):
        """Record failed authentication attempt"""        try:
            stmt = select(AccountSecurity).where(AccountSecurity.user_id == user_id)
            result = await self.session.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                account = AccountSecurity(
                    security_id=str(uuid4()),
                    user_id=user_id
                )
                self.session.add(account)
            
            account.failed_login_attempts += 1
            account.last_failed_login = datetime.now(timezone.utc)
            
            # Check if account should be locked
            if account.failed_login_attempts >= self.policy.max_failed_attempts:
                account.lockout_until = datetime.now(timezone.utc) + timedelta(
                    minutes=self.policy.lockout_duration_minutes
                )
                account.account_status = AccountStatus.LOCKED.value
            
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to record failed attempt: {e}")
    
    async def _record_successful_authentication(self, user_id: str, credential_id: str):
        """Record successful authentication"""        try:
            # Reset failed attempts
            stmt = select(AccountSecurity).where(AccountSecurity.user_id == user_id)
            result = await self.session.execute(stmt)
            account = result.scalar_one_or_none()
            
            if account:
                account.failed_login_attempts = 0
                account.last_successful_login = datetime.now(timezone.utc)
                account.lockout_until = None
                if account.account_status == AccountStatus.LOCKED.value:
                    account.account_status = AccountStatus.ACTIVE.value
            
            # Update credential last use
            stmt = select(UserCredentials).where(UserCredentials.credential_id == credential_id)
            result = await self.session.execute(stmt)
            credential = result.scalar_one_or_none()
            
            if credential:
                credential.last_successful_use = datetime.now(timezone.utc)
                credential.failed_attempts = 0
            
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to record successful authentication: {e}")
    
    async def _update_account_security(
        self,
        user_id: str,
        last_password_change: bool = False,
        security_questions_set: bool = False
    ):
        """Update account security settings"""        try:
            stmt = select(AccountSecurity).where(AccountSecurity.user_id == user_id)
            result = await self.session.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                account = AccountSecurity(
                    security_id=str(uuid4()),
                    user_id=user_id
                )
                self.session.add(account)
            
            if last_password_change:
                account.last_password_change = datetime.now(timezone.utc)
                account.password_change_required = False
            
            if security_questions_set:
                account.security_questions_set = True
            
            account.updated_at = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Failed to update account security: {e}")

# Export the main classes
__all__ = [
    'UserCredentialsRepository',
    'UserCredentials',
    'PasswordHistory',
    'SecurityQuestions',
    'AccountSecurity',
    'CredentialType',
    'SecurityLevel',
    'AccountStatus',
    'PasswordPolicy',
    'SecurityQuestion',
    'CredentialMetadata'
]
