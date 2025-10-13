"""
Guardian Authentication & Permissions System
User roles, permissions, and access control
"""

from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Set
from datetime import datetime
import uuid

class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    COORDINATOR = "coordinator"
    VOLUNTEER = "volunteer"
    GUEST = "guest"

class Permission(str, Enum):
    """System permissions"""
    # Mission permissions
    MISSION_CREATE = "mission:create"
    MISSION_EDIT = "mission:edit"
    MISSION_DELETE = "mission:delete"
    MISSION_VIEW = "mission:view"
    MISSION_APPROVE = "mission:approve"
    
    # Volunteer permissions
    VOLUNTEER_REGISTER = "volunteer:register"
    VOLUNTEER_EDIT = "volunteer:edit"
    VOLUNTEER_VIEW = "volunteer:view"
    VOLUNTEER_MANAGE = "volunteer:manage"
    
    # Content permissions
    CONTENT_MODERATE = "content:moderate"
    CONTENT_DELETE = "content:delete"
    
    # Stream permissions
    STREAM_CREATE = "stream:create"
    STREAM_MODERATE = "stream:moderate"
    
    # Room permissions
    ROOM_CREATE = "room:create"
    ROOM_MODERATE = "room:moderate"
    
    # File permissions
    FILE_UPLOAD = "file:upload"
    FILE_DELETE = "file:delete"
    FILE_MODERATE = "file:moderate"
    
    # Chat permissions
    CHAT_SEND = "chat:send"
    CHAT_MODERATE = "chat:moderate"
    
    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    ADMIN_USERS = "admin:users"

# Role-based permissions mapping
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: {
        # Full access
        *list(Permission)
    },
    
    UserRole.MODERATOR: {
        Permission.MISSION_VIEW,
        Permission.MISSION_APPROVE,
        Permission.VOLUNTEER_VIEW,
        Permission.VOLUNTEER_MANAGE,
        Permission.CONTENT_MODERATE,
        Permission.CONTENT_DELETE,
        Permission.STREAM_MODERATE,
        Permission.ROOM_MODERATE,
        Permission.FILE_MODERATE,
        Permission.CHAT_MODERATE,
    },
    
    UserRole.COORDINATOR: {
        Permission.MISSION_CREATE,
        Permission.MISSION_EDIT,
        Permission.MISSION_VIEW,
        Permission.VOLUNTEER_VIEW,
        Permission.VOLUNTEER_MANAGE,
        Permission.STREAM_CREATE,
        Permission.ROOM_CREATE,
        Permission.FILE_UPLOAD,
        Permission.CHAT_SEND,
    },
    
    UserRole.VOLUNTEER: {
        Permission.MISSION_VIEW,
        Permission.VOLUNTEER_REGISTER,
        Permission.VOLUNTEER_EDIT,
        Permission.STREAM_CREATE,
        Permission.ROOM_CREATE,
        Permission.FILE_UPLOAD,
        Permission.CHAT_SEND,
    },
    
    UserRole.GUEST: {
        Permission.MISSION_VIEW,
        Permission.VOLUNTEER_REGISTER,
    }
}

class User(BaseModel):
    """User model with authentication"""
    user_id: str
    username: str
    email: Optional[str] = None
    role: UserRole = UserRole.VOLUNTEER
    is_verified: bool = False
    is_banned: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        if self.is_banned:
            return False
        
        role_perms = ROLE_PERMISSIONS.get(self.role, set())
        return permission in role_perms
    
    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the given permissions"""
        return any(self.has_permission(perm) for perm in permissions)
    
    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if user has all of the given permissions"""
        return all(self.has_permission(perm) for perm in permissions)

class AuthManager:
    """Simple authentication manager"""
    
    def __init__(self):
        # In-memory user storage (should use database in production)
        self.users: dict[str, User] = {}
        self.sessions: dict[str, str] = {}  # session_token -> user_id
    
    def create_user(
        self,
        username: str,
        email: Optional[str] = None,
        role: UserRole = UserRole.VOLUNTEER
    ) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            created_at=datetime.utcnow()
        )
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_session(self, session_token: str) -> Optional[User]:
        """Get user by session token"""
        user_id = self.sessions.get(session_token)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def create_session(self, user_id: str) -> str:
        """Create session for user"""
        session_token = str(uuid.uuid4())
        self.sessions[session_token] = user_id
        
        # Update last login
        if user_id in self.users:
            self.users[user_id].last_login = datetime.utcnow()
        
        return session_token
    
    def validate_session(self, session_token: str) -> bool:
        """Check if session is valid"""
        return session_token in self.sessions
    
    def revoke_session(self, session_token: str):
        """Revoke session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
    
    def ban_user(self, user_id: str):
        """Ban a user"""
        if user_id in self.users:
            self.users[user_id].is_banned = True
            
            # Revoke all sessions
            sessions_to_revoke = [
                token for token, uid in self.sessions.items()
                if uid == user_id
            ]
            for token in sessions_to_revoke:
                del self.sessions[token]
    
    def unban_user(self, user_id: str):
        """Unban a user"""
        if user_id in self.users:
            self.users[user_id].is_banned = False
    
    def verify_user(self, user_id: str):
        """Verify a user"""
        if user_id in self.users:
            self.users[user_id].is_verified = True
    
    def change_role(self, user_id: str, new_role: UserRole):
        """Change user role"""
        if user_id in self.users:
            self.users[user_id].role = new_role

# Singleton instance
_auth_manager_instance = None

def get_auth_manager() -> AuthManager:
    """Get or create auth manager instance"""
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = AuthManager()
        
        # Create default admin user
        admin = _auth_manager_instance.create_user(
            username="admin",
            email="admin@guardian.io",
            role=UserRole.ADMIN
        )
        _auth_manager_instance.verify_user(admin.user_id)
    
    return _auth_manager_instance

def require_permission(permission: Permission):
    """
    Decorator to require specific permission
    Usage: @require_permission(Permission.MISSION_CREATE)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This is a simplified example
            # In real implementation, extract user from request context
            return await func(*args, **kwargs)
        return wrapper
    return decorator
