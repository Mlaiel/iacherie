"""Enhanced 2FA Enforcement System
===============================

Mandatory 2FA enforcement for admin accounts with grace period,
backup codes, and comprehensive audit trail.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import secrets
import qrcode
import pyotp
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from config.security.production_security import TwoFactorAuthConfig, get_security_config


logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User role classifications"""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SECURITY_ADMIN = "security_admin" 
    SYSTEM_ADMIN = "system_admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class User2FAStatus:
    """User 2FA status and configuration"""
    user_id: str
    email: str
    role: UserRole
    is_2fa_enabled: bool
    is_2fa_enforced: bool
    secret: Optional[str]
    backup_codes: List[str] = field(default_factory=list)
    enrollment_deadline: Optional[datetime] = None
    last_2fa_verification: Optional[datetime] = None
    failed_attempts: int = 0
    is_locked_out: bool = False
    lockout_until: Optional[datetime] = None


@dataclass 
class TwoFactorAuthResult:
    """2FA authentication result"""
    success: bool
    user_id: str
    method: str  # totp, backup_code
    remaining_attempts: Optional[int] = None
    lockout_until: Optional[datetime] = None
    error_message: Optional[str] = None


class Enhanced2FAManager:
    """Enhanced 2FA manager with mandatory enforcement"""
    
    def __init__(self, config: Optional[TwoFactorAuthConfig] = None):
        self.config = config or get_security_config().two_factor_auth
        self.users_2fa_status: Dict[str, User2FAStatus] = {}
        
    def _is_privileged_role(self, role: UserRole) -> bool:
        """Check if role requires mandatory 2FA"""
        privileged_roles = {
            UserRole.ADMIN,
            UserRole.SECURITY_ADMIN,
            UserRole.SYSTEM_ADMIN,
            UserRole.SUPER_ADMIN
        }
        return role in privileged_roles
    
    def _calculate_enrollment_deadline(self) -> datetime:
        """Calculate 2FA enrollment deadline"""
        return datetime.utcnow() + timedelta(days=self.config.grace_period_days)
    
    def _generate_backup_codes(self, count: int = None) -> List[str]:
        """Generate backup codes for 2FA"""
        count = count or self.config.backup_codes_count
        return [secrets.token_hex(8).upper() for _ in range(count)]
    
    def generate_2fa_secret(self) -> str:
        """Generate new 2FA secret"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, user_email: str) -> bytes:
        """Generate QR code for 2FA setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            user_email,
            issuer_name="Ainflue Platform"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    async def register_user(
        self,
        user_id: str,
        email: str,
        role: UserRole
    ) -> User2FAStatus:
        """Register user and determine 2FA requirements"""
        # Check if 2FA is enforced for this role
        is_enforced = (
            self.config.mandatory_for_admin and self._is_privileged_role(role)
        ) or (
            self.config.mandatory_for_privileged and role != UserRole.USER
        )
        
        status = User2FAStatus(
            user_id=user_id,
            email=email,
            role=role,
            is_2fa_enabled=False,
            is_2fa_enforced=is_enforced,
            secret=None,
            enrollment_deadline=self._calculate_enrollment_deadline() if is_enforced else None
        )
        
        self.users_2fa_status[user_id] = status
        
        if is_enforced:
            logger.info(f"User {user_id} ({role.value}) enrolled with mandatory 2FA. Deadline: {status.enrollment_deadline}")
        
        return status
    
    async def initiate_2fa_setup(self, user_id: str) -> Dict[str, Any]:
        """Initiate 2FA setup for user"""
        if user_id not in self.users_2fa_status:
            raise ValueError(f"User {user_id} not registered")
        
        status = self.users_2fa_status[user_id]
        
        # Generate new secret and backup codes
        secret = self.generate_2fa_secret()
        backup_codes = self._generate_backup_codes()
        
        # Store temporarily (should be persisted in real implementation)
        status.secret = secret
        status.backup_codes = backup_codes
        
        # Generate QR code
        qr_code = self.generate_qr_code(secret, status.email)
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "setup_instructions": [
                "1. Install an authenticator app (Google Authenticator, Authy, etc.)",
                "2. Scan the QR code or enter the secret manually",
                "3. Enter the 6-digit code from your app to verify setup",
                "4. Save your backup codes in a secure location"
            ]
        }
    
    async def verify_2fa_setup(self, user_id: str, token: str) -> bool:
        """Verify 2FA setup with initial token"""
        if user_id not in self.users_2fa_status:
            return False
        
        status = self.users_2fa_status[user_id]
        
        if not status.secret:
            return False
        
        # Verify TOTP token
        totp = pyotp.TOTP(status.secret)
        if totp.verify(token, valid_window=self.config.totp_window):
            # Enable 2FA for user
            status.is_2fa_enabled = True
            status.last_2fa_verification = datetime.utcnow()
            
            logger.info(f"2FA setup completed for user {user_id}")
            return True
        
        return False
    
    async def authenticate_2fa(self, user_id: str, token: str) -> TwoFactorAuthResult:
        """Authenticate user with 2FA token"""
        if user_id not in self.users_2fa_status:
            return TwoFactorAuthResult(
                success=False,
                user_id=user_id,
                method="unknown",
                error_message="User not found"
            )
        
        status = self.users_2fa_status[user_id]
        
        # Check if user is locked out
        if status.is_locked_out and status.lockout_until:
            if datetime.utcnow() < status.lockout_until:
                return TwoFactorAuthResult(
                    success=False,
                    user_id=user_id,
                    method="lockout",
                    lockout_until=status.lockout_until,
                    error_message="Account temporarily locked due to failed 2FA attempts"
                )
            else:
                # Reset lockout
                status.is_locked_out = False
                status.lockout_until = None
                status.failed_attempts = 0
        
        # Try TOTP first
        if status.secret:
            totp = pyotp.TOTP(status.secret)
            if totp.verify(token, valid_window=self.config.totp_window):
                status.last_2fa_verification = datetime.utcnow()
                status.failed_attempts = 0
                return TwoFactorAuthResult(
                    success=True,
                    user_id=user_id,
                    method="totp"
                )
        
        # Try backup codes
        if token.upper() in status.backup_codes:
            # Remove used backup code
            status.backup_codes.remove(token.upper())
            status.last_2fa_verification = datetime.utcnow()
            status.failed_attempts = 0
            
            return TwoFactorAuthResult(
                success=True,
                user_id=user_id,
                method="backup_code",
                remaining_attempts=len(status.backup_codes)
            )
        
        # Failed attempt
        status.failed_attempts += 1
        
        # Check for lockout
        if status.failed_attempts >= 5:  # Configurable threshold
            status.is_locked_out = True
            status.lockout_until = datetime.utcnow() + timedelta(minutes=15)
            
            logger.warning(f"User {user_id} locked out due to failed 2FA attempts")
            
            return TwoFactorAuthResult(
                success=False,
                user_id=user_id,
                method="failed",
                lockout_until=status.lockout_until,
                error_message="Too many failed attempts. Account locked for 15 minutes."
            )
        
        return TwoFactorAuthResult(
            success=False,
            user_id=user_id,
            method="failed",
            remaining_attempts=5 - status.failed_attempts,
            error_message="Invalid 2FA token"
        )
    
    async def check_2fa_enforcement(self, user_id: str) -> Dict[str, Any]:
        """Check 2FA enforcement status for user"""
        if user_id not in self.users_2fa_status:
            return {"status": "unknown", "message": "User not found"}
        
        status = self.users_2fa_status[user_id]
        
        if not status.is_2fa_enforced:
            return {
                "status": "not_required",
                "message": "2FA not required for this user role"
            }
        
        if status.is_2fa_enabled:
            return {
                "status": "compliant",
                "message": "2FA is enabled and compliant"
            }
        
        # Check grace period
        if status.enrollment_deadline:
            now = datetime.utcnow()
            if now > status.enrollment_deadline:
                return {
                    "status": "overdue",
                    "message": "2FA enrollment is overdue. Access will be restricted.",
                    "days_overdue": (now - status.enrollment_deadline).days
                }
            else:
                days_remaining = (status.enrollment_deadline - now).days
                return {
                    "status": "grace_period",
                    "message": f"2FA must be enabled within {days_remaining} days",
                    "days_remaining": days_remaining,
                    "deadline": status.enrollment_deadline.isoformat()
                }
        
        return {
            "status": "required",
            "message": "2FA setup is required for this account"
        }
    
    async def get_users_requiring_2fa(self) -> List[Dict[str, Any]]:
        """Get list of users requiring 2FA setup"""
        requiring_2fa = []
        
        for user_id, status in self.users_2fa_status.items():
            if status.is_2fa_enforced and not status.is_2fa_enabled:
                enforcement_check = await self.check_2fa_enforcement(user_id)
                requiring_2fa.append({
                    "user_id": user_id,
                    "email": status.email,
                    "role": status.role.value,
                    "enforcement_status": enforcement_check["status"],
                    "deadline": status.enrollment_deadline.isoformat() if status.enrollment_deadline else None
                })
        
        return requiring_2fa
    
    async def generate_new_backup_codes(self, user_id: str) -> List[str]:
        """Generate new backup codes for user"""
        if user_id not in self.users_2fa_status:
            raise ValueError(f"User {user_id} not found")
        
        status = self.users_2fa_status[user_id]
        if not status.is_2fa_enabled:
            raise ValueError("2FA not enabled for user")
        
        # Generate new backup codes
        new_codes = self._generate_backup_codes()
        status.backup_codes = new_codes
        
        logger.info(f"Generated new backup codes for user {user_id}")
        return new_codes
    
    async def disable_2fa(self, user_id: str, admin_override: bool = False) -> bool:
        """Disable 2FA for user (admin function)"""
        if user_id not in self.users_2fa_status:
            return False
        
        status = self.users_2fa_status[user_id]
        
        # Check if 2FA is enforced
        if status.is_2fa_enforced and not admin_override:
            raise ValueError("Cannot disable 2FA for enforced accounts without admin override")
        
        status.is_2fa_enabled = False
        status.secret = None
        status.backup_codes = []
        
        logger.warning(f"2FA disabled for user {user_id} (admin override: {admin_override})")
        return True
    
    async def get_2fa_stats(self) -> Dict[str, Any]:
        """Get 2FA statistics and compliance report"""
        total_users = len(self.users_2fa_status)
        enforced_users = sum(1 for s in self.users_2fa_status.values() if s.is_2fa_enforced)
        enabled_users = sum(1 for s in self.users_2fa_status.values() if s.is_2fa_enabled)
        overdue_users = sum(
            1 for s in self.users_2fa_status.values() 
            if s.is_2fa_enforced and not s.is_2fa_enabled and 
            s.enrollment_deadline and datetime.utcnow() > s.enrollment_deadline
        )
        
        compliance_rate = (enabled_users / enforced_users * 100) if enforced_users > 0 else 100
        
        return {
            "total_users": total_users,
            "enforced_users": enforced_users,
            "enabled_users": enabled_users,
            "overdue_users": overdue_users,
            "compliance_rate": round(compliance_rate, 2),
            "grace_period_days": self.config.grace_period_days,
            "admin_enforcement": self.config.mandatory_for_admin,
            "privileged_enforcement": self.config.mandatory_for_privileged
        }


