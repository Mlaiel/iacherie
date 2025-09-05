"""
Authentication Routes - Enterprise Security & Identity Management
Advanced authentication with JWT, OAuth2, 2FA, RBAC, and session management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
import secrets
import hashlib
import re

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, validator
import jwt
import bcrypt

# Enterprise Security
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Authentication failed"}}
)

# ========================================
# CONSTANTS & CONFIGURATION
# ========================================

SECRET_KEY = "ainflue_enterprise_secret_key_2025"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_EXPIRE_HOURS = 2

# ========================================
# ENUMS
# ========================================

class UserRole(str, Enum):
    ADMIN = "admin"
    CREATOR = "creator"
    MODERATOR = "moderator"
    VIEWER = "viewer"
    ENTERPRISE_USER = "enterprise_user"
    API_USER = "api_user"

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"

class AuthMethod(str, Enum):
    EMAIL_PASSWORD = "email_password"
    GOOGLE_OAUTH = "google_oauth"
    MICROSOFT_OAUTH = "microsoft_oauth"
    GITHUB_OAUTH = "github_oauth"
    API_KEY = "api_key"
    SSO_SAML = "sso_saml"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"

class TwoFactorMethod(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    TOTP = "totp"
    BACKUP_CODES = "backup_codes"

# ========================================
# PYDANTIC MODELS
# ========================================

class UserRegistration(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Strong password")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r'^\+?[1-9]\d{1,14}$')
    country: str = Field(..., min_length=2, max_length=2, description="ISO country code")
    preferred_language: str = Field(default="en", min_length=2, max_length=5)
    marketing_consent: bool = Field(default=False)
    terms_accepted: bool = Field(..., description="Must accept terms")
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('terms_accepted')
    def validate_terms(cls, v):
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False)
    captcha_token: Optional[str] = Field(None, description="CAPTCHA verification token")
    device_fingerprint: Optional[str] = Field(None, description="Device fingerprint for security")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user_id: str
    email: str
    role: UserRole
    subscription_tier: SubscriptionTier
    requires_2fa: bool = Field(default=False)
    session_id: str

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    country: str
    preferred_language: str
    role: UserRole
    subscription_tier: SubscriptionTier
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    two_factor_enabled: bool = Field(default=False)
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    permissions: List[str] = Field(default_factory=list)
    api_quota: Dict[str, int] = Field(default_factory=dict)
    storage_quota_gb: int = Field(default=10)

class PasswordChange(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class PasswordReset(BaseModel):
    email: EmailStr = Field(..., description="Email address for password reset")
    captcha_token: Optional[str] = Field(None)

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class TwoFactorSetup(BaseModel):
    method: TwoFactorMethod = Field(..., description="2FA method to setup")
    phone_number: Optional[str] = Field(None, description="Phone number for SMS 2FA")
    backup_email: Optional[EmailStr] = Field(None, description="Backup email for email 2FA")

class TwoFactorVerification(BaseModel):
    token: str = Field(..., min_length=6, max_length=8, description="2FA verification code")
    method: TwoFactorMethod = Field(..., description="2FA method used")
    remember_device: bool = Field(default=False)

class OAuth2AuthRequest(BaseModel):
    provider: AuthMethod = Field(..., description="OAuth2 provider")
    authorization_code: str = Field(..., description="OAuth2 authorization code")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    state: Optional[str] = Field(None, description="CSRF protection state")

class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    device_info: Dict[str, str] = Field(default_factory=dict)
    ip_address: str
    user_agent: str
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_current: bool = Field(default=False)

class APIKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="API key name")
    description: Optional[str] = Field(None, max_length=500)
    permissions: List[str] = Field(..., min_items=1, description="API key permissions")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")

class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str = Field(..., description="API key (shown only once)")
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

# ========================================
# UTILITY FUNCTIONS
# ========================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# ========================================
# DEPENDENCY FUNCTIONS
# ========================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Extract current user from JWT token"""
    payload = verify_token(credentials.credentials)
    
    # In production, fetch from database
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role", "creator"),
        "subscription_tier": payload.get("subscription_tier", "free"),
        "permissions": payload.get("permissions", []),
        "session_id": payload.get("session_id")
    }

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current active user with additional checks"""
    # In production, check if user is active in database
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_role(required_role: UserRole):
    """Dependency to require specific user role"""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# ========================================
# AUTHENTICATION ENDPOINTS
# ========================================

@router.post("/register", response_model=UserProfile)
async def register_user(
    user_data: UserRegistration,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Register new user with comprehensive validation"""
    
    # Check if user already exists
    # In production, check database
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user profile
    user_id = str(uuid.uuid4())
    user_profile = UserProfile(
        id=user_id,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        company=user_data.company,
        phone=user_data.phone,
        country=user_data.country,
        preferred_language=user_data.preferred_language,
        role=UserRole.CREATOR,
        subscription_tier=SubscriptionTier.FREE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        permissions=["content:create", "content:read", "content:update", "content:delete"],
        api_quota={"requests_per_hour": 1000, "storage_gb": 10}
    )
    
    # Schedule background tasks
    background_tasks.add_task(send_verification_email, user_data.email, user_id)
    background_tasks.add_task(log_registration_event, user_id, request.client.host)
    
    return user_profile

@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Authenticate user and create session"""
    
    # In production, verify credentials against database
    # For demo, use mock verification
    
    if login_data.email == "demo@ainflue.com" and login_data.password == "DemoPassword123!":
        # Mock user data
        user_id = "user_demo_123"
        session_id = str(uuid.uuid4())
        
        # Create tokens
        token_data = {
            "sub": user_id,
            "email": login_data.email,
            "role": "creator",
            "subscription_tier": "enterprise",
            "session_id": session_id,
            "permissions": ["content:*", "collaboration:*", "analytics:*"]
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Schedule background tasks
        background_tasks.add_task(log_login_event, user_id, request.client.host)
        background_tasks.add_task(update_last_login, user_id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user_id,
            email=login_data.email,
            role=UserRole.CREATOR,
            subscription_tier=SubscriptionTier.ENTERPRISE,
            session_id=session_id
        )
    else:
        # Log failed attempt
        background_tasks.add_task(log_failed_login, login_data.email, request.client.host)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    background_tasks: BackgroundTasks,
    request: Request
):
    """OAuth2 compatible token endpoint"""
    
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    return await login_user(login_data, background_tasks, request)

@router.post("/logout")
async def logout_user(
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Logout user and invalidate session"""
    
    # In production, invalidate session in database/Redis
    background_tasks.add_task(invalidate_session, current_user["session_id"])
    background_tasks.add_task(log_logout_event, current_user["id"])
    
    return {
        "message": "Successfully logged out",
        "logged_out_at": datetime.utcnow()
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_token: str,
    background_tasks: BackgroundTasks
):
    """Refresh access token using refresh token"""
    
    payload = verify_token(refresh_token, "refresh")
    
    # Create new access token
    token_data = {
        "sub": payload["sub"],
        "email": payload["email"],
        "role": payload["role"],
        "subscription_tier": payload["subscription_tier"],
        "session_id": payload["session_id"],
        "permissions": payload["permissions"]
    }
    
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=payload["sub"],
        email=payload["email"],
        role=UserRole(payload["role"]),
        subscription_tier=SubscriptionTier(payload["subscription_tier"]),
        session_id=payload["session_id"]
    )

# ========================================
# USER PROFILE MANAGEMENT
# ========================================

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    
    # In production, fetch complete profile from database
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        first_name="Demo",
        last_name="User",
        display_name="Demo Creator",
        avatar_url="https://example.com/avatar.jpg",
        company="Ainflue Demo Corp",
        country="US",
        preferred_language="en",
        role=UserRole(current_user["role"]),
        subscription_tier=SubscriptionTier(current_user["subscription_tier"]),
        is_verified=True,
        is_active=True,
        two_factor_enabled=False,
        last_login=datetime.utcnow() - timedelta(minutes=30),
        created_at=datetime.utcnow() - timedelta(days=30),
        updated_at=datetime.utcnow() - timedelta(hours=2),
        permissions=current_user["permissions"],
        api_quota={"requests_per_hour": 10000, "storage_gb": 1000},
        storage_quota_gb=1000
    )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_updates: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Update user profile"""
    
    # In production, validate and update database
    background_tasks.add_task(log_profile_update, current_user["id"], profile_updates)
    
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        first_name=profile_updates.get("first_name", "Updated"),
        last_name=profile_updates.get("last_name", "User"),
        display_name=profile_updates.get("display_name"),
        company=profile_updates.get("company"),
        country=profile_updates.get("country", "US"),
        preferred_language=profile_updates.get("preferred_language", "en"),
        role=UserRole(current_user["role"]),
        subscription_tier=SubscriptionTier(current_user["subscription_tier"]),
        is_verified=True,
        is_active=True,
        two_factor_enabled=False,
        created_at=datetime.utcnow() - timedelta(days=30),
        updated_at=datetime.utcnow(),
        permissions=current_user["permissions"],
        api_quota={"requests_per_hour": 10000, "storage_gb": 1000},
        storage_quota_gb=1000
    )

# ========================================
# PASSWORD MANAGEMENT
# ========================================

@router.post("/password/change")
async def change_password(
    password_change: PasswordChange,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Change user password"""
    
    # In production, verify current password against database
    # Hash new password and update database
    
    background_tasks.add_task(log_password_change, current_user["id"])
    background_tasks.add_task(send_password_change_notification, current_user["email"])
    
    return {
        "message": "Password changed successfully",
        "changed_at": datetime.utcnow(),
        "requires_re_login": True
    }

