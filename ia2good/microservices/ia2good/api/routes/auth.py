"""
Authentication routes - Login, register, token refresh
Real JWT-based authentication endpoints
"""
from datetime import timedelta
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, ConfigDict

from api.dependencies import get_db, get_current_user
from services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models.user import User

router = APIRouter()


# Pydantic models for request/response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID  # Accepte UUID directement
    email: str
    username: str
    full_name: Optional[str] = None
    roles: list[str]
    is_active: bool
    is_verified: bool


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Creates a new user account with the provided credentials.
    Password is automatically hashed before storage.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    user = create_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
        roles=["user"]  # Default role
    )
    
    return user


@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email/username and password
    
    Returns a JWT access token that can be used for authenticated requests.
    Token should be included in Authorization header as: Bearer <token>
    """
    # Try to authenticate with email or username
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/auth/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    Returns the profile of the currently authenticated user.
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.post("/auth/test-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_test_user(db: Session = Depends(get_db)):
    """
    Create a test user for development/testing
    
    Credentials:
    - Email: test@ia2good.com
    - Username: testuser
    - Password: Test123!
    
    ⚠️ This endpoint should be disabled in production!
    """
    # Check if test user already exists
    existing = db.query(User).filter(User.email == "test@ia2good.com").first()
    if existing:
        return existing
    
    # Create test user
    user = create_user(
        db=db,
        email="test@ia2good.com",
        username="testuser",
        password="Test123!",
        full_name="Test User",
        roles=["user", "volunteer", "admin"]
    )
    
    return user
