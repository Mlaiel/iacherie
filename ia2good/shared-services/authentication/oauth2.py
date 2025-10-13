"""
OAuth2 Handler
Implements OAuth2 password flow with FastAPI
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .jwt_handler import JWTHandler


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class OAuth2Handler:
    """Handle OAuth2 authentication flow"""
    
    def __init__(self):
        self.jwt_handler = JWTHandler()
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> dict:
        """
        Validate token and return current user
        
        Args:
            token: JWT token from request header
            
        Returns:
            User payload from token
            
        Raises:
            HTTPException: If token is invalid
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        payload = self.jwt_handler.verify_token(token)
        
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        return payload
    
    async def get_current_active_user(
        self, 
        current_user: dict = Depends(get_current_user)
    ) -> dict:
        """
        Validate that user is active
        
        Args:
            current_user: User payload from get_current_user
            
        Returns:
            Active user payload
            
        Raises:
            HTTPException: If user is inactive
        """
        # In production, check user status from database
        if current_user.get("status") == "inactive":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        return current_user
    
    def require_role(self, required_roles: list[str]):
        """
        Dependency to check if user has required role
        
        Args:
            required_roles: List of allowed roles
            
        Returns:
            Dependency function
        """
        async def role_checker(current_user: dict = Depends(self.get_current_user)) -> dict:
            user_roles = current_user.get("roles", [])
            
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have required role. Required: {required_roles}"
                )
            
            return current_user
        
        return role_checker
    
    def require_module_access(self, module: str):
        """
        Dependency to check if user has access to specific module
        
        Args:
            module: Module name (ia2good, guardian, eduverify, medcare)
            
        Returns:
            Dependency function
        """
        async def module_checker(current_user: dict = Depends(self.get_current_user)) -> dict:
            user_modules = current_user.get("modules", [])
            
            if module not in user_modules:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have access to module: {module}"
                )
            
            return current_user
        
        return module_checker
