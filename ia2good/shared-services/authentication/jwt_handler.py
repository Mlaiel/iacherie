"""
JWT Token Handler
Manages JWT token creation, validation, and refresh
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError
import os


class JWTHandler:
    """Handle JWT token operations"""
    
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        self.access_token_expire_minutes = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
        self.refresh_token_expire_days = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    
    def create_access_token(
        self, 
        user_id: str, 
        email: str,
        roles: list[str] = None,
        additional_claims: Dict[str, Any] = None
    ) -> str:
        """
        Create a new access token
        
        Args:
            user_id: User unique identifier
            email: User email
            roles: List of user roles
            additional_claims: Any additional claims to include
            
        Returns:
            Encoded JWT token string
        """
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            'sub': user_id,
            'email': email,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        if roles:
            to_encode['roles'] = roles
            
        if additional_claims:
            to_encode.update(additional_claims)
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a new refresh token
        
        Args:
            user_id: User unique identifier
            
        Returns:
            Encoded JWT refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode = {
            'sub': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Generate new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict with new access_token and refresh_token, or None if invalid
        """
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return None
        
        user_id = payload.get('sub')
        if not user_id:
            return None
        
        # In production, you'd fetch user details from database
        # For now, create basic tokens
        new_access_token = self.create_access_token(user_id=user_id, email='')
        new_refresh_token = self.create_refresh_token(user_id=user_id)
        
        return {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'bearer'
        }
