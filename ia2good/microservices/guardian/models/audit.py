"""
Audit Log Model avec support multilingue (644+ langues)
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class AuditEventType(str, enum.Enum):
    """Types d'événements audités"""
    # Authentification
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    
    # Missions
    MISSION_CREATED = "mission_created"
    MISSION_UPDATED = "mission_updated"
    MISSION_DELETED = "mission_deleted"
    MISSION_PUBLISHED = "mission_published"
    MISSION_COMPLETED = "mission_completed"
    
    # Volontaires
    VOLUNTEER_APPLIED = "volunteer_applied"
    VOLUNTEER_ACCEPTED = "volunteer_accepted"
    VOLUNTEER_REJECTED = "volunteer_rejected"
    VOLUNTEER_WITHDRAWN = "volunteer_withdrawn"
    
    # Chat et messages
    MESSAGE_SENT = "message_sent"
    MESSAGE_DELETED = "message_deleted"
    MESSAGE_EDITED = "message_edited"
    MESSAGE_FLAGGED = "message_flagged"
    
    # Fichiers
    FILE_UPLOADED = "file_uploaded"
    FILE_DOWNLOADED = "file_downloaded"
    FILE_DELETED = "file_deleted"
    
    # Streaming
    STREAM_STARTED = "stream_started"
    STREAM_ENDED = "stream_ended"
    
    # Modération
    CONTENT_MODERATED = "content_moderated"
    USER_BANNED = "user_banned"
    USER_UNBANNED = "user_unbanned"
    USER_WARNED = "user_warned"
    
    # Sécurité
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    
    # Administration
    SETTINGS_CHANGED = "settings_changed"
    USER_ROLE_CHANGED = "user_role_changed"
    PERMISSION_CHANGED = "permission_changed"


class AuditSeverity(str, enum.Enum):
    """Niveaux de sévérité"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base):
    """
    Journal d'audit avec descriptions multilingues
    """
    __tablename__ = "audit_logs"
    
    # ID et métadonnées
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(50), unique=True, index=True)
    
    # Type et sévérité
    event_type = Column(SQLEnum(AuditEventType), index=True)
    severity = Column(SQLEnum(AuditSeverity), default=AuditSeverity.INFO, index=True)
    
    # Utilisateur concerné
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user = relationship("User")
    
    # Description de l'événement (multilingue)
    description_translations = Column(JSON)  # {"EN": "User logged in", "FR": "Utilisateur connecté"}
    original_language = Column(String(10), default="EN")
    
    # Détails techniques (non traduits)
    details = Column(JSON)  # Détails techniques de l'événement
    
    # Informations de la requête
    ip_address = Column(String(45))  # Support IPv4 et IPv6
    user_agent = Column(String(500))
    request_method = Column(String(10))
    request_path = Column(String(500))
    request_params = Column(JSON)
    
    # Réponse
    response_status = Column(Integer)
    response_time_ms = Column(Integer)  # Temps de réponse en ms
    
    # Géolocalisation
    country = Column(String(100))
    city = Column(String(100))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Entité affectée
    entity_type = Column(String(50))  # Ex: "mission", "volunteer", "message"
    entity_id = Column(Integer)
    
    # Tags pour filtrage
    tags = Column(JSON)  # Ex: ["security", "login", "failed"]
    
    # Métadonnées
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def get_description(self, language: str = "EN") -> str:
        """Obtient la description dans la langue demandée"""
        if not self.description_translations:
            return ""
        return self.description_translations.get(language.upper(),
                                                 self.description_translations.get("EN", ""))
    
    def to_dict(self, language: str = "EN") -> dict:
        return {
            "id": self.id,
            "log_id": self.log_id,
            "event_type": self.event_type.value if self.event_type else None,
            "severity": self.severity.value if self.severity else None,
            "user_id": self.user_id,
            "description": self.get_description(language),
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "country": self.country,
            "city": self.city,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