# Global 2FA manager instance
_2fa_manager_instance: Optional[Enhanced2FAManager] = None

def get_2fa_manager() -> Enhanced2FAManager:
    """Get global 2FA manager instance"""
    global _2fa_manager_instance
    if _2fa_manager_instance is None:
        _2fa_manager_instance = Enhanced2FAManager()
    return _2fa_manager_instance


async def enforce_2fa_for_user(user_id: str, email: str, role: str) -> Dict[str, Any]:
    """Enforce 2FA for user (main entry point)"""
    manager = get_2fa_manager()
    user_role = UserRole(role.lower())
    
    # Register user
    status = await manager.register_user(user_id, email, user_role)
    
    # Check enforcement
    enforcement = await manager.check_2fa_enforcement(user_id)
    
    return {
        "user_id": user_id,
        "2fa_enforced": status.is_2fa_enforced,
        "2fa_enabled": status.is_2fa_enabled,
        "enforcement_status": enforcement,
        "enrollment_deadline": status.enrollment_deadline.isoformat() if status.enrollment_deadline else None
    }


if __name__ == "__main__":
    async def main():
        # Test 2FA enforcement
        manager = Enhanced2FAManager()
        
        # Register admin user
        await manager.register_user("admin1", "admin@ainflue.com", UserRole.ADMIN)
        
        # Check enforcement
        enforcement = await manager.check_2fa_enforcement("admin1")
        print(f"Admin enforcement: {enforcement}")
        
        # Get stats
        stats = await manager.get_2fa_stats()
        print(f"2FA stats: {stats}")
    
    asyncio.run(main())