"""User Preferences Database Models and Operations

Gestion complète des préférences utilisateur avec IA personnalisée,
recommandations et optimisation d'expérience utilisateur.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & UX Personalization Specialist

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle de Fahed Mlaiel.
Toute utilisation, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de 
poursuites judiciaires selon la loi allemande.
Email: mlaiel@live.de pour autorisation d'utilisation.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey, Decimal
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum as PyEnum
import logging
import uuid
import json

logger = logging.getLogger(__name__)

Base = declarative_base()


class NotificationChannel(PyEnum):
    """
Canaux de notification disponibles."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationFrequency(PyEnum):
    """Fréquences de notification."""

    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    DISABLED = "disabled"


class PrivacyLevel(PyEnum):
    """Niveaux de confidentialité."""

    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"
    CUSTOM = "custom"


class AIPersonality(PyEnum):
    """Types de personnalité IA."""

    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    CASUAL = "casual"
    MENTOR = "mentor"


class ContentGenrePreference(PyEnum):
    """Préférences de genre de contenu."""

    MUSIC = "music"
    PODCAST = "podcast"
    VIDEO = "video"
    BLOG = "blog"
    PHOTOGRAPHY = "photography"
    ART = "art"
    COMEDY = "comedy"


class UserPreferences(Base):
    """
    Préférences principales de l'utilisateur avec IA personnalisée.
    """
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Préférences générales
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    date_format = Column(String(20), default="YYYY-MM-DD")
    time_format = Column(String(10), default="24h")
    currency_preference = Column(String(3), default="EUR")
    
    # Thème et interface
    theme = Column(String(20), default="light")  # "light", "dark", "auto"
    color_scheme = Column(String(50), default="default")
    dashboard_layout = Column(String(50), default="default")
    sidebar_collapsed = Column(Boolean, default=False)
    animations_enabled = Column(Boolean, default=True)
    
    # IA et personnalisation
    ai_assistant_enabled = Column(Boolean, default=True)
    ai_personality = Column(Enum(AIPersonality), default=AIPersonality.PROFESSIONAL)
    ai_response_style = Column(String(50), default="balanced")  # "brief", "detailed", "balanced"
    ai_suggestions_enabled = Column(Boolean, default=True)
    ai_auto_optimization = Column(Boolean, default=False)
    
    # Contenu et recommandations
    content_discovery_enabled = Column(Boolean, default=True)
    collaboration_suggestions = Column(Boolean, default=True)
    trending_alerts = Column(Boolean, default=True)
    genre_preferences = Column(JSON)  # Liste des genres préférés
    content_rating_preference = Column(String(10), default="all")
    
    # Workflow et automatisation
    auto_save_enabled = Column(Boolean, default=True)
    auto_backup_enabled = Column(Boolean, default=True)
    batch_processing_enabled = Column(Boolean, default=False)
    smart_scheduling = Column(Boolean, default=False)
    auto_tagging = Column(Boolean, default=True)
    
    # Analytics et métriques
    analytics_level = Column(String(20), default="standard")  # "basic", "standard", "advanced"
    performance_tracking = Column(Boolean, default=True)
    audience_insights = Column(Boolean, default=True)
    revenue_tracking = Column(Boolean, default=True)
    competitor_analysis = Column(Boolean, default=False)
    
    # Intégrations et APIs
    platform_sync_enabled = Column(Boolean, default=True)
    auto_posting_enabled = Column(Boolean, default=False)
    cross_platform_analytics = Column(Boolean, default=True)
    third_party_integrations = Column(JSON)  # Liste des intégrations activées
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime)
    
    # Relations
    user = relationship("User", back_populates="preferences")
    notification_settings = relationship("NotificationSettings", back_populates="preferences", uselist=False)
    privacy_settings = relationship("PrivacySettings", back_populates="preferences", uselist=False)

    def __repr__(self):
        return f"<UserPreferences({self.user_id})>"
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Récupère une préférence spécifique."""
        return getattr(self, key, default)
    
    def update_preference(self, key: str, value: Any) -> bool:
        """
