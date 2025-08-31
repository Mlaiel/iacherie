"""User Profiles Database Models and Operations

Gestion complète des profils utilisateurs avec support multi-tenant
et intégration IA pour personnalisation et recommandations.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & User Experience Specialist

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle de Fahed Mlaiel.
Toute utilisation, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de 
poursuites judiciaires selon la loi allemande.
Email: mlaiel@live.de pour autorisation d'utilisation.
"""from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey, Decimal
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum as PyEnum
import logging
import uuid
import hashlib

logger = logging.getLogger(__name__)

Base = declarative_base()


class UserType(PyEnum):
    """Types d'utilisateurs dans la plateforme."""    INDIVIDUAL = "individual"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    CREATOR = "creator"
    MANAGER = "manager"
    AGENCY = "agency"


class UserStatus(PyEnum):
    """Statuts possibles des utilisateurs."""    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class OnboardingStep(PyEnum):
    """Étapes du processus d'onboarding."""    REGISTRATION = "registration"
    EMAIL_VERIFICATION = "email_verification"
    PROFILE_SETUP = "profile_setup"
    CREATOR_SETUP = "creator_setup"
    PLATFORM_INTEGRATION = "platform_integration"
    AI_PREFERENCES = "ai_preferences"
    COMPLETED = "completed"


class NotificationPreference(PyEnum):
    """Préférences de notification."""    ALL = "all"
    IMPORTANT_ONLY = "important_only"
    MINIMAL = "minimal"
    DISABLED = "disabled"


class User(Base):
    """    Modèle principal des utilisateurs avec support multi-tenant.
    Intègre l'IA pour personnalisation et recommandations.
    """    __tablename__ = "users"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, default="default")
    user_uuid = Column(String, unique=True, nullable=False)
    
    # Informations de base
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    display_name = Column(String(200))
    
    # Type et statut
    user_type = Column(Enum(UserType), default=UserType.INDIVIDUAL)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    onboarding_step = Column(Enum(OnboardingStep), default=OnboardingStep.REGISTRATION)
    
    # Informations géographiques
    country_code = Column(String(3))
    timezone = Column(String(50))
    language_preference = Column(String(10), default="en")
    locale = Column(String(10), default="en_US")
    
    # Avatar et profil
    avatar_url = Column(String(500))
    banner_url = Column(String(500))
    bio = Column(Text)
    website_url = Column(String(500))
    
    # Préférences utilisateur
    notification_preferences = Column(JSON)
    privacy_settings = Column(JSON)
    ai_preferences = Column(JSON)
    theme_preferences = Column(JSON)
    
    # Sécurité et vérification
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    identity_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    
    # Dates importantes
    email_verified_at = Column(DateTime)
    last_login_at = Column(DateTime)
    last_activity_at = Column(DateTime)
    password_changed_at = Column(DateTime)
    
    # Onboarding et activation
    onboarding_completed_at = Column(DateTime)
    activation_token = Column(String(255))
    activation_expires_at = Column(DateTime)
    
    # Métriques utilisateur
    login_count = Column(Integer, default=0)
    session_duration_total = Column(Integer, default=0)  # en secondes
    feature_usage_stats = Column(JSON)
    ai_interaction_score = Column(Decimal(5, 2), default=0.00)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    
    # Relations
    creator_account = relationship("CreatorAccount", back_populates="user", uselist=False)
    subscriptions = relationship("UserSubscription", back_populates="user")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    security_logs = relationship("UserSecurityLog", back_populates="user")

    def __repr__(self):
        return f"<User({self.username}, {self.email})>"
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet de l'utilisateur."""        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.username
    
    @property
    def is_creator(self) -> bool:
        """Vérifie si l'utilisateur est un créateur."""        return self.creator_account is not None
    
    @property
    def avatar_hash(self) -> str:
        """Génère un hash pour l'avatar par défaut."""        return hashlib.md5(self.email.encode()).hexdigest()


class UserProfile(Base):
    """    Profil détaillé de l'utilisateur avec informations personnelles et professionnelles.
    """    __tablename__ = "user_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Informations personnelles détaillées
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    profession = Column(String(200))
    company = Column(String(200))
    industry = Column(String(100))
    
    # Coordonnées
    phone = Column(String(50))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    # Réseaux sociaux
    social_media_links = Column(JSON)
    linkedin_profile = Column(String(500))
    twitter_handle = Column(String(100))
    instagram_handle = Column(String(100))
    
    # Centres d'intérêt et compétences
    interests = Column(JSON)
    skills = Column(JSON)
    languages_spoken = Column(JSON)
    experience_level = Column(String(50))
    
    # Configuration IA personnalisée
    ai_assistant_name = Column(String(100))
    ai_personality_type = Column(String(50))
    ai_response_style = Column(String(50))
    content_creation_preferences = Column(JSON)
    
    # Objectifs et préférences
    platform_goals = Column(JSON)
    target_audience = Column(JSON)
    content_strategy = Column(JSON)
    collaboration_interests = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile({self.user_id})>"


class UserActivity(Base):
    """    Suivi des activités utilisateur pour analytics et personnalisation IA.
    """    __tablename__ = "user_activities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Informations d'activité
    activity_type = Column(String(100), nullable=False)  # "login", "upload", "collaboration"
    activity_category = Column(String(50))  # "content", "social", "monetization"
    activity_description = Column(Text)
    
    # Contexte technique
    platform = Column(String(50))  # "web", "mobile", "api"
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    session_id = Column(String(255))
    
    # Données d'activité
    activity_data = Column(JSON)  # Données spécifiques à l'activité
    duration_seconds = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Géolocalisation
    location_country = Column(String(3))
    location_city = Column(String(100))
    location_coordinates = Column(JSON)  # {"lat": 48.8566, "lng": 2.3522}
    
    # AI Analytics
    ai_engagement_score = Column(Decimal(5, 2))
    content_interaction_type = Column(String(50))
    recommendation_followed = Column(Boolean)
    feature_discovery = Column(JSON)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<UserActivity({self.activity_type}, {self.created_at})>"


class UserSession(Base):
    """    Gestion des sessions utilisateur avec analytics détaillés.
    """    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Informations de session
    session_token = Column(String(255), unique=True, nullable=False)
    device_fingerprint = Column(String(255))
    device_type = Column(String(50))  # "desktop", "mobile", "tablet"
    browser = Column(String(100))
    operating_system = Column(String(100))
    
    # Géolocalisation
    ip_address = Column(String(45))
    country_code = Column(String(3))
    city = Column(String(100))
    timezone_detected = Column(String(50))
    
    # Durée et activité
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    is_active = Column(Boolean, default=True)
    
    # Analytics de session
    pages_visited = Column(Integer, default=0)
    features_used = Column(JSON)  # Features utilisées durant la session
    ai_interactions = Column(Integer, default=0)
    content_uploaded = Column(Integer, default=0)
    collaborations_initiated = Column(Integer, default=0)
    
    # Sécurité
    is_suspicious = Column(Boolean, default=False)
    security_warnings = Column(JSON)
    failed_login_attempts = Column(Integer, default=0)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="sessions")

    def end_session(self):
        """Terminer la session."""        self.ended_at = datetime.utcnow()
        self.is_active = False
        if self.started_at:
            self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())

    def __repr__(self):
        return f"<UserSession({self.user_id}, {self.started_at})>"


class UserSecurityLog(Base):
    """    Logs de sécurité pour traçabilité et détection d'anomalies.
    """    __tablename__ = "user_security_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Type d'événement de sécurité
    event_type = Column(String(100), nullable=False)  # "login_success", "login_failed", "password_change"
    severity_level = Column(String(20), default="info")  # "info", "warning", "critical"
    description = Column(Text)
    
    # Contexte technique
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    country_code = Column(String(3))
    device_fingerprint = Column(String(255))
    
    # Détails de l'événement
    event_data = Column(JSON)  # Données spécifiques à l'événement
    success = Column(Boolean, default=True)
    risk_score = Column(Decimal(3, 2), default=0.00)  # Score de risque 0-1
    
    # Actions automatiques
    action_taken = Column(String(100))  # "none", "rate_limit", "account_lock"
    requires_review = Column(Boolean, default=False)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="security_logs")

    def __repr__(self):
        return f"<UserSecurityLog({self.event_type}, {self.severity_level})>"


class UserAIProfile(Base):
    """    Profil IA pour personnalisation avancée et recommandations.
    """    __tablename__ = "user_ai_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Embeddings et vecteurs IA
    content_embedding = Column(JSON)  # Embedding des préférences de contenu
    behavior_embedding = Column(JSON)  # Embedding des patterns comportementaux
    collaboration_embedding = Column(JSON)  # Embedding des préférences de collaboration
    
    # Scores et métriques IA
    creativity_score = Column(Decimal(5, 2), default=0.00)
    engagement_propensity = Column(Decimal(3, 2), default=0.00)
    collaboration_compatibility = Column(Decimal(3, 2), default=0.00)
    monetization_readiness = Column(Decimal(3, 2), default=0.00)
    
    # Patterns comportementaux
    usage_patterns = Column(JSON)  # Patterns d'utilisation détectés
    peak_activity_hours = Column(JSON)  # Heures de pointe d'activité
    preferred_content_types = Column(JSON)  # Types de contenu préférés
    interaction_style = Column(String(50))  # "explorer", "focused", "social"
    
    # Recommandations personnalisées
    recommendation_weights = Column(JSON)  # Poids pour les algorithmes de recommandation
    exclusion_filters = Column(JSON)  # Filtres d'exclusion
    boost_factors = Column(JSON)  # Facteurs de boost
    
    # Apprentissage et adaptation
    model_version = Column(String(50))
    last_training_date = Column(DateTime)
    feedback_incorporated = Column(Integer, default=0)
    accuracy_metrics = Column(JSON)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="ai_profile")

    def update_embeddings(self, content_data: Dict[str, Any]):
        """Mettre à jour les embeddings basés sur les nouvelles données."""        # Implémentation simplifiée - à enrichir avec ML réel
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<UserAIProfile({self.user_id})>"


class UserRepository:
    """    Repository pour la gestion des utilisateurs avec fonctionnalités avancées.
    """    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Créer un nouvel utilisateur avec profil complet."""        try:
            # Vérifier l'unicité de l'email et du username
            existing_user = self.db.query(User).filter(
                (User.email == user_data['email']) | 
                (User.username == user_data['username'])
            ).first()
            
            if existing_user:
                raise ValueError("Email ou nom d'utilisateur déjà utilisé")
            
            # Créer l'utilisateur principal
            user = User(**user_data)
            self.db.add(user)
            self.db.flush()  # Pour obtenir l'ID
            
            # Créer le profil utilisateur
            profile = UserProfile(user_id=user.id)
            self.db.add(profile)
            
            # Créer le profil IA
            ai_profile = UserAIProfile(user_id=user.id)
            self.db.add(ai_profile)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Utilisateur créé: {user.username} ({user.email})")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création utilisateur: {str(e)}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupérer un utilisateur par email."""        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupérer un utilisateur par nom d'utilisateur."""        return self.db.query(User).filter(User.username == username).first()
    
    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Authentifier un utilisateur par email/username et mot de passe."""        try:
            user = self.db.query(User).filter(
                (User.email == identifier) | (User.username == identifier)
            ).first()
            
            if user and user.verify_password(password):
                # Enregistrer la connexion
                self.log_security_event(user.id, "login_success", {"ip": "unknown"})
                user.last_login_at = datetime.utcnow()
                user.login_count += 1
                self.db.commit()
                return user
            else:
                # Enregistrer l'échec
                if user:
                    self.log_security_event(user.id, "login_failed", {"reason": "invalid_password"})
                return None
                
        except Exception as e:
            logger.error(f"Erreur authentification: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Mettre à jour le profil utilisateur."""        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Mettre à jour les champs utilisateur
            for key, value in profile_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            user.calculate_profile_completion()
            
            self.db.commit()
            logger.info(f"Profil mis à jour: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur mise à jour profil: {str(e)}")
            return False
    
    def create_user_session(self, user_id: str, session_data: Dict[str, Any]) -> UserSession:
        """Créer une nouvelle session utilisateur."""        try:
            session = UserSession(
                user_id=user_id,
                session_token=str(uuid.uuid4()),
                **session_data
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            return session
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création session: {str(e)}")
            raise
    
    def log_user_activity(self, user_id: str, activity_type: str, activity_data: Dict[str, Any] = None) -> UserActivity:
        """Enregistrer une activité utilisateur."""        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                activity_data=activity_data or {}
            )
            self.db.add(activity)
            self.db.commit()
            
            return activity
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur log activité: {str(e)}")
            raise
    
    def log_security_event(self, user_id: str, event_type: str, event_data: Dict[str, Any] = None) -> UserSecurityLog:
        """Enregistrer un événement de sécurité."""        try:
            security_log = UserSecurityLog(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data or {}
            )
            self.db.add(security_log)
            self.db.commit()
            
            return security_log
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur log sécurité: {str(e)}")
            raise
    
    def get_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Obtenir les analytics d'un utilisateur."""        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Activités dans la période
            activities = self.db.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.created_at >= start_date
            ).all()
            
            # Sessions dans la période
            sessions = self.db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.started_at >= start_date
            ).all()
            
            # Calculer les métriques
            total_activities = len(activities)
            total_sessions = len(sessions)
            avg_session_duration = 0
            
            if sessions:
                durations = [s.duration_seconds for s in sessions if s.duration_seconds]
                avg_session_duration = sum(durations) / len(durations) if durations else 0
            
            # Types d'activités
            activity_types = {}
            for activity in activities:
                activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
            
            return {
                "period_days": days,
                "total_activities": total_activities,
                "total_sessions": total_sessions,
                "average_session_duration": avg_session_duration,
                "activity_breakdown": activity_types,
                "most_active_day": self._get_most_active_day(activities),
                "engagement_score": self._calculate_engagement_score(activities, sessions)
            }
            
        except Exception as e:
            logger.error(f"Erreur analytics utilisateur: {str(e)}")
            return {}
    
    def update_ai_profile(self, user_id: str, ai_data: Dict[str, Any]) -> bool:
        """Mettre à jour le profil IA d'un utilisateur."""        try:
            ai_profile = self.db.query(UserAIProfile).filter(
                UserAIProfile.user_id == user_id
            ).first()
            
            if not ai_profile:
                ai_profile = UserAIProfile(user_id=user_id)
                self.db.add(ai_profile)
            
            for key, value in ai_data.items():
                if hasattr(ai_profile, key):
                    setattr(ai_profile, key, value)
            
            ai_profile.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Profil IA mis à jour: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur mise à jour IA: {str(e)}")
            return False
    
    def get_users_by_criteria(self, criteria: Dict[str, Any], limit: int = 100) -> List[User]:
        """Rechercher des utilisateurs selon des critères."""        try:
            query = self.db.query(User)
            
            if 'user_type' in criteria:
                query = query.filter(User.user_type == criteria['user_type'])
            
            if 'status' in criteria:
                query = query.filter(User.status == criteria['status'])
            
            if 'country_code' in criteria:
                query = query.filter(User.country_code == criteria['country_code'])
            
            if 'created_after' in criteria:
                query = query.filter(User.created_at >= criteria['created_after'])
            
            if 'monetization_enabled' in criteria:
                query = query.filter(User.monetization_enabled == criteria['monetization_enabled'])
            
            users = query.limit(limit).all()
            return users
            
        except Exception as e:
            logger.error(f"Erreur recherche utilisateurs: {str(e)}")
            return []
    
    def _get_most_active_day(self, activities: List[UserActivity]) -> str:
        """Déterminer le jour le plus actif."""        if not activities:
            return "N/A"
        
        day_counts = {}
        for activity in activities:
            day = activity.created_at.strftime("%A")
            day_counts[day] = day_counts.get(day, 0) + 1
        
        return max(day_counts, key=day_counts.get) if day_counts else "N/A"
    
    def _calculate_engagement_score(self, activities: List[UserActivity], sessions: List[UserSession]) -> float:
        """Calculer un score d'engagement utilisateur."""        if not activities and not sessions:
            return 0.0
        
        # Score basé sur la fréquence et diversité d'activités
        activity_score = min(len(activities) / 30, 1.0) * 0.5  # Max 30 activités par mois
        
        # Score basé sur la durée des sessions
        session_score = 0
        if sessions:
            avg_duration = sum(s.duration_seconds or 0 for s in sessions) / len(sessions)
            session_score = min(avg_duration / 3600, 1.0) * 0.3  # Max 1h par session
        
        # Score basé sur la diversité des activités
        activity_types = set(a.activity_type for a in activities)
        diversity_score = min(len(activity_types) / 10, 1.0) * 0.2  # Max 10 types différents
        
        return (activity_score + session_score + diversity_score) * 100
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Métriques de session
    pages_visited = Column(Integer, default=0)
    actions_performed = Column(Integer, default=0)
    features_used = Column(JSON)
    ai_interactions = Column(Integer, default=0)
    
    # État de session
    is_active = Column(Boolean, default=True)
    logout_type = Column(String(50))  # "manual", "timeout", "forced"
    
    # Relations
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession({self.session_token[:8]}..., {self.started_at})>"


