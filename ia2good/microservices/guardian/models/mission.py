"""
Mission Model avec support multilingue (644+ langues)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class MissionStatus(str, enum.Enum):
    """Statuts possibles d'une mission"""
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MissionType(str, enum.Enum):
    """Types de missions disponibles"""
    HUMANITARIAN = "humanitarian"
    ENVIRONMENTAL = "environmental"
    EDUCATION = "education"
    HEALTH = "health"
    COMMUNITY = "community"
    EMERGENCY = "emergency"
    DEVELOPMENT = "development"
    OTHER = "other"


class Mission(Base):
    """
    Modèle de mission avec support multilingue (644+ langues)
    Tous les champs de texte sont traduits dans toutes les langues supportées par IACherie
    """
    __tablename__ = "missions"
    
    # ID et métadonnées
    id = Column(Integer, primary_key=True, index=True)
    mission_code = Column(String(50), unique=True, index=True)  # Ex: "MISS-2024-001"
    
    # Informations multilingues (JSON avec 644 langues)
    # Format: {"EN": "text in english", "FR": "texte en français", "AR": "نص بالعربية", ...}
    title_translations = Column(JSON, nullable=False)  # Titre dans toutes les langues
    description_translations = Column(JSON, nullable=False)  # Description dans toutes les langues
    requirements_translations = Column(JSON)  # Prérequis dans toutes les langues
    objectives_translations = Column(JSON)  # Objectifs dans toutes les langues
    
    # Langue originale de la mission
    original_language = Column(String(10), default="EN")
    
    # Type et statut
    mission_type = Column(SQLEnum(MissionType), default=MissionType.HUMANITARIAN)
    status = Column(SQLEnum(MissionStatus), default=MissionStatus.DRAFT)
    
    # Localisation géographique
    country = Column(String(100))
    city = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    location_translations = Column(JSON)  # Localisation traduite
    
    # Coordinateur de la mission
    coordinator_id = Column(Integer, ForeignKey("users.id"))
    coordinator = relationship("User", back_populates="coordinated_missions")
    
    # Organisation partenaire
    partner_organization = Column(String(200))
    partner_organization_translations = Column(JSON)
    
    # Dates et durée
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration_days = Column(Integer)
    
    # Besoins en volontaires
    volunteers_needed = Column(Integer, default=1)
    volunteers_registered = Column(Integer, default=0)
    volunteers_confirmed = Column(Integer, default=0)
    
    # Compétences requises (multilingue)
    skills_required = Column(JSON)  # Liste de compétences traduites
    
    # Budget et financement
    budget_required = Column(Float, default=0.0)
    budget_secured = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    
    # Urgence et priorité
    is_urgent = Column(Boolean, default=False)
    priority_level = Column(Integer, default=3)  # 1=basse, 3=moyenne, 5=haute
    
    # Médias
    images = Column(JSON)  # Liste d'URLs d'images
    videos = Column(JSON)  # Liste d'URLs de vidéos
    documents = Column(JSON)  # Liste de documents (avec traductions)
    
    # Indicateurs de succès (multilingue)
    success_indicators_translations = Column(JSON)
    
    # Impact attendu (multilingue)
    expected_impact_translations = Column(JSON)
    
    # Risques identifiés (multilingue)
    identified_risks_translations = Column(JSON)
    
    # Mesures de sécurité (multilingue)
    safety_measures_translations = Column(JSON)
    
    # Contact d'urgence
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(50))
    emergency_contact_email = Column(String(200))
    
    # Réseaux sociaux et communication
    social_media_links = Column(JSON)
    hashtags = Column(JSON)
    
    # Certification et validation
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Statistiques
    views_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    applications_count = Column(Integer, default=0)
    
    # IA et recommandations
    ai_recommendations = Column(JSON)  # Recommandations IA
    ai_risk_score = Column(Float)  # Score de risque calculé par IA (0-1)
    ai_impact_score = Column(Float)  # Score d'impact prédit par IA (0-1)
    
    # Accessibilité
    accessibility_features = Column(JSON)  # Fonctionnalités d'accessibilité
    disability_friendly = Column(Boolean, default=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relations
    volunteers = relationship("Volunteer", back_populates="mission")
    chat_rooms = relationship("ChatRoom", back_populates="mission")
    files = relationship("FileUpload", back_populates="mission")
    streams = relationship("LiveStream", back_populates="mission")
    
    def get_title(self, language: str = "EN") -> str:
        """Obtient le titre dans la langue demandée"""
        if not self.title_translations:
            return ""
        return self.title_translations.get(language.upper(), 
                                           self.title_translations.get("EN", ""))
    
    def get_description(self, language: str = "EN") -> str:
        """Obtient la description dans la langue demandée"""
        if not self.description_translations:
            return ""
        return self.description_translations.get(language.upper(),
                                                 self.description_translations.get("EN", ""))
    
    def to_dict(self, language: str = "EN") -> dict:
        """Convertit la mission en dictionnaire avec traductions"""
        return {
            "id": self.id,
            "mission_code": self.mission_code,
            "title": self.get_title(language),
            "description": self.get_description(language),
            "title_translations": self.title_translations,
            "description_translations": self.description_translations,
            "original_language": self.original_language,
            "mission_type": self.mission_type.value if self.mission_type else None,
            "status": self.status.value if self.status else None,
            "country": self.country,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "coordinator_id": self.coordinator_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "duration_days": self.duration_days,
            "volunteers_needed": self.volunteers_needed,
            "volunteers_registered": self.volunteers_registered,
            "volunteers_confirmed": self.volunteers_confirmed,
            "budget_required": self.budget_required,
            "budget_secured": self.budget_secured,
            "currency": self.currency,
            "is_urgent": self.is_urgent,
            "priority_level": self.priority_level,
            "images": self.images,
            "videos": self.videos,
            "is_verified": self.is_verified,
            "views_count": self.views_count,
            "shares_count": self.shares_count,
            "ai_risk_score": self.ai_risk_score,
            "ai_impact_score": self.ai_impact_score,
            "disability_friendly": self.disability_friendly,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