Met à jour une préférence spécifique."""
        if hasattr(self, key):
            setattr(self, key, value)
            self.updated_at = datetime.utcnow()
            return True
        return False


class NotificationSettings(Base):
    """
    Paramètres de notification détaillés par type et canal.
    """
    __tablename__ = "notification_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_preferences_id = Column(String, ForeignKey("user_preferences.id"), nullable=False, unique=True)
    
    # Notifications générales
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    in_app_notifications = Column(Boolean, default=True)
    
    # Fréquences par type
    upload_notifications = Column(Enum(NotificationFrequency), default=NotificationFrequency.REAL_TIME)
    collaboration_notifications = Column(Enum(NotificationFrequency), default=NotificationFrequency.REAL_TIME)
    analytics_reports = Column(Enum(NotificationFrequency), default=NotificationFrequency.WEEKLY)
    revenue_updates = Column(Enum(NotificationFrequency), default=NotificationFrequency.DAILY)
    security_alerts = Column(Enum(NotificationFrequency), default=NotificationFrequency.REAL_TIME)
    
    # Notifications spécialisées
    ai_recommendations = Column(Boolean, default=True)
    content_protection_alerts = Column(Boolean, default=True)
    trending_opportunities = Column(Boolean, default=True)
    platform_updates = Column(Boolean, default=True)
    maintenance_notices = Column(Boolean, default=True)
    
    # Heures de notification
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # "22:00"
    quiet_hours_end = Column(String(5))  # "08:00"
    weekend_notifications = Column(Boolean, default=True)
    
    # Canaux préférés par type
    urgent_channel = Column(Enum(NotificationChannel), default=NotificationChannel.PUSH)
    marketing_channel = Column(Enum(NotificationChannel), default=NotificationChannel.EMAIL)
    updates_channel = Column(Enum(NotificationChannel), default=NotificationChannel.IN_APP)
    
    # Personnalisation
    notification_sound = Column(String(50), default="default")
    email_digest_enabled = Column(Boolean, default=True)
    digest_frequency = Column(Enum(NotificationFrequency), default=NotificationFrequency.DAILY)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    preferences = relationship("UserPreferences", back_populates="notification_settings")

    def __repr__(self):
        return f"<NotificationSettings({self.user_preferences_id})>"


class PrivacySettings(Base):
    """
    Paramètres de confidentialité et sécurité utilisateur.
    """
    __tablename__ = "privacy_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_preferences_id = Column(String, ForeignKey("user_preferences.id"), nullable=False, unique=True)
    
    # Visibilité du profil
    profile_visibility = Column(Enum(PrivacyLevel), default=PrivacyLevel.PUBLIC)
    content_visibility = Column(Enum(PrivacyLevel), default=PrivacyLevel.PUBLIC)
    analytics_visibility = Column(Enum(PrivacyLevel), default=PrivacyLevel.PRIVATE)
    collaboration_visibility = Column(Enum(PrivacyLevel), default=PrivacyLevel.FRIENDS)
    
    # Partage de données
    allow_data_analytics = Column(Boolean, default=True)
    allow_marketing_emails = Column(Boolean, default=False)
    allow_third_party_sharing = Column(Boolean, default=False)
    allow_ai_training = Column(Boolean, default=True)
    allow_recommendation_sharing = Column(Boolean, default=True)
    
    # Sécurité
    two_factor_required = Column(Boolean, default=False)
    login_alerts = Column(Boolean, default=True)
    device_management = Column(Boolean, default=True)
    session_timeout_minutes = Column(Integer, default=120)
    
    # Contenu et modération
    content_filtering_enabled = Column(Boolean, default=True)
    explicit_content_allowed = Column(Boolean, default=False)
    auto_moderation = Column(Boolean, default=True)
    comment_moderation = Column(Boolean, default=False)
    
    # Tracking et cookies
    analytics_cookies = Column(Boolean, default=True)
    marketing_cookies = Column(Boolean, default=False)
    functional_cookies = Column(Boolean, default=True)
    performance_tracking = Column(Boolean, default=True)
    
    # GDPR et conformité
    data_processing_consent = Column(Boolean, default=False)
    marketing_consent = Column(Boolean, default=False)
    data_retention_days = Column(Integer, default=365)
    export_data_format = Column(String(20), default="json")
    
    # Blocages et restrictions
    blocked_users = Column(JSON)  # Liste des utilisateurs bloqués
    blocked_domains = Column(JSON)  # Domaines bloqués
    restricted_features = Column(JSON)  # Fonctionnalités restreintes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    consent_updated_at = Column(DateTime)
    
    # Relations
    preferences = relationship("UserPreferences", back_populates="privacy_settings")

    def __repr__(self):
        return f"<PrivacySettings({self.user_preferences_id})>"


class AIPersonalizationProfile(Base):
    """
    Profil de personnalisation IA avancé avec apprentissage automatique.
    """
    __tablename__ = "ai_personalization_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Profil comportemental
    interaction_patterns = Column(JSON)  # Patterns d'interaction analysés
    content_preferences = Column(JSON)  # Préférences de contenu apprises
    feature_usage_patterns = Column(JSON)  # Utilisation des fonctionnalités
    collaboration_style = Column(JSON)  # Style de collaboration
    
    # Scores IA
    engagement_score = Column(Decimal(5, 2), default=0.00)
    creativity_score = Column(Decimal(5, 2), default=0.00)
    productivity_score = Column(Decimal(5, 2), default=0.00)
    learning_velocity = Column(Decimal(5, 2), default=0.00)
    
    # Recommandations personnalisées
    content_recommendations = Column(JSON)
    collaboration_recommendations = Column(JSON)
    feature_recommendations = Column(JSON)
    optimization_suggestions = Column(JSON)
    
    # Modèles de prédiction
    next_action_predictions = Column(JSON)
    content_performance_predictions = Column(JSON)
    optimal_posting_times = Column(JSON)
    audience_growth_predictions = Column(JSON)
    
    # Apprentissage adaptatif
    learning_rate = Column(Decimal(5, 4), default=0.0100)
    model_confidence = Column(Decimal(5, 2), default=0.00)
    feedback_incorporation_rate = Column(Decimal(5, 4), default=0.0500)
    personalization_strength = Column(Decimal(3, 2), default=0.50)
    
    # Métriques d'efficacité
    recommendation_accuracy = Column(Decimal(5, 2), default=0.00)
    user_satisfaction_score = Column(Decimal(5, 2), default=0.00)
    goal_achievement_rate = Column(Decimal(5, 2), default=0.00)
    time_saved_minutes = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_learning_update = Column(DateTime)
    last_recommendation_update = Column(DateTime)
    
    # Relations
    user = relationship("User", back_populates="ai_profile")

    def __repr__(self):
        return f"<AIPersonalizationProfile({self.user_id})>"


class UserPreferencesRepository:
    """
    Repository pattern pour la gestion des préférences utilisateur.
    Implémentation professionnelle avec IA personnalisée.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    def create_default_preferences(self, user_id: str) -> UserPreferences:
        """
        Crée les préférences par défaut pour un nouvel utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            UserPreferences: Préférences créées
        """
        try:
            # Préférences principales
            preferences = UserPreferences(user_id=user_id)
            self.session.add(preferences)
            self.session.flush()  # Pour obtenir l'ID
            
            # Paramètres de notification par défaut
            notification_settings = NotificationSettings(
                user_preferences_id=preferences.id
            )
            self.session.add(notification_settings)
            
            # Paramètres de confidentialité par défaut
            privacy_settings = PrivacySettings(
                user_preferences_id=preferences.id
            )
            self.session.add(privacy_settings)
            
            # Profil IA personnalisé
            ai_profile = AIPersonalizationProfile(user_id=user_id)
            self.session.add(ai_profile)
            
            self.session.commit()
            
            self.logger.info(f"Préférences par défaut créées pour: {user_id}")
            return preferences
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur création préférences: {str(e)}")
            raise
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Récupère les préférences complètes d'un utilisateur."""
        return self.session.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
    
    def update_preference(self, user_id: str, preference_key: str, value: Any) -> bool:
        """
        Met à jour une préférence spécifique.
        
        Args:
            user_id: ID de l'utilisateur
            preference_key: Clé de la préférence
            value: Nouvelle valeur
            
        Returns:
            bool: True si mis à jour avec succès
        """
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences:
                preferences = self.create_default_preferences(user_id)
            
            if preferences.update_preference(preference_key, value):
                self.session.commit()
                self.logger.info(f"Préférence mise à jour: {user_id}.{preference_key}")
                return True
            
            return False
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour préférence: {str(e)}")
            return False
    
    def update_notification_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """
        Met à jour les paramètres de notification.
        
        Args:
            user_id: ID de l'utilisateur
            settings: Nouveaux paramètres
            
        Returns:
            bool: True si mis à jour avec succès
        """
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences or not preferences.notification_settings:
                return False
            
            notification_settings = preferences.notification_settings
            
            for key, value in settings.items():
                if hasattr(notification_settings, key):
                    setattr(notification_settings, key, value)
            
            notification_settings.updated_at = datetime.utcnow()
            self.session.commit()
            
            self.logger.info(f"Paramètres notification mis à jour: {user_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour notifications: {str(e)}")
            return False
    
    def update_privacy_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """
        Met à jour les paramètres de confidentialité.
        
        Args:
            user_id: ID de l'utilisateur
            settings: Nouveaux paramètres
            
        Returns:
            bool: True si mis à jour avec succès
        """
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences or not preferences.privacy_settings:
                return False
            
            privacy_settings = preferences.privacy_settings
            
            for key, value in settings.items():
                if hasattr(privacy_settings, key):
                    setattr(privacy_settings, key, value)
            
            privacy_settings.updated_at = datetime.utcnow()
            
            # Mise à jour du consentement si nécessaire
            if 'data_processing_consent' in settings or 'marketing_consent' in settings:
                privacy_settings.consent_updated_at = datetime.utcnow()
            
            self.session.commit()
            
            self.logger.info(f"Paramètres confidentialité mis à jour: {user_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour confidentialité: {str(e)}")
            return False
    
    def get_ai_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les recommandations IA personnalisées.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict[str, Any]: Recommandations personnalisées
        """
        ai_profile = self.session.query(AIPersonalizationProfile).filter(
            AIPersonalizationProfile.user_id == user_id
        ).first()
        
        if not ai_profile:
            return {
                'content_recommendations': [],
                'collaboration_recommendations': [],
                'feature_recommendations': [],
                'optimization_suggestions': []
            }
        
        return {
            'content_recommendations': ai_profile.content_recommendations or [],
            'collaboration_recommendations': ai_profile.collaboration_recommendations or [],
            'feature_recommendations': ai_profile.feature_recommendations or [],
            'optimization_suggestions': ai_profile.optimization_suggestions or [],
            'engagement_score': float(ai_profile.engagement_score),
            'last_updated': ai_profile.last_recommendation_update.isoformat() if ai_profile.last_recommendation_update else None
        }
    
    def update_ai_learning(self, user_id: str, interaction_data: Dict[str, Any]) -> bool:
        """
        Met à jour l'apprentissage IA basé sur les interactions utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            interaction_data: Données d'interaction
            
        Returns:
            bool: True si mis à jour avec succès
        """
        try:
            ai_profile = self.session.query(AIPersonalizationProfile).filter(
                AIPersonalizationProfile.user_id == user_id
            ).first()
            
            if not ai_profile:
                ai_profile = AIPersonalizationProfile(user_id=user_id)
                self.session.add(ai_profile)
            
            # Mise à jour des patterns d'interaction
            current_patterns = ai_profile.interaction_patterns or {}
            current_patterns.update(interaction_data.get('patterns', {}))
            ai_profile.interaction_patterns = current_patterns
            
            # Mise à jour des scores
            if 'engagement_score' in interaction_data:
                ai_profile.engagement_score = DecimalType(str(interaction_data['engagement_score']))
            
            # Mise à jour des prédictions
            if 'predictions' in interaction_data:
                ai_profile.next_action_predictions = interaction_data['predictions']
            
            ai_profile.last_learning_update = datetime.utcnow()
            ai_profile.updated_at = datetime.utcnow()
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour apprentissage IA: {str(e)}")
            return False
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Exporte toutes les données utilisateur (conformité GDPR).
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict[str, Any]: Données utilisateur complètes
        """
        preferences = self.get_user_preferences(user_id)
        
        if not preferences:
            return {}
        
        # Données principales
        data = {
            'preferences': {
                'language': preferences.language,
                'timezone': preferences.timezone,
                'theme': preferences.theme,
                'ai_personality': preferences.ai_personality.value if preferences.ai_personality else None,
                'content_discovery_enabled': preferences.content_discovery_enabled,
                'created_at': preferences.created_at.isoformat(),
                'updated_at': preferences.updated_at.isoformat()
            }
        }
        
        # Paramètres de notification
        if preferences.notification_settings:
            data['notification_settings'] = {
                'email_notifications': preferences.notification_settings.email_notifications,
                'push_notifications': preferences.notification_settings.push_notifications,
                'quiet_hours_enabled': preferences.notification_settings.quiet_hours_enabled,
                'digest_frequency': preferences.notification_settings.digest_frequency.value if preferences.notification_settings.digest_frequency else None
            }
        
        # Paramètres de confidentialité
        if preferences.privacy_settings:
            data['privacy_settings'] = {
                'profile_visibility': preferences.privacy_settings.profile_visibility.value if preferences.privacy_settings.profile_visibility else None,
                'data_processing_consent': preferences.privacy_settings.data_processing_consent,
                'marketing_consent': preferences.privacy_settings.marketing_consent,
                'consent_updated_at': preferences.privacy_settings.consent_updated_at.isoformat() if preferences.privacy_settings.consent_updated_at else None
            }
        
        # Profil IA (anonymisé)
        ai_profile = self.session.query(AIPersonalizationProfile).filter(
            AIPersonalizationProfile.user_id == user_id
        ).first()
        
        if ai_profile:
            data['ai_profile'] = {
                'engagement_score': float(ai_profile.engagement_score),
                'creativity_score': float(ai_profile.creativity_score),
                'learning_velocity': float(ai_profile.learning_velocity),
                'recommendation_accuracy': float(ai_profile.recommendation_accuracy)
            }
        
        data['export_timestamp'] = datetime.utcnow().isoformat()
        return data


# Configuration des relations
UserPreferences.notification_settings = relationship("NotificationSettings", back_populates="preferences", uselist=False)
UserPreferences.privacy_settings = relationship("PrivacySettings", back_populates="preferences", uselist=False)
# Note: La relation avec User sera configurée dans le module user_profiles
