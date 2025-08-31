"""Authentication API Routes
User authentication, registration, and authorization endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
import bcrypt

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger


# Pydantic models for request/response
class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    creator_type: str = Field(..., regex="^(musician|blogger|photographer|influencer|comedian|writer|other)$")
    terms_accepted: bool = Field(..., description="Must accept terms of service")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_data: Dict[str, Any]


class UserProfile(BaseModel):
    user_id: str
    email: str
    username: str
    first_name: str
    last_name: str
    creator_type: str
    created_at: datetime
    is_verified: bool
    subscription_tier: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8, max_length=100)


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistration):
    """Register a new user account"""    try:
        # Validate terms acceptance
        if not user_data.terms_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Terms of service must be accepted"
            )
        
        # Check if user already exists
        async with database_manager.get_postgres_session() as session:
            existing_user = await session.execute(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (user_data.email, user_data.username)
            )
            
            if existing_user.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email or username already exists"
                )
            
            # Hash password
            hashed_password = security_manager.password_manager.hash_password(user_data.password)
            
            # Create user
            user_id = security_manager.password_manager.generate_secure_token(16)
            tenant_id = security_manager.multitenant_manager.get_tenant_id(user_id)
            
            await session.execute(
                """                INSERT INTO users 
                (id, email, username, password_hash, first_name, last_name, 
                 creator_type, tenant_id, created_at, is_verified, subscription_tier)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, user_data.email, user_data.username, hashed_password,
                 user_data.first_name, user_data.last_name, user_data.creator_type,
                 tenant_id, datetime.utcnow(), False, "free")
            )
            
            # Create user profile data
            profile_data = {
                "user_id": user_id,
                "email": user_data.email,
                "username": user_data.username,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "creator_type": user_data.creator_type,
                "tenant_id": tenant_id,
                "subscription_tier": "free",
                "permissions": ["content:create", "content:read", "protection:basic"]
            }
            
            # Generate tokens
            tokens = security_manager.create_user_tokens(user_id, profile_data)
            
            # Cache user data
            cache_key = f"user_profile:{user_id}"
            await cache_manager.set(cache_key, profile_data, ttl=3600)
            
            # Log registration
            logger.info(f"User registered successfully: {user_data.email}")
            
            return TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type=tokens["token_type"],
                expires_in=3600,
                user_data=profile_data
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """Authenticate user and return tokens"""    try:
        async with database_manager.get_postgres_session() as session:
            # Get user by email
            result = await session.execute(
                """                SELECT id, email, username, password_hash, first_name, last_name, 
                       creator_type, tenant_id, is_verified, subscription_tier, created_at
                FROM users WHERE email = %s AND active = true
                """,
                (credentials.email,)
            )
            
            user_row = result.fetchone()
            if not user_row:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Verify password
            if not security_manager.password_manager.verify_password(
                credentials.password, user_row[3]
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Create user profile data
            profile_data = {
                "user_id": user_row[0],
                "email": user_row[1],
                "username": user_row[2],
                "first_name": user_row[4],
                "last_name": user_row[5],
                "creator_type": user_row[6],
                "tenant_id": user_row[7],
                "is_verified": user_row[8],
                "subscription_tier": user_row[9],
                "permissions": await _get_user_permissions(user_row[9])
            }
            
            # Generate tokens
            tokens = security_manager.create_user_tokens(user_row[0], profile_data)
            
            # Cache user data
            cache_key = f"user_profile:{user_row[0]}"
            await cache_manager.set(cache_key, profile_data, ttl=3600)
            
            # Log login
            logger.info(f"User logged in successfully: {credentials.email}")
            
            return TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type=tokens["token_type"],
                expires_in=3600,
                user_data=profile_data
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    """Refresh access token using refresh token"""    try:
        # Generate new access token
        new_access_token = security_manager.jwt_manager.refresh_access_token(refresh_token)
        
        # Decode refresh token to get user ID
        payload = security_manager.jwt_manager.verify_token(refresh_token)
        user_id = payload["sub"]
        
        # Get cached user data
        cache_key = f"user_profile:{user_id}"
        user_data = await cache_manager.get(cache_key)
        
        if not user_data:
            # Reload user data from database
            async with database_manager.get_postgres_session() as session:
                result = await session.execute(
                    """                    SELECT email, username, first_name, last_name, creator_type,
                           tenant_id, is_verified, subscription_tier
                    FROM users WHERE id = %s AND active = true
                    """,
                    (user_id,)
                )
                
                user_row = result.fetchone()
                if not user_row:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found"
                    )
                
                user_data = {
                    "user_id": user_id,
                    "email": user_row[0],
                    "username": user_row[1],
                    "first_name": user_row[2],
                    "last_name": user_row[3],
                    "creator_type": user_row[4],
                    "tenant_id": user_row[5],
                    "is_verified": user_row[6],
                    "subscription_tier": user_row[7],
                    "permissions": await _get_user_permissions(user_row[7])
                }
                
                # Cache refreshed user data
                await cache_manager.set(cache_key, user_data, ttl=3600)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user_data=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Get current user profile"""    try:
        user_id = current_user["user_id"]
        
        # Try cache first
        cache_key = f"user_profile:{user_id}"
        cached_profile = await cache_manager.get(cache_key)
        
        if cached_profile:
            return UserProfile(**cached_profile)
        
        # Get from database
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                """                SELECT id, email, username, first_name, last_name, creator_type,
                       created_at, is_verified, subscription_tier
                FROM users WHERE id = %s AND active = true
                """,
                (user_id,)
            )
            
            user_row = result.fetchone()
            if not user_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            profile_data = {
                "user_id": user_row[0],
                "email": user_row[1],
                "username": user_row[2],
                "first_name": user_row[3],
                "last_name": user_row[4],
                "creator_type": user_row[5],
                "created_at": user_row[6],
                "is_verified": user_row[7],
                "subscription_tier": user_row[8]
            }
            
            # Cache profile
            await cache_manager.set(cache_key, profile_data, ttl=3600)
            
            return UserProfile(**profile_data)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


@router.put("/profile")
async def update_user_profile(
    profile_updates: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Update user profile"""    try:
        user_id = current_user["user_id"]
        
        # Allowed fields for update
        allowed_fields = ["first_name", "last_name", "username"]
        updates = {k: v for k, v in profile_updates.items() if k in allowed_fields}
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        # Check username uniqueness if being updated
        if "username" in updates:
            async with database_manager.get_postgres_session() as session:
                existing = await session.execute(
                    "SELECT id FROM users WHERE username = %s AND id != %s",
                    (updates["username"], user_id)
                )
                
                if existing.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Username already taken"
                    )
        
        # Update database
        async with database_manager.get_postgres_session() as session:
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            
            await session.execute(
                f"UPDATE users SET {set_clause}, updated_at = %s WHERE id = %s",
                values + [datetime.utcnow()]
            )
        
        # Invalidate cache
        cache_key = f"user_profile:{user_id}"
        await cache_manager.delete(cache_key)
        
        logger.info(f"Profile updated for user {user_id}")
        
        return {"message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Change user password"""    try:
        user_id = current_user["user_id"]
        
        # Get current password hash
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                "SELECT password_hash FROM users WHERE id = %s",
                (user_id,)
            )
            
            user_row = result.fetchone()
            if not user_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Verify current password
            if not security_manager.password_manager.verify_password(
                password_data.current_password, user_row[0]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # Hash new password
            new_password_hash = security_manager.password_manager.hash_password(
                password_data.new_password
            )
            
            # Update password
            await session.execute(
                "UPDATE users SET password_hash = %s, updated_at = %s WHERE id = %s",
                (new_password_hash, datetime.utcnow(), user_id)
            )
        
        logger.info(f"Password changed for user {user_id}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/logout")
async def logout_user(
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Logout user (invalidate tokens)"""    try:
        user_id = current_user["user_id"]
        
        # Invalidate cached user data
        cache_key = f"user_profile:{user_id}"
        await cache_manager.delete(cache_key)
        
        # In a production system, you would maintain a blacklist of invalidated tokens
        # For now, we just clear the cache
        
        logger.info(f"User logged out: {user_id}")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


async def _get_user_permissions(subscription_tier: str) -> list:
    """Get user permissions based on subscription tier"""    base_permissions = ["content:create", "content:read", "protection:basic"]
    
    if subscription_tier == "premium":
        base_permissions.extend([
            "protection:advanced", "analytics:detailed", "collaboration:unlimited"
        ])
    elif subscription_tier == "professional":
        base_permissions.extend([
            "protection:advanced", "analytics:detailed", "collaboration:unlimited",
            "api:full_access", "priority_support"
        ])
    
    return base_permissions