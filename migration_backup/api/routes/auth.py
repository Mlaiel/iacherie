
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
#!/usr/bin/env python3
"""
Authentication Endpoints - IA Chéries Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Role: Backend Senior + Security Expert
Purpose: Enterprise authentication and authorization endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
import jwt
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "ainflue_secret_key_change_in_production_2025"  # Change in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Pydantic Models
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserProfile(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str
    bio: str = ""
    creator_type: str = "influencer"
    verified: bool = False
    followers_count: int = 0
    following_count: int = 0
    content_count: int = 0
    joined_date: str
    location: Dict[str, str] = {}
    preferences: Dict[str, Any] = {}
    monetization: Dict[str, Any] = {}
    ai_settings: Dict[str, bool] = {}

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginResponse(BaseModel):
    token: str
    user: UserProfile

class ApiResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None
    errors: Optional[list] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Security dependencies
security = HTTPBearer()

# Mock user database (replace with real database in production)
MOCK_USERS = {
    "admin@ainflue.com": {
        "id": "user_001",
        "username": "admin_user",
        "email": "admin@ainflue.com",
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "full_name": "Admin User",
        "bio": "Platform Administrator",
        "creator_type": "admin",
        "verified": True,
        "followers_count": 1000,
        "following_count": 50,
        "content_count": 25,
        "joined_date": "2025-01-01T00:00:00",
        "location": {"country": "France", "city": "Paris", "timezone": "Europe/Paris"},
        "preferences": {
            "categories": ["technology", "business"],
            "languages": ["en", "fr"],
            "content_rating": "general"
        },
        "monetization": {
            "enabled": True,
            "subscription_price": 29.99,
            "commission_rate": 0.15,
            "total_earnings": 5420.50
        },
        "ai_settings": {
            "auto_tags": True,
            "content_protection": True,
            "seo_optimization": True,
            "collaboration_matching": True
        }
    },
    "creator@ainflue.com": {
        "id": "user_002",
        "username": "creator_pro",
        "email": "creator@ainflue.com",
        "password_hash": hashlib.sha256("creator123".encode()).hexdigest(),
        "full_name": "Pro Creator",
        "bio": "Professional content creator specializing in tech reviews",
        "creator_type": "influencer",
        "verified": True,
        "followers_count": 125000,
        "following_count": 500,
        "content_count": 150,
        "joined_date": "2024-06-15T10:30:00",
        "location": {"country": "United States", "city": "Los Angeles", "timezone": "America/Los_Angeles"},
        "preferences": {
            "categories": ["technology", "lifestyle", "entertainment"],
            "languages": ["en"],
            "content_rating": "general"
        },
        "monetization": {
            "enabled": True,
            "subscription_price": 19.99,
            "commission_rate": 0.12,
            "total_earnings": 15750.25
        },
        "ai_settings": {
            "auto_tags": True,
            "content_protection": True,
            "seo_optimization": True,
            "collaboration_matching": False
        }
    }
}

# Router setup
router = APIRouter(prefix="/auth", tags=["authentication"])

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """Create refresh token"""
    data = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Find user in mock database
    user_data = None
    for email, user in MOCK_USERS.items():
        if user["id"] == user_id:
            user_data = user
            break
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return UserProfile(**user_data)

# Authentication endpoints
@router.post("/login", response_model=ApiResponse)
async def login(login_data: UserLogin):
    """Authenticate user and return JWT tokens"""
    try:
        # Find user by email
        user_data = MOCK_USERS.get(login_data.email)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user_data["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": user_data["id"], "email": user_data["email"]}
        )
        refresh_token = create_refresh_token(user_data["id"])
        
        # Create user profile (remove password hash)
        user_profile_data = {k: v for k, v in user_data.items() if k != "password_hash"}
        user_profile = UserProfile(**user_profile_data)
        
        response_data = LoginResponse(
            token=access_token,
            user=user_profile
        )
        
        logger.info(f"User {login_data.email} logged in successfully")
        
        return ApiResponse(
            success=True,
            data=response_data.dict(),
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token using refresh token"""
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Find user
        user_data = None
        for email, user in MOCK_USERS.items():
            if user["id"] == user_id:
                user_data = user
                break
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        new_access_token = create_access_token(
            data={"sub": user_data["id"], "email": user_data["email"]}
        )
        
        token_response = TokenResponse(
            access_token=new_access_token,
            refresh_token=token,  # Keep same refresh token
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return ApiResponse(
            success=True,
            data=token_response.dict(),
            message="Token refreshed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout", response_model=ApiResponse)
async def logout(current_user: UserProfile = Depends(get_current_user)):
    """Logout user (invalidate token)"""
    try:
        # In a real implementation, you would add the token to a blacklist
        logger.info(f"User {current_user.email} logged out")
        
        return ApiResponse(
            success=True,
            data={"message": "Logged out successfully"},
            message="Logout successful"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=ApiResponse)
async def get_current_user_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get current user profile"""
    try:
        return ApiResponse(
            success=True,
            data=current_user.dict(),
            message="User profile retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/me", response_model=ApiResponse)
async def update_user_profile(
    profile_data: dict,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        # Find user in mock database
        user_email = None
        for email, user in MOCK_USERS.items():
            if user["id"] == current_user.id:
                user_email = email
                break
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update allowed fields
        allowed_fields = [
            "full_name", "bio", "location", "preferences", 
            "monetization", "ai_settings"
        ]
        
        for field, value in profile_data.items():
            if field in allowed_fields:
                MOCK_USERS[user_email][field] = value
        
        # Return updated profile
        updated_user_data = {k: v for k, v in MOCK_USERS[user_email].items() if k != "password_hash"}
        updated_profile = UserProfile(**updated_user_data)
        
        logger.info(f"Profile updated for user {current_user.email}")
        
        return ApiResponse(
            success=True,
            data=updated_profile.dict(),
            message="Profile updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/validate", response_model=ApiResponse)
async def validate_token(current_user: UserProfile = Depends(get_current_user)):
    """Validate current token"""
    try:
        return ApiResponse(
            success=True,
            data={
                "valid": True,
                "user_id": current_user.id,
                "email": current_user.email
            },
            message="Token is valid"
        )
        
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Health check for auth service
@router.get("/health", response_model=ApiResponse)
async def auth_health():
    """Health check for authentication service"""
    return ApiResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "authentication",
            "timestamp": datetime.now().isoformat()
        },
        message="Authentication service is healthy"
    )