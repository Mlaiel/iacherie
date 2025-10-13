"""
User Model avec support multilingue (644+ langues)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class UserRole(str, enum.Enum):
    """Rôles utilisateur"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    COORDINATOR = "coordinator"
    VOLUNTEER = "volunteer"
    GUEST = "guest"


class User(Base):
    """
    Utilisateur avec support multilingue (644+ langues)
    """
    __tablename__ = "users"
    
    # ID et authentification
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    
    # Rôle et permissions
    role = Column(SQLEnum(UserRole), default=UserRole.VOLUNTEER)
    permissions = Column(JSON)  # Permissions spécifiques
    
    # Informations personnelles
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(200))
    
    # Bio et description (multilingue)
    bio_translations = Column(JSON)  # {"EN": "I love helping...", "FR": "J'adore aider..."}
    
    # Photo de profil
    profile_picture_url = Column(String(500))
    cover_image_url = Column(String(500))
    
    # Langues
    preferred_language = Column(String(10), default="EN")
    spoken_languages = Column(JSON)  # ["EN", "FR", "ES", "AR"]
    language_proficiency = Column(JSON)  # {"EN": "native", "FR": "fluent"}
    
    # Localisation
    country = Column(String(100))
    city = Column(String(100))
    timezone = Column(String(50))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Contact
    phone = Column(String(50))
    phone_verified = Column(Boolean, default=False)
    
    # Réseaux sociaux
    social_links = Column(JSON)  # {"twitter": "url", "linkedin": "url"}
    
    # Statut du compte
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    ban_reason_translations = Column(JSON)
    banned_until = Column(DateTime, nullable=True)
    
    # Vérifications
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    background_check_completed = Column(Boolean, default=False)
    background_check_date = Column(DateTime, nullable=True)
    
    # Statistiques
    total_missions = Column(Integer, default=0)
    completed_missions = Column(Integer, default=0)
    total_hours_volunteered = Column(Integer, default=0)
    impact_score = Column(Float, default=0.0)
    reputation_score = Column(Float, default=0.0)
    
    # Badges et récompenses
    badges = Column(JSON)  # Liste de badges obtenus
    certifications = Column(JSON)  # Certifications
    
    # Préférences de notification
    notification_preferences = Column(JSON)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    
    # Préférences de confidentialité
    profile_visibility = Column(String(20), default="public")  # public, friends, private
    show_location = Column(Boolean, default=True)
    show_contact = Column(Boolean, default=False)
    
    # Dates
    last_login_at = Column(DateTime, nullable=True)
    last_active_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relations
    coordinated_missions = relationship("Mission", back_populates="coordinator")
    volunteer_applications = relationship("Volunteer", back_populates="user")
    
    def get_bio(self, language: str = "EN") -> str:
        """Obtient la bio dans la langue demandée"""
        if not self.bio_translations:
            return ""
        return self.bio_translations.get(language.upper(),
                                         self.bio_translations.get("EN", ""))
    
    def to_dict(self, language: str = "EN", include_sensitive: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.email if include_sensitive else None,
            "role": self.role.value if self.role else None,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "bio": self.get_bio(language),
            "profile_picture_url": self.profile_picture_url,
            "preferred_language": self.preferred_language,
            "spoken_languages": self.spoken_languages,
            "country": self.country,
            "city": self.city if self.show_location else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "total_missions": self.total_missions,
            "completed_missions": self.completed_missions,
            "total_hours_volunteered": self.total_hours_volunteered,
            "impact_score": self.impact_score,
            "reputation_score": self.reputation_score,
            "badges": self.badges,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                "phone": self.phone,
                "email_verified": self.email_verified,
                "permissions": self.permissions,
                "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
            })
        
        return data


class UserSession(Base):
    """
    Session utilisateur pour JWT tokens
    """
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Token info
    access_token = Column(String(500))
    refresh_token = Column(String(500))
    
    # Informations de la session
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    device_info = Column(JSON)
    
    # Géolocalisation
    country = Column(String(100))
    city = Column(String(100))
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    
    # Statut
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
