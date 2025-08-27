"""
Authentication endpoints for IA Influencer Agent platform.

This module handles user authentication, JWT token management,
and access control for the multi-format content protection system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import logging

from ..core.config import get_settings
from ..core.database import get_db
from ..models.user import User, UserCreate, UserInDB, Token, TokenData
from ..business.user_service import UserService
from ..security.auth_manager import AuthManager

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Response models
class LoginResponse(BaseModel):
    """Response model for successful login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_profile: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Request model for password reset"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Request model for password reset confirmation"""
    token: str
    new_password: str

# Authentication endpoints
@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db=Depends(get_db),
    user_service: UserService = Depends()
):
    """
    Register new user with email verification.
    
    Supports multi-role registration:
    - Musician, Blogger, Photographer, Influencer, Actor
    """
    try:
        # Validate user role and content types
        if user_data.role not in settings.ALLOWED_USER_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user role specified"
            )
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user with email verification
        new_user = await user_service.create_user(user_data)
        
        # Send verification email
        verification_token = AuthManager.generate_verification_token(new_user.email)
        await user_service.send_verification_email(new_user.email, verification_token)
        
        logger.info(f"New user registered: {user_data.email} - Role: {user_data.role}")
        
        return {
            "message": "User registered successfully",
            "user_id": str(new_user.id),
            "email_verification_sent": True,
            "role": new_user.role,
            "supported_formats": new_user.supported_content_formats
        }
        
    except Exception as e:
        logger.error(f"Registration error for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/token", response_model=LoginResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
    user_service: UserService = Depends(),
    auth_manager: AuthManager = Depends()
):
    """
    Authenticate user and return access/refresh tokens.
    
    Returns JWT tokens with user profile information.
    """
    try:
        # Authenticate user
        user = await user_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is verified
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified"
            )
        
        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Generate tokens
        access_token = auth_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        refresh_token = auth_manager.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # Update last login
        await user_service.update_last_login(user.id)
        
        logger.info(f"Successful login: {user.email}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_profile={
                "user_id": str(user.id),
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "full_name": user.full_name,
                "supported_formats": user.supported_content_formats,
                "profile_completed": user.profile_completed,
                "subscription_tier": user.subscription_tier
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post("/refresh", response_model=Dict[str, str])
async def refresh_access_token(
    request: RefreshTokenRequest,
    auth_manager: AuthManager = Depends()
):
    """
    Refresh access token using valid refresh token.
    """
    try:
        payload = auth_manager.verify_refresh_token(request.refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Generate new access token
        new_access_token = auth_manager.create_access_token(
            data={"sub": user_id}
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    user_service: UserService = Depends(),
    auth_manager: AuthManager = Depends()
):
    """
    Verify user email using verification token.
    """
    try:
        payload = auth_manager.verify_verification_token(token)
        email = payload.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        # Verify user email
        user = await user_service.verify_user_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Email verified: {email}")
        
        return {
            "message": "Email verified successfully",
            "user_id": str(user.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification failed"
        )

@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    user_service: UserService = Depends()
):
    """
    Request password reset link via email.
    """
    try:
        user = await user_service.get_user_by_email(request.email)
        if user:
            reset_token = AuthManager.generate_password_reset_token(request.email)
            await user_service.send_password_reset_email(request.email, reset_token)
            logger.info(f"Password reset requested: {request.email}")
        
        # Always return success for security (don't reveal if email exists)
        return {
            "message": "If the email exists, a reset link has been sent"
        }
        
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        return {
            "message": "If the email exists, a reset link has been sent"
        }

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    user_service: UserService = Depends(),
    auth_manager: AuthManager = Depends()
):
    """
    Confirm password reset with token and new password.
    """
    try:
        payload = auth_manager.verify_password_reset_token(request.token)
        email = payload.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Update user password
        user = await user_service.reset_user_password(email, request.new_password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Password reset completed: {email}")
        
        return {
            "message": "Password reset successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirmation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset failed"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(auth_manager.get_current_user),
    auth_manager: AuthManager = Depends()
):
    """
    Logout user by invalidating tokens.
    """
    try:
        # Add token to blacklist
        await auth_manager.invalidate_user_tokens(str(current_user.id))
        
        logger.info(f"User logged out: {current_user.email}")
        
        return {
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Get current authenticated user information.
    """
    try:
        return {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "username": current_user.username,
            "role": current_user.role,
            "full_name": current_user.full_name,
            "supported_formats": current_user.supported_content_formats,
            "profile_completed": current_user.profile_completed,
            "subscription_tier": current_user.subscription_tier,
            "is_verified": current_user.is_verified,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "last_login": current_user.last_login
        }
        
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )

@router.put("/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user: User = Depends(auth_manager.get_current_user),
    user_service: UserService = Depends()
):
    """
    Change user password (requires current password).
    """
    try:
        # Verify current password
        if not await user_service.verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Update password
        await user_service.update_user_password(current_user.id, new_password)
        
        logger.info(f"Password changed: {current_user.email}")
        
        return {
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

# Admin endpoints
@router.get("/users", dependencies=[Depends(auth_manager.require_admin)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends()
):
    """
    List all users (admin only).
    """
    try:
        users = await user_service.get_users(skip=skip, limit=limit)
        return {
            "users": [
                {
                    "user_id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at,
                    "last_login": user.last_login
                }
                for user in users
            ],
            "total": len(users)
        }
        
    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )
