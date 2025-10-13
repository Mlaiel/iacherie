"""
Security and Permission Management System
Role-based access control for OpenAI API routes
"""
from typing import List, Callable
from functools import wraps
from fastapi import HTTPException, status, Depends
from backend.security.auth_manager import get_current_user, User

def require_permissions(required_permissions: List[str]) -> Callable:
    """
    Decorator to require specific permissions for API endpoints
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs (injected by FastAPI dependency)


            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permissions

            user_permissions = set(current_user.permissions)


            required_permissions_set = set(required_permissions)

            
            if not required_permissions_set.issubset(user_permissions):
                missing_permissions = required_permissions_set - user_permissions
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permissions: {', '.join(missing_permissions)}"
                )

            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Export for use in other modules
__all__ = ["require_permissions"]