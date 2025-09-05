"""
Core Authentication Components for Ainflue Platform
Provides user authentication, session management, and authorization
"""

import json
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
from .logging import get_logger
from .security import SecurityManager, TokenManager

logger = get_logger("auth")


class User:
    """User model for authentication"""
    
    def __init__(self, user_id: str, email: str, username: str, roles: Optional[List[str]] = None):
        self.user_id = user_id
        self.email = email
        self.username = username
        self.roles = roles or ["user"]
        self.created_at = datetime.utcnow()
        self.last_login = None
        self.is_active = True
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'roles': self.roles,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary"""
        user = cls(
            user_id=data['user_id'],
            email=data['email'],
            username=data['username'],
            roles=data.get('roles', ["user"])
        )
        user.created_at = datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat()))
        user.last_login = datetime.fromisoformat(data['last_login']) if data.get('last_login') else None
        user.is_active = data.get('is_active', True)
        user.metadata = data.get('metadata', {})
        return user


class AuthenticationManager:
    """Manages user authentication and sessions"""
    
    def __init__(self):
        self.security_manager = SecurityManager()
        self.token_manager = TokenManager()
        self.logger = get_logger("auth_manager")
        self.users: Dict[str, User] = {}  # In production, this would be a database
        self.user_credentials: Dict[str, str] = {}  # username -> hashed_password
    
    def create_user(self, email: str, username: str, password: str, roles: Optional[List[str]] = None) -> Optional[User]:
        """Create a new user account"""
        try:
            # Check if user already exists
            if any(user.email == email or user.username == username for user in self.users.values()):
                self.logger.warning(f"User creation failed - already exists: {email}/{username}")
                return None
            
            # Generate user ID
            import uuid
            user_id = str(uuid.uuid4())
            
            # Hash password
            password_hash = self.security_manager.generate_secure_hash(password)
            
            # Create user
            user = User(user_id=user_id, email=email, username=username, roles=roles)
            
            # Store user and credentials
            self.users[user_id] = user
            self.user_credentials[username] = password_hash
            
            self.logger.info(f"User created successfully: {username} ({user_id})")
            return user
            
        except Exception as e:
            self.logger.error(f"User creation error: {str(e)}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return token"""
        try:
            # Find user by username
            user = self._get_user_by_username(username)
            if not user:
                self.logger.warning(f"Authentication failed - user not found: {username}")
                return None
            
            if not user.is_active:
                self.logger.warning(f"Authentication failed - user inactive: {username}")
                return None
            
            # Verify password
            stored_hash = self.user_credentials.get(username)
            if not stored_hash or not self.security_manager.verify_hash(password, stored_hash):
                self.logger.warning(f"Authentication failed - invalid password: {username}")
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            
            # Generate token
            token = self.token_manager.generate_token(
                user_id=user.user_id,
                additional_data={
                    'username': user.username,
                    'email': user.email,
                    'roles': user.roles
                }
            )
            
            self.logger.info(f"User authenticated successfully: {username}")
            return token
            
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return None
    
    def validate_token(self, token: str) -> Optional[User]:
        """Validate token and return user"""
        token_data = self.token_manager.validate_token(token)
        if not token_data:
            return None
        
        user_id = token_data.get('user_id')
        return self.users.get(user_id)
    
    def logout_user(self, token: str) -> bool:
        """Logout user by revoking token"""
        return self.token_manager.revoke_token(token)
    
    def update_user_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Update user password"""
        try:
            user = self.users.get(user_id)
            if not user:
                return False
            
            # Verify old password
            stored_hash = self.user_credentials.get(user.username)
            if not stored_hash or not self.security_manager.verify_hash(old_password, stored_hash):
                self.logger.warning(f"Password update failed - invalid old password: {user.username}")
                return False
            
            # Hash new password
            new_hash = self.security_manager.generate_secure_hash(new_password)
            self.user_credentials[user.username] = new_hash
            
            self.logger.info(f"Password updated successfully: {user.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Password update error: {str(e)}")
            return False
    
    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account"""
        user = self.users.get(user_id)
        if user:
            user.is_active = False
            self.logger.info(f"User deactivated: {user.username}")
            return True
        return False


class AuthorizationManager:
    """Manages user permissions and role-based access control"""
    
    def __init__(self):
        self.logger = get_logger("authz_manager")
        self.permissions: Dict[str, List[str]] = {
            "admin": ["*"],  # Admin has all permissions
            "user": ["read", "write_own", "update_own"],
            "viewer": ["read"],
            "moderator": ["read", "write", "moderate"]
        }
    
    def check_permission(self, user: User, permission: str, resource: Optional[str] = None) -> bool:
        """Check if user has permission for a resource"""
        try:
            if not user.is_active:
                return False
            
            for role in user.roles:
                role_permissions = self.permissions.get(role, [])
                
                # Admin has all permissions
                if "*" in role_permissions:
                    return True
                
                # Check exact permission match
                if permission in role_permissions:
                    return True
                
                # Check resource-specific permissions
                if resource and f"{permission}_{resource}" in role_permissions:
                    return True
            
            self.logger.debug(f"Permission denied: {user.username} -> {permission} on {resource}")
            return False
            
        except Exception as e:
            self.logger.error(f"Permission check error: {str(e)}")
            return False
    
    def add_role_permission(self, role: str, permission: str) -> bool:
        """Add permission to a role"""
        try:
            if role not in self.permissions:
                self.permissions[role] = []
            
            if permission not in self.permissions[role]:
                self.permissions[role].append(permission)
                self.logger.info(f"Permission added: {role} -> {permission}")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Add permission error: {str(e)}")
            return False
    
    def remove_role_permission(self, role: str, permission: str) -> bool:
        """Remove permission from a role"""
        try:
            if role in self.permissions and permission in self.permissions[role]:
                self.permissions[role].remove(permission)
                self.logger.info(f"Permission removed: {role} -> {permission}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Remove permission error: {str(e)}")
            return False


# Factory functions
def create_authentication_manager() -> AuthenticationManager:
    """Create an authentication manager instance"""
    return AuthenticationManager()


def create_authorization_manager() -> AuthorizationManager:
    """Create an authorization manager instance"""
    return AuthorizationManager()


def create_auth_system() -> Dict[str, Any]:
    """Create a complete authentication system"""
    return {
        'auth_manager': create_authentication_manager(),
        'authz_manager': create_authorization_manager()
    }


__all__ = [
    "User",
    "AuthenticationManager",
    "AuthorizationManager",
    "create_authentication_manager",
    "create_authorization_manager",
    "create_auth_system"
]