"""User business service for IA Influencer Agent platform.

This service handles all user-related business logic including registration,
authentication, profile management, and role-based operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging

from ..core.config import get_settings
from ..core.database import get_db
from ..models.user import User, UserCreate, UserUpdate, UserInDB
from ..utils.email_sender import EmailSender
from ..utils.profile_validator import ProfileValidator

logger = logging.getLogger(__name__)
settings = get_settings()

class UserService:
    """
    Comprehensive user management service for multi-role content creators.
    
    Supports: Musicians, Bloggers, Photographers, Influencers, Actors
    """
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.email_sender = EmailSender()
        self.profile_validator = ProfileValidator()
    
    async def create_user(self, user_data: UserCreate, db: Session = None) -> User:
        """
        Create new user with role-specific initialization.
        
        Args:
            user_data: User creation data with role and content preferences
            db: Database session
            
        Returns:
            Created user instance
        """
        try:
            if not db:
                db = next(get_db())
            
            # Validate user data based on role
            validation_result = await self.profile_validator.validate_user_data(user_data)
            if not validation_result.is_valid:
                raise ValueError(f"Invalid user data: {validation_result.errors}")
            
            # Hash password
            hashed_password = self.pwd_context.hash(user_data.password)
            
            # Create user instance
            user = User(
                id=uuid.uuid4(),
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                role=user_data.role,
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow(),
                supported_content_formats=self._get_role_content_formats(user_data.role),
                subscription_tier="basic",
                profile_completed=False
            )
            
            # Role-specific initialization
            await self._initialize_role_specific_data(user, user_data)
            
            # Save to database
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created: {user.email} - Role: {user.role}")
            return user
            
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def authenticate_user(self, email: str, password: str, db: Session = None) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            db: Database session
            
        Returns:
            Authenticated user or None
        """
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None
            
            if not self.verify_password(password, user.hashed_password):
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            logger.info(f"User authenticated: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def get_user_by_email(self, email: str, db: Session = None) -> Optional[User]:
        """
Get user by email address"""
        try:
            if not db:
                db = next(get_db())
            
            return db.query(User).filter(User.email == email).first()
            
        except Exception as e:
            logger.error(f"Get user by email error: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str, db: Session = None) -> Optional[User]:
        """Get user by ID"""
        try:
            if not db:
                db = next(get_db())
            
            return db.query(User).filter(User.id == user_id).first()
            
        except Exception as e:
            logger.error(f"Get user by ID error: {str(e)}")
            return None
    
    async def update_user(self, user_id: str, user_update: UserUpdate, db: Session = None) -> Optional[User]:
        """
        Update user profile with role-specific validation.
        """
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Validate updates based on role
            if user_update.dict(exclude_unset=True):
                validation_result = await self.profile_validator.validate_user_update(
                    user, user_update
                )
                if not validation_result.is_valid:
                    raise ValueError(f"Invalid update data: {validation_result.errors}")
            
            # Apply updates
            update_data = user_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            # Check if profile is completed
            user.profile_completed = self._check_profile_completion(user)
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User updated: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"User update error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def verify_user_email(self, email: str, db: Session = None) -> Optional[User]:
        """Verify user email address"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None
            
            user.is_verified = True
            user.verified_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            
            logger.info(f"Email verified: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            if db:
                db.rollback()
            return None
    
    async def reset_user_password(self, email: str, new_password: str, db: Session = None) -> Optional[User]:
        """Reset user password"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None
            
            # Hash new password
            user.hashed_password = self.pwd_context.hash(new_password)
            user.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"Password reset: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            if db:
                db.rollback()
            return None
    
    async def update_user_password(self, user_id: str, new_password: str, db: Session = None) -> bool:
        """Update user password"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.hashed_password = self.pwd_context.hash(new_password)
            user.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Password updated for user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Password update error: {str(e)}")
            if db:
                db.rollback()
            return False
    
    async def update_last_login(self, user_id: str, db: Session = None) -> None:
        """Update user's last login timestamp"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.utcnow()
                db.commit()
                
        except Exception as e:
            logger.error(f"Update last login error: {str(e)}")
    
    async def get_users(self, skip: int = 0, limit: int = 100, db: Session = None) -> List[User]:
        """Get list of users with pagination"""
        try:
            if not db:
                db = next(get_db())
            
            return db.query(User).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Get users error: {str(e)}")
            return []
    
    async def send_verification_email(self, email: str, token: str) -> bool:
        """Send email verification link"""
        try:
            verification_url = f"{settings.frontend_url}/verify-email?token={token}"
            
            await self.email_sender.send_verification_email(
                recipient=email,
                verification_url=verification_url
            )
            
            logger.info(f"Verification email sent: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Send verification email error: {str(e)}")
            return False
    
    async def send_password_reset_email(self, email: str, token: str) -> bool:
        """Send password reset link"""
        try:
            reset_url = f"{settings.frontend_url}/reset-password?token={token}"
            
            await self.email_sender.send_password_reset_email(
                recipient=email,
                reset_url=reset_url
            )
            
            logger.info(f"Password reset email sent: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Send password reset email error: {str(e)}")
            return False
    
    async def get_user_statistics(self, user_id: str, db: Session = None) -> Dict[str, Any]:
        """Get user statistics and metrics"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # Calculate user statistics
            stats = {
                "total_content": len(user.content_items) if hasattr(user, 'content_items') else 0,
                "total_collaborations": len(user.collaborations) if hasattr(user, 'collaborations') else 0,
                "profile_completion": self._calculate_profile_completion(user),
                "account_age_days": (datetime.utcnow() - user.created_at).days,
                "last_activity": user.last_login,
                "subscription_tier": user.subscription_tier,
                "role": user.role,
                "is_verified": user.is_verified
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Get user statistics error: {str(e)}")
            return {}
    
    def _get_role_content_formats(self, role: str) -> List[str]:
        """Get supported content formats based on user role"""
        role_formats = {
            "musician": ["audio", "video", "image"],
            "blogger": ["text", "image", "video", "document"],
            "photographer": ["image", "video"],
            "influencer": ["image", "video", "text"],
            "actor": ["video", "audio", "image"]
        }
        return role_formats.get(role.lower(), ["text", "image"])
    
    async def _initialize_role_specific_data(self, user: User, user_data: UserCreate) -> None:
        """Initialize role-specific user data and preferences"""
        try:
            role_config = {
                "musician": {
                    "preferred_genres": getattr(user_data, 'genres', []),
                    "instruments": getattr(user_data, 'instruments', []),
                    "experience_level": getattr(user_data, 'experience_level', 'beginner')
                },
                "blogger": {
                    "niches": getattr(user_data, 'niches', []),
                    "writing_style": getattr(user_data, 'writing_style', 'casual'),
                    "target_audience": getattr(user_data, 'target_audience', 'general')
                },
                "photographer": {
                    "photography_styles": getattr(user_data, 'photography_styles', []),
                    "equipment": getattr(user_data, 'equipment', []),
                    "specializations": getattr(user_data, 'specializations', [])
                },
                "influencer": {
                    "platforms": getattr(user_data, 'platforms', []),
                    "follower_ranges": getattr(user_data, 'follower_ranges', {}),
                    "content_themes": getattr(user_data, 'content_themes', [])
                },
                "actor": {
                    "acting_styles": getattr(user_data, 'acting_styles', []),
                    "languages": getattr(user_data, 'languages', []),
                    "performance_types": getattr(user_data, 'performance_types', [])
                }
            }
            
            user.role_specific_data = role_config.get(user.role.lower(), {})
            
        except Exception as e:
            logger.error(f"Role-specific initialization error: {str(e)}")
    
    def _check_profile_completion(self, user: User) -> bool:
        """Check if user profile is complete based on role requirements"""
        required_fields = ['full_name', 'role']
        
        for field in required_fields:
            if not getattr(user, field, None):
                return False
        
        # Role-specific completion checks
        if user.role == "musician" and not user.role_specific_data.get('instruments'):
            return False
        elif user.role == "blogger" and not user.role_specific_data.get('niches'):
            return False
        elif user.role == "photographer" and not user.role_specific_data.get('photography_styles'):
            return False
        
        return True
    
    def _calculate_profile_completion(self, user: User) -> float:
        """Calculate profile completion percentage"""
        total_fields = 10
        completed_fields = 0
        
        # Basic fields
        if user.full_name:
            completed_fields += 1
        if user.bio:
            completed_fields += 1
        if user.location:
            completed_fields += 1
        if user.website:
            completed_fields += 1
        if user.profile_image_url:
            completed_fields += 1
        if user.is_verified:
            completed_fields += 1
        
        # Role-specific fields
        if user.role_specific_data:
            completed_fields += min(4, len(user.role_specific_data))
        
        return round((completed_fields / total_fields) * 100, 2)