@router.post("/password/reset")
async def request_password_reset(
    reset_request: PasswordReset,
    background_tasks: BackgroundTasks
):
    """Request password reset"""
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    
    # In production, store token in database with expiration
    background_tasks.add_task(send_password_reset_email, reset_request.email, reset_token)
    
    return {
        "message": "Password reset email sent if account exists",
        "sent_at": datetime.utcnow()
    }

@router.post("/password/reset/confirm")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    background_tasks: BackgroundTasks
):
    """Confirm password reset with token"""
    
    # In production, verify token from database
    # Hash new password and update database
    
    background_tasks.add_task(log_password_reset, reset_confirm.token)
    
    return {
        "message": "Password reset successfully",
        "reset_at": datetime.utcnow()
    }

# ========================================
# TWO-FACTOR AUTHENTICATION
# ========================================

@router.post("/2fa/setup")
async def setup_two_factor(
    setup_data: TwoFactorSetup,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Setup two-factor authentication"""
    
    if setup_data.method == TwoFactorMethod.TOTP:
        # Generate TOTP secret
        secret = secrets.token_hex(20)
        qr_code_url = f"otpauth://totp/Ainflue:{current_user['email']}?secret={secret}&issuer=Ainflue"
        
        background_tasks.add_task(log_2fa_setup, current_user["id"], setup_data.method)
        
        return {
            "method": setup_data.method,
            "secret": secret,
            "qr_code_url": qr_code_url,
            "backup_codes": [secrets.token_hex(4) for _ in range(10)]
        }
    
    elif setup_data.method == TwoFactorMethod.SMS:
        if not setup_data.phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number required for SMS 2FA"
            )
        
        verification_code = str(secrets.randbelow(1000000)).zfill(6)
        background_tasks.add_task(send_sms_verification, setup_data.phone_number, verification_code)
        
        return {
            "method": setup_data.method,
            "phone_number": setup_data.phone_number,
            "verification_sent": True
        }
    
    else:
        return {
            "method": setup_data.method,
            "setup_completed": True
        }

@router.post("/2fa/verify")
async def verify_two_factor(
    verification: TwoFactorVerification,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Verify two-factor authentication code"""
    
    # In production, verify code against stored secret/sent code
    background_tasks.add_task(log_2fa_verification, current_user["id"], verification.method)
    
    return {
        "verified": True,
        "method": verification.method,
        "verified_at": datetime.utcnow(),
        "device_remembered": verification.remember_device
    }

@router.post("/2fa/disable")
async def disable_two_factor(
    current_password: str,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Disable two-factor authentication"""
    
    # In production, verify password and disable 2FA
    background_tasks.add_task(log_2fa_disable, current_user["id"])
    
    return {
        "message": "Two-factor authentication disabled",
        "disabled_at": datetime.utcnow()
    }

# ========================================
# OAUTH2 & SOCIAL LOGIN
# ========================================

@router.post("/oauth2/authorize")
async def oauth2_authorize(
    auth_request: OAuth2AuthRequest,
    background_tasks: BackgroundTasks
):
    """Handle OAuth2 authorization"""
    
    # In production, exchange authorization code for tokens
    # with respective OAuth2 provider
    
    background_tasks.add_task(log_oauth_login, auth_request.provider)
    
    # Mock OAuth2 response
    user_id = f"oauth_{auth_request.provider.value}_{uuid.uuid4().hex[:8]}"
    token_data = {
        "sub": user_id,
        "email": "oauth.user@example.com",
        "role": "creator",
        "subscription_tier": "free",
        "session_id": str(uuid.uuid4()),
        "permissions": ["content:create", "content:read"]
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user_id,
        email="oauth.user@example.com",
        role=UserRole.CREATOR,
        subscription_tier=SubscriptionTier.FREE,
        session_id=token_data["session_id"]
    )

# ========================================
# SESSION MANAGEMENT
# ========================================

@router.get("/sessions", response_model=List[SessionInfo])
async def get_user_sessions(
    current_user: dict = Depends(get_current_user)
):
    """Get all active sessions for user"""
    
    # Mock session data
    return [
        SessionInfo(
            session_id=current_user["session_id"],
            user_id=current_user["id"],
            device_info={"device": "Chrome Browser", "os": "Windows 10"},
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            status=SessionStatus.ACTIVE,
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_activity=datetime.utcnow() - timedelta(minutes=5),
            expires_at=datetime.utcnow() + timedelta(days=7),
            is_current=True
        ),
        SessionInfo(
            session_id="session_mobile_456",
            user_id=current_user["id"],
            device_info={"device": "iPhone 14", "os": "iOS 17"},
            ip_address="192.168.1.101",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
            status=SessionStatus.ACTIVE,
            created_at=datetime.utcnow() - timedelta(days=1),
            last_activity=datetime.utcnow() - timedelta(hours=3),
            expires_at=datetime.utcnow() + timedelta(days=6),
            is_current=False
        )
    ]

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Revoke specific session"""
    
    background_tasks.add_task(invalidate_session, session_id)
    background_tasks.add_task(log_session_revocation, current_user["id"], session_id)
    
    return {
        "message": f"Session {session_id} revoked successfully",
        "revoked_at": datetime.utcnow()
    }

@router.delete("/sessions/all")
async def revoke_all_sessions(
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Revoke all user sessions except current"""
    
    background_tasks.add_task(invalidate_all_user_sessions, current_user["id"], current_user["session_id"])
    
    return {
        "message": "All other sessions revoked successfully",
        "revoked_at": datetime.utcnow(),
        "current_session_preserved": True
    }

# ========================================
# API KEY MANAGEMENT
# ========================================

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_request: APIKeyRequest,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Create new API key"""
    
    api_key = f"ak_{secrets.token_urlsafe(32)}"
    key_id = str(uuid.uuid4())
    
    background_tasks.add_task(log_api_key_creation, current_user["id"], key_id)
    
    return APIKeyResponse(
        id=key_id,
        name=key_request.name,
        key=api_key,
        permissions=key_request.permissions,
        created_at=datetime.utcnow(),
        expires_at=key_request.expires_at
    )

@router.get("/api-keys")
async def list_api_keys(
    current_user: dict = Depends(get_current_user)
):
    """List user's API keys (without showing the actual keys)"""
    
    # Mock API keys
    return [
        {
            "id": "key_001",
            "name": "Production API Key",
            "permissions": ["content:read", "analytics:read"],
            "created_at": datetime.utcnow() - timedelta(days=30),
            "last_used": datetime.utcnow() - timedelta(hours=2),
            "expires_at": None
        },
        {
            "id": "key_002",
            "name": "Development Key",
            "permissions": ["content:*"],
            "created_at": datetime.utcnow() - timedelta(days=7),
            "last_used": datetime.utcnow() - timedelta(minutes=30),
            "expires_at": datetime.utcnow() + timedelta(days=90)
        }
    ]

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """Revoke API key"""
    
    background_tasks.add_task(log_api_key_revocation, current_user["id"], key_id)
    
    return {
        "message": f"API key {key_id} revoked successfully",
        "revoked_at": datetime.utcnow()
    }

# ========================================
# VERIFICATION & SECURITY
# ========================================

@router.post("/verify-email")
async def verify_email(
    verification_token: str,
    background_tasks: BackgroundTasks
):
    """Verify email address"""
    
    # In production, verify token and mark email as verified
    background_tasks.add_task(log_email_verification, verification_token)
    
    return {
        "message": "Email verified successfully",
        "verified_at": datetime.utcnow()
    }

@router.post("/resend-verification")
async def resend_verification_email(
    email: EmailStr,
    background_tasks: BackgroundTasks
):
    """Resend email verification"""
    
    verification_token = secrets.token_urlsafe(32)
    background_tasks.add_task(send_verification_email, email, verification_token)
    
    return {
        "message": "Verification email sent if account exists",
        "sent_at": datetime.utcnow()
    }

@router.get("/permissions")
async def get_user_permissions(
    current_user: dict = Depends(get_current_user)
):
    """Get user permissions"""
    
    return {
        "user_id": current_user["id"],
        "role": current_user["role"],
        "permissions": current_user["permissions"],
        "subscription_tier": current_user["subscription_tier"],
        "api_quota": {
            "requests_per_hour": 10000,
            "requests_used_this_hour": 150,
            "storage_gb": 1000,
            "storage_used_gb": 234.5
        }
    }

# ========================================
# BACKGROUND TASKS
# ========================================

async def send_verification_email(email: str, user_id: str):
    """Send email verification"""
    await asyncio.sleep(1)
    print(f"Verification email sent to {email} for user {user_id}")

async def log_registration_event(user_id: str, ip_address: str):
    """Log user registration"""
    await asyncio.sleep(0.5)
    print(f"User {user_id} registered from {ip_address}")

async def log_login_event(user_id: str, ip_address: str):
    """Log successful login"""
    await asyncio.sleep(0.5)
    print(f"User {user_id} logged in from {ip_address}")

async def log_failed_login(email: str, ip_address: str):
    """Log failed login attempt"""
    await asyncio.sleep(0.5)
    print(f"Failed login attempt for {email} from {ip_address}")

async def update_last_login(user_id: str):
    """Update last login timestamp"""
    await asyncio.sleep(0.5)
    print(f"Updated last login for user {user_id}")

async def invalidate_session(session_id: str):
    """Invalidate session"""
    await asyncio.sleep(0.5)
    print(f"Session {session_id} invalidated")

async def log_logout_event(user_id: str):
    """Log user logout"""
    await asyncio.sleep(0.5)
    print(f"User {user_id} logged out")

async def log_profile_update(user_id: str, updates: Dict[str, Any]):
    """Log profile update"""
    await asyncio.sleep(0.5)
    print(f"Profile updated for user {user_id}: {list(updates.keys())}")

async def log_password_change(user_id: str):
    """Log password change"""
    await asyncio.sleep(0.5)
    print(f"Password changed for user {user_id}")

async def send_password_change_notification(email: str):
    """Send password change notification"""
    await asyncio.sleep(1)
    print(f"Password change notification sent to {email}")

async def send_password_reset_email(email: str, token: str):
    """Send password reset email"""
    await asyncio.sleep(1)
    print(f"Password reset email sent to {email} with token {token[:8]}...")

async def log_password_reset(token: str):
    """Log password reset"""
    await asyncio.sleep(0.5)
    print(f"Password reset completed with token {token[:8]}...")

async def log_2fa_setup(user_id: str, method: TwoFactorMethod):
    """Log 2FA setup"""
    await asyncio.sleep(0.5)
    print(f"2FA setup for user {user_id} with method {method}")

async def send_sms_verification(phone: str, code: str):
    """Send SMS verification"""
    await asyncio.sleep(1)
    print(f"SMS verification sent to {phone} with code {code}")

async def log_2fa_verification(user_id: str, method: TwoFactorMethod):
    """Log 2FA verification"""
    await asyncio.sleep(0.5)
    print(f"2FA verified for user {user_id} with method {method}")

async def log_2fa_disable(user_id: str):
    """Log 2FA disable"""
    await asyncio.sleep(0.5)
    print(f"2FA disabled for user {user_id}")

async def log_oauth_login(provider: AuthMethod):
    """Log OAuth login"""
    await asyncio.sleep(0.5)
    print(f"OAuth login with provider {provider}")

async def invalidate_all_user_sessions(user_id: str, exclude_session: str):
    """Invalidate all user sessions except one"""
    await asyncio.sleep(1)
    print(f"All sessions invalidated for user {user_id} except {exclude_session}")

async def log_session_revocation(user_id: str, session_id: str):
    """Log session revocation"""
    await asyncio.sleep(0.5)
    print(f"Session {session_id} revoked for user {user_id}")

async def log_api_key_creation(user_id: str, key_id: str):
    """Log API key creation"""
    await asyncio.sleep(0.5)
    print(f"API key {key_id} created for user {user_id}")

async def log_api_key_revocation(user_id: str, key_id: str):
    """Log API key revocation"""
    await asyncio.sleep(0.5)
    print(f"API key {key_id} revoked for user {user_id}")

async def log_email_verification(token: str):
    """Log email verification"""
    await asyncio.sleep(0.5)
    print(f"Email verified with token {token[:8]}...")

__all__ = ["router"]
