"""
API Dependencies for Challenges & Competitions
==============================================
Module: api/dependencies.py
Author: Fahed Mlaiel (mlaiel@live.de)

Basic dependencies for authentication and authorization.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    This is a simplified version - in production would validate JWT.
    """
    try:
        # In a real implementation, you would:
        # 1. Decode and validate the JWT token
        # 2. Extract user information
        # 3. Check if user exists and is active
        
        # For now, return a mock user
        return {
            "user_id": "user_123",
            "username": "demo_user",
            "email": "demo@example.com",
            "roles": ["user"],
            "permissions": ["challenge:participate", "challenge:create"]
        }
        
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def verify_permissions(required_permission: str):
    """
    Verify user has required permission.
    """
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        
        if required_permission not in user_permissions:
            # For demo purposes, allow all challenge operations
            if required_permission.startswith("challenge:"):
                return None
                
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{required_permission}' required"
            )
        
        return None
    
    return permission_checker