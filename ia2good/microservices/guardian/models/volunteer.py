"""
Volunteer Model avec support multilingue (644+ langues)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class VolunteerStatus(str, enum.Enum):
    """Statuts possibles d'un volontaire"""
    APPLIED = "applied"
    REVIEWING = "reviewing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class Volunteer(Base):
    """
    Modèle de volontaire avec support multilingue (644+ langues)
    """
    __tablename__ = "volunteers"
    
    # ID et métadonnées
    id = Column(Integer, primary_key=True, index=True)
    volunteer_code = Column(String(50), unique=True, index=True)  # Ex: "VOL-2024-001"
    
    # Utilisateur associé
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="volunteer_applications")
    
    # Mission associée
    mission_id = Column(Integer, ForeignKey("missions.id"))
    mission = relationship("Mission", back_populates="volunteers")
    
    # Statut
    status = Column(SQLEnum(VolunteerStatus), default=VolunteerStatus.APPLIED)
    
    # Motivation (multilingue)
    motivation_translations = Column(JSON)  # {"EN": "I want to help...", "FR": "Je veux aider..."}
    original_language = Column(String(10), default="EN")
    
    # Compétences (multilingue)
    skills_translations = Column(JSON)  # Compétences dans toutes les langues
    skills_list = Column(JSON)  # Liste de compétences (codes standards)
    
    # Expérience précédente (multilingue)
    experience_translations = Column(JSON)
    years_of_experience = Column(Integer, default=0)
    
    # Langues parlées par le volontaire
    spoken_languages = Column(JSON)  # ["EN", "FR", "ES", "AR"]
    language_proficiency = Column(JSON)  # {"EN": "native", "FR": "fluent", "ES": "intermediate"}
    
    # Disponibilité
    available_from = Column(DateTime)
    available_until = Column(DateTime)
    available_hours_per_week = Column(Integer)
    
    # Localisation
    current_country = Column(String(100))
    current_city = Column(String(100))
    willing_to_relocate = Column(Boolean, default=False)
    willing_to_travel = Column(Boolean, default=True)
    
    # Documents et certifications
    cv_url = Column(String(500))
    cover_letter_url = Column(String(500))
    certificates = Column(JSON)  # Liste de certificats
    references = Column(JSON)  # Références
    
    # Vérifications
    background_check_completed = Column(Boolean, default=False)
    background_check_date = Column(DateTime, nullable=True)
    background_check_status = Column(String(50))
    
    # Formation et préparation
    training_completed = Column(JSON)  # Formations complétées
    training_required = Column(JSON)  # Formations requises
    orientation_completed = Column(Boolean, default=False)
    
    # Évaluation et feedback
    rating = Column(Float)  # Note moyenne (0-5)
    reviews_count = Column(Integer, default=0)
    feedback_translations = Column(JSON)  # Feedback multilingue
    
    # Statistiques
    missions_completed = Column(Integer, default=0)
    total_hours_volunteered = Column(Integer, default=0)
    impact_score = Column(Float)  # Score d'impact (calculé par IA)
    
    # Contact d'urgence
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(50))
    emergency_contact_relationship = Column(String(100))
    
    # Santé et sécurité
    medical_conditions_translations = Column(JSON)
    allergies_translations = Column(JSON)
    special_requirements_translations = Column(JSON)
    insurance_provider = Column(String(200))
    insurance_policy_number = Column(String(100))
    
    # Préférences
    preferred_mission_types = Column(JSON)
    preferred_regions = Column(JSON)
    work_style_preferences = Column(JSON)
    
    # Dates de candidature et décision
    applied_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    decision_made_at = Column(DateTime, nullable=True)
    decision_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    decision_notes_translations = Column(JSON)
    
    # Dates de participation
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    withdrawn_at = Column(DateTime, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    def get_motivation(self, language: str = "EN") -> str:
        """Obtient la motivation dans la langue demandée"""
        if not self.motivation_translations:
            return ""
        return self.motivation_translations.get(language.upper(),
                                               self.motivation_translations.get("EN", ""))
    
    def to_dict(self, language: str = "EN") -> dict:
        """Convertit le volontaire en dictionnaire"""
        return {
            "id": self.id,
            "volunteer_code": self.volunteer_code,
            "user_id": self.user_id,
            "mission_id": self.mission_id,
            "status": self.status.value if self.status else None,
            "motivation": self.get_motivation(language),
            "original_language": self.original_language,
            "spoken_languages": self.spoken_languages,
            "language_proficiency": self.language_proficiency,
            "available_from": self.available_from.isoformat() if self.available_from else None,
            "available_until": self.available_until.isoformat() if self.available_until else None,
            "current_country": self.current_country,
            "current_city": self.current_city,
            "willing_to_relocate": self.willing_to_relocate,
            "background_check_completed": self.background_check_completed,
            "training_completed": self.training_completed,
            "rating": self.rating,
            "reviews_count": self.reviews_count,
            "missions_completed": self.missions_completed,
            "total_hours_volunteered": self.total_hours_volunteered,
            "impact_score": self.impact_score,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
