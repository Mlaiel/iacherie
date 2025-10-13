"""API Dependencies - Database sessions, authentication, etc."""
from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.auth_service import decode_access_token, get_user_by_id
from models.user import User


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    
    Creates a new database session for each request and closes it after.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get current authenticated user from JWT token
    
    Extracts JWT from Authorization header, validates it, and returns user data.
    Raises 401 if token is missing or invalid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user data from token
    user_id: str = payload.get("sub") or payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return user data from token (no DB lookup needed)
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "roles": payload.get("roles", ["user"])
    }


def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[object]:
    """
    Get current user if authenticated, None otherwise
    
    Useful for endpoints that work for both authenticated and anonymous users.
    """
    try:
        return get_current_user(authorization, db)
    except Exception:
        return None


def require_role(required_role: str):
    """
    Dependency factory for role-based access control
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
        def admin_only():
            return {"message": "Admin access"}
    """
    def role_checker(current_user = Depends(get_current_user)):
        if required_role not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_checker