class UserRepository:
    """    Repository pattern pour les opérations sur les utilisateurs.
    Implémentation professionnelle avec gestion d'erreurs et analytics.
    """    
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """        Crée un nouvel utilisateur avec validation complète.
        
        Args:
            user_data: Données de l'utilisateur
            
        Returns:
            User: Utilisateur créé
            
        Raises:
            ValueError: Si les données sont invalides
            Exception: En cas d'erreur de création
        """        try:
            # Validation des données obligatoires
            required_fields = ['email', 'username']
            for field in required_fields:
                if field not in user_data:
                    raise ValueError(f"Champ obligatoire manquant: {field}")
            
            # Vérification unicité email et username
            if self.get_user_by_email(user_data['email']):
                raise ValueError("Email déjà utilisé")
            
            if self.get_user_by_username(user_data['username']):
                raise ValueError("Nom d'utilisateur déjà utilisé")
            
            # Génération UUID unique
            user_uuid = str(uuid.uuid4())
            
            # Création de l'utilisateur
            user = User(
                user_uuid=user_uuid,
                email=user_data['email'].lower(),
                username=user_data['username'],
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                display_name=user_data.get('display_name'),
                user_type=UserType(user_data.get('user_type', 'individual')),
                country_code=user_data.get('country_code'),
                timezone=user_data.get('timezone'),
                language_preference=user_data.get('language_preference', 'en'),
                tenant_id=user_data.get('tenant_id', 'default')
            )
            
            self.session.add(user)
            self.session.commit()
            
            self.logger.info(f"Utilisateur créé: {user.id}")
            return user
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur création utilisateur: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Récupère un utilisateur par son ID."""        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email."""        return self.session.query(User).filter(User.email == email.lower()).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par son nom d'utilisateur."""        return self.session.query(User).filter(User.username == username).first()
    
    def update_user_status(self, user_id: str, status: UserStatus) -> bool:
        """        Met à jour le statut d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            status: Nouveau statut
            
        Returns:
            bool: True si mis à jour avec succès
        """        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.status = status
            user.updated_at = datetime.utcnow()
            
            self.session.commit()
            self.logger.info(f"Statut utilisateur mis à jour: {user_id} -> {status.value}")
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour statut: {str(e)}")
            return False
    
    def complete_onboarding_step(self, user_id: str, step: OnboardingStep) -> bool:
        """        Marque une étape d'onboarding comme complétée.
        
        Args:
            user_id: ID de l'utilisateur
            step: Étape à marquer comme complétée
            
        Returns:
            bool: True si mis à jour avec succès
        """        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.onboarding_step = step
            user.updated_at = datetime.utcnow()
            
            if step == OnboardingStep.COMPLETED:
                user.onboarding_completed_at = datetime.utcnow()
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur mise à jour onboarding: {str(e)}")
            return False
    
    def track_user_activity(self, user_id: str, activity_data: Dict[str, Any]) -> bool:
        """        Enregistre une activité utilisateur pour analytics.
        
        Args:
            user_id: ID de l'utilisateur
            activity_data: Données d'activité
            
        Returns:
            bool: True si enregistré avec succès
        """        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_data['activity_type'],
                activity_category=activity_data.get('activity_category'),
                activity_description=activity_data.get('activity_description'),
                platform=activity_data.get('platform'),
                user_agent=activity_data.get('user_agent'),
                ip_address=activity_data.get('ip_address'),
                activity_data=activity_data.get('activity_data', {}),
                duration_seconds=activity_data.get('duration_seconds'),
                success=activity_data.get('success', True)
            )
            
            self.session.add(activity)
            
            # Mise à jour de la dernière activité
            user = self.get_user_by_id(user_id)
            if user:
                user.last_activity_at = datetime.utcnow()
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur enregistrement activité: {str(e)}")
            return False
    
    def get_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """        Retourne les analytics d'un utilisateur sur une période donnée.
        
        Args:
            user_id: ID de l'utilisateur
            days: Nombre de jours à analyser
            
        Returns:
            Dict[str, Any]: Analytics utilisateur
        """        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Activités récentes
        activities = self.session.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.created_at >= start_date
        ).all()
        
        # Statistiques d'activité
        activity_stats = {}
        for activity in activities:
            activity_type = activity.activity_type
            if activity_type not in activity_stats:
                activity_stats[activity_type] = 0
            activity_stats[activity_type] += 1
        
        # Sessions récentes
        sessions = self.session.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.started_at >= start_date
        ).all()
        
        total_session_time = sum(
            s.duration_seconds or 0 for s in sessions if s.duration_seconds
        )
        
        return {
            'period_days': days,
            'total_activities': len(activities),
            'activity_breakdown': activity_stats,
            'total_sessions': len(sessions),
            'total_session_time_seconds': total_session_time,
            'average_session_time_seconds': total_session_time / len(sessions) if sessions else 0,
            'most_used_platform': self._get_most_used_platform(activities),
            'last_activity': activities[-1].created_at.isoformat() if activities else None
        }
    
    def _get_most_used_platform(self, activities: List[UserActivity]) -> str:
        """Helper pour déterminer la plateforme la plus utilisée."""        platform_counts = {}
        for activity in activities:
            platform = activity.platform or 'unknown'
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        if not platform_counts:
            return 'unknown'
        
        return max(platform_counts, key=platform_counts.get)


# Configuration des relations
User.profile = relationship("UserProfile", back_populates="user", uselist=False)
User.activities = relationship("UserActivity", back_populates="user")
User.sessions = relationship("UserSession", back_populates="user")
