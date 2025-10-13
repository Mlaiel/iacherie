"""
Real JWT Authentication Service
Handles token creation, validation, and user authentication
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from models.user import User
import os

# Security settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION_ia2good_secret_key_2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hash a password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing user data (typically {"sub": user_id})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email/username and password
    
    Args:
        db: Database session
        email: User email or username
        password: Plain text password
        
    Returns:
        User object if authenticated, None otherwise
    """
    # Try email first, then username
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = db.query(User).filter(User.username == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Get user by ID
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        User object or None
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    email: str,
    username: str,
    password: str,
    full_name: Optional[str] = None,
    roles: Optional[list] = None
) -> User:
    """
    Create a new user
    
    Args:
        db: Database session
        email: User email
        username: Username
        password: Plain text password (will be hashed)
        full_name: Optional full name
        roles: Optional list of role names
        
    Returns:
        Created User object
    """
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hashed_password,
        roles=roles or ["user"],
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
