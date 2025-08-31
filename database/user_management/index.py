"""User Management Database Index File

Point d'entrée principal pour tous les modules de gestion d'utilisateurs
avec initialisation automatique et gestion des relations.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & Database Architecture Specialist

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle de Fahed Mlaiel.
Toute utilisation, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de 
poursuites judiciaires selon la loi allemande.
Email: mlaiel@live.de pour autorisation d'utilisation.
"""
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import os
from contextlib import contextmanager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base déclarative commune
Base = declarative_base()

# Import de tous les modèles - USER MANAGEMENT CORE
from .user_profiles import (
    User, UserProfile, UserActivity, UserSession, UserSecurityLog, UserAIProfile,
    UserRepository, UserType, UserStatus, OnboardingStep, NotificationPreference
)

# Import de tous les modèles - CREATOR ECOSYSTEM
from .creator_accounts import (
    CreatorAccount, CreatorProfile, CreatorMetrics, CreatorAccountRepository,
    CreatorType, CreatorStatus, VerificationLevel
)

# Import de tous les modèles - SUBSCRIPTION & BILLING
from .subscription_management import (
    SubscriptionPlan, UserSubscription, SubscriptionPayment, 
    SubscriptionUsage, SubscriptionRepository,
    SubscriptionTier, SubscriptionStatus, BillingCycle, PaymentStatus
)

# Import de tous les modèles - USER PREFERENCES & AI
from .user_preferences import (
    UserPreferences, NotificationSettings, PrivacySettings, 
    UserPreferencesRepository, ContentPreferences, AIPersonalizationSettings
)

# Import de tous les modèles - SECURITY FRAMEWORK
from .account_security import (
    UserSecurity, SecurityLog, TwoFactorAuth, SecurityRepository,
    LoginAttempt, DeviceFingerprint, SecurityThreat
)

# Import de tous les modèles - COLLABORATION NETWORK
from .collaboration_network import (
    CollaborationNetwork, Collaboration, CollaborationInvitation,
    CollaborationMatchingProfile, CollaborationNetworkRepository,
    CollaborationType, CollaborationStatus, NetworkTier, MatchingAlgorithm
)

# Import de tous les modèles - PLATFORM INTEGRATION
from .platform_integration import (
    PlatformIntegration, ContentDistribution, SynchronizationTask,
    PlatformAnalytics, PlatformIntegrationRepository,
    PlatformType, IntegrationStatus, SyncFrequency, DistributionChannel
)

# Import de tous les modèles - MONETIZATION TRACKING
from .monetization_tracking import (
    RevenueTransaction, RevenueProjection, RevenueAnalytics, PayoutRequest,
    MonetizationRepository, RevenueSource, PaymentStatus, RevenueType, Currency
)


class UserManagementEngine:
    """    Moteur principal de gestion utilisateurs avec orchestration complète.
    Centralise toutes les opérations et fournit une interface unifiée.
    """    
    def __init__(self, database_url: str = None, **engine_kwargs):
        """        Initialise le moteur de gestion utilisateurs.
        
        Args:
            database_url: URL de connexion à la base de données
            **engine_kwargs: Arguments additionnels pour l'engine SQLAlchemy
        """        self.database_url = database_url or self._get_database_url()
        
        # Configuration optimisée pour production
        engine_config = {
            'poolclass': QueuePool,
            'pool_size': 20,
            'max_overflow': 30,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'echo': False,
            **engine_kwargs
        }
        
        self.engine = create_engine(self.database_url, **engine_config)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialisation des repositories
        self._init_repositories()
        
        # Configuration des événements SQLAlchemy
        self._setup_events()
        
        logger.info("UserManagementEngine initialisé avec succès")
    
    def _get_database_url(self) -> str:
        """Récupère l'URL de la base de données depuis l'environnement."""        default_url = "postgresql://user:password@localhost/ia_influencer_db"
        return os.getenv("DATABASE_URL", default_url)
    
    def _init_repositories(self):
        """Initialise tous les repositories avec une session partagée."""        self.user_repository = None
        self.creator_repository = None
        self.subscription_repository = None
        self.preferences_repository = None
        self.security_repository = None
        self.collaboration_repository = None
        self.platform_repository = None
        self.monetization_repository = None
    
    def _setup_events(self):
        """Configure les événements SQLAlchemy pour l'audit et la performance."""        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Configure les paramètres de performance pour SQLite (dev)."""            if 'sqlite' in self.database_url:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
        
        @event.listens_for(User, 'before_insert')
        def user_before_insert(mapper, connection, target):
            """Événement avant insertion d'un utilisateur."""            target.created_at = datetime.utcnow()
            target.updated_at = datetime.utcnow()
            logger.info(f"Nouvel utilisateur en cours de création: {target.email}")
        
        @event.listens_for(User, 'before_update')
        def user_before_update(mapper, connection, target):
            """Événement avant mise à jour d'un utilisateur."""            target.updated_at = datetime.utcnow()
    
    @contextmanager
    def get_session(self):
        """        Context manager pour obtenir une session de base de données.
        
        Yields:
            Session: Session SQLAlchemy configurée
        """        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur session base de données: {str(e)}")
            raise
        finally:
            session.close()
    
    def init_database(self, drop_existing: bool = False):
        """        Initialise la base de données avec tous les modèles.
        
        Args:
            drop_existing: Si True, supprime les tables existantes
        """        try:
            if drop_existing:
                logger.warning("Suppression des tables existantes...")
                Base.metadata.drop_all(bind=self.engine)
            
            logger.info("Création des tables de base de données...")
            Base.metadata.create_all(bind=self.engine)
            
            # Initialiser les données de base
            self._init_default_data()
            
            logger.info("Base de données initialisée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation base de données: {str(e)}")
            raise
    
    def _init_default_data(self):
        """Initialise les données par défaut nécessaires."""        with self.get_session() as session:
            try:
                # Créer les plans d'abonnement par défaut
                default_plans = [
                    {
                        "name": "Starter",
                        "tier": SubscriptionTier.BASIC,
                        "price_monthly": 9.99,
                        "price_yearly": 99.99,
                        "features": {
                            "max_uploads": 50,
                            "ai_recommendations": True,
                            "basic_analytics": True,
                            "collaboration_enabled": False,
                            "monetization_enabled": False
                        }
                    },
                    {
                        "name": "Professional",
                        "tier": SubscriptionTier.PROFESSIONAL,
                        "price_monthly": 29.99,
                        "price_yearly": 299.99,
                        "features": {
                            "max_uploads": 500,
                            "ai_recommendations": True,
                            "advanced_analytics": True,
                            "collaboration_enabled": True,
                            "monetization_enabled": True,
                            "content_protection": True
                        }
                    },
                    {
                        "name": "Enterprise",
                        "tier": SubscriptionTier.ENTERPRISE,
                        "price_monthly": 99.99,
                        "price_yearly": 999.99,
                        "features": {
                            "max_uploads": -1,  # Illimité
                            "ai_recommendations": True,
                            "premium_analytics": True,
                            "collaboration_enabled": True,
                            "monetization_enabled": True,
                            "content_protection": True,
                            "white_label": True,
                            "priority_support": True
                        }
                    }
                ]
                
                for plan_data in default_plans:
                    existing_plan = session.query(SubscriptionPlan).filter(
                        SubscriptionPlan.name == plan_data["name"]
                    ).first()
                    
                    if not existing_plan:
                        plan = SubscriptionPlan(**plan_data)
                        session.add(plan)
                
                session.commit()
                logger.info("Données par défaut initialisées")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Erreur initialisation données par défaut: {str(e)}")
                raise
    
    def get_repositories(self, session=None) -> Dict[str, Any]:
        """        Retourne tous les repositories initialisés avec une session.
        
        Args:
            session: Session SQLAlchemy (optionnel)
            
        Returns:
            Dict contenant tous les repositories
        """        if session is None:
            session = self.SessionLocal()
        
        return {
            'user': UserRepository(session),
            'creator': CreatorAccountRepository(session),
            'subscription': SubscriptionRepository(session),
            'preferences': UserPreferencesRepository(session),
            'security': SecurityRepository(session),
            'collaboration': CollaborationNetworkRepository(session),
            'platform': PlatformIntegrationRepository(session),
            'monetization': MonetizationRepository(session)
        }
    
    def create_user_complete(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """        Crée un utilisateur complet avec tous les profils associés.
        
        Args:
            user_data: Données de l'utilisateur
            
        Returns:
            Dict contenant l'utilisateur créé et ses profils
        """        with self.get_session() as session:
            try:
                repositories = self.get_repositories(session)
                
                # Créer l'utilisateur principal
                user = repositories['user'].create_user(user_data)
                
                # Créer les préférences par défaut
                default_preferences = {
                    "language": user_data.get("language_preference", "en"),
                    "timezone": user_data.get("timezone", "UTC"),
                    "notification_settings": {
                        "email_enabled": True,
                        "push_enabled": True,
                        "marketing_emails": False
                    },
                    "privacy_settings": {
                        "profile_visibility": "public",
                        "data_sharing": False,
                        "analytics_tracking": True
                    }
                }
                
                preferences = repositories['preferences'].create_user_preferences(
                    user.id, default_preferences
                )
                
                # Créer le profil de sécurité
                security_profile = repositories['security'].create_user_security(user.id, {
                    "two_factor_enabled": False,
                    "security_level": "standard"
                })
                
                # Si c'est un créateur, créer le compte créateur
                creator_account = None
                if user_data.get("user_type") == UserType.CREATOR or user_data.get("is_creator"):
                    creator_data = {
                        "creator_type": user_data.get("creator_type", "musician"),
                        "stage_name": user_data.get("stage_name", user.display_name),
                        "display_name": user.display_name,
                        "bio": user_data.get("bio", ""),
                        "content_formats": user_data.get("content_formats", ["audio"]),
                        "target_platforms": user_data.get("target_platforms", ["spotify"])
                    }
                    
                    creator_account = repositories['creator'].create_creator_account(
                        user.id, creator_data
                    )
                    
                    # Créer le réseau de collaboration
                    collaboration_network = repositories['collaboration'].create_network(
                        creator_account.id, {
                            "network_tier": NetworkTier.STARTER,
                            "max_collaborations": 5,
                            "preferred_collaboration_types": ["music_feature", "content_cross_promotion"]
                        }
                    )
                
                result = {
                    "user": user.to_dict(),
                    "preferences": preferences,
                    "security": security_profile,
                    "creator_account": creator_account.to_dict() if creator_account else None,
                    "success": True,
                    "message": "Utilisateur créé avec succès"
                }
                
                logger.info(f"Utilisateur complet créé: {user.email}")
                return result
                
            except Exception as e:
                logger.error(f"Erreur création utilisateur complet: {str(e)}")
                raise
    
    def get_user_complete_profile(self, user_id: str) -> Dict[str, Any]:
        """        Récupère le profil complet d'un utilisateur avec toutes ses données.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict contenant toutes les données de l'utilisateur
        """        with self.get_session() as session:
            try:
                repositories = self.get_repositories(session)
                
                # Récupérer l'utilisateur principal
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return {"error": "Utilisateur non trouvé"}
                
                # Récupérer toutes les données associées
                profile_data = {
                    "user": user.to_dict(),
                    "preferences": repositories['preferences'].get_user_preferences(user_id),
                    "security": repositories['security'].get_user_security(user_id),
                    "analytics": repositories['user'].get_user_analytics(user_id),
                    "creator_account": None,
                    "collaborations": [],
                    "platform_integrations": [],
                    "monetization": {}
                }
                
                # Si c'est un créateur, récupérer les données créateur
                creator_account = repositories['creator'].get_creator_by_user_id(user_id)
                if creator_account:
                    profile_data["creator_account"] = creator_account.to_dict()
                    profile_data["creator_analytics"] = repositories['creator'].get_creator_analytics(creator_account.id)
                    
                    # Récupérer les collaborations
                    profile_data["collaborations"] = repositories['collaboration'].get_creator_collaborations(creator_account.id)
                    
                    # Récupérer les intégrations de plateforme
                    profile_data["platform_integrations"] = repositories['platform'].get_active_integrations(creator_account.id)
                    
                    # Récupérer les données de monétisation
                    profile_data["monetization"] = repositories['monetization'].get_revenue_summary(creator_account.id)
                
                return profile_data
                
            except Exception as e:
                logger.error(f"Erreur récupération profil complet: {str(e)}")
                return {"error": str(e)}
    
    def get_system_health(self) -> Dict[str, Any]:
        """        Vérifie la santé du système de gestion utilisateurs.
        
        Returns:
            Dict contenant les métriques de santé
        """        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "database_connection": False,
            "total_users": 0,
            "active_creators": 0,
            "total_collaborations": 0,
            "total_revenue": 0,
            "system_version": "2.0.0",
            "modules_loaded": []
        }
        
        try:
            with self.get_session() as session:
                # Test de connexion base de données
                session.execute("SELECT 1")
                health_data["database_connection"] = True
                
                # Compter les utilisateurs
                health_data["total_users"] = session.query(User).count()
                
                # Compter les créateurs actifs
                health_data["active_creators"] = session.query(CreatorAccount).filter(
                    CreatorAccount.status == CreatorStatus.ACTIVE
                ).count()
                
                # Compter les collaborations
                health_data["total_collaborations"] = session.query(Collaboration).count()
                
                # Calculer le revenu total
                total_revenue = session.query(RevenueTransaction).with_entities(
                    func.sum(RevenueTransaction.net_amount)
                ).scalar()
                health_data["total_revenue"] = float(total_revenue or 0)
                
                # Modules chargés
                health_data["modules_loaded"] = [
                    "user_profiles", "creator_accounts", "subscription_management",
                    "user_preferences", "account_security", "collaboration_network",
                    "platform_integration", "monetization_tracking"
                ]
                
                health_data["status"] = "healthy"
                
        except Exception as e:
            health_data["status"] = "unhealthy"
            health_data["error"] = str(e)
            logger.error(f"Erreur vérification santé système: {str(e)}")
        
        return health_data
    
    def close(self):
        """Ferme les connexions et nettoie les ressources."""        if hasattr(self, 'engine'):
            self.engine.dispose()
        logger.info("UserManagementEngine fermé")


# Instance globale du moteur (singleton pattern)
_user_management_engine = None

def get_user_management_engine(database_url: str = None, **kwargs) -> UserManagementEngine:
    """    Retourne l'instance singleton du moteur de gestion utilisateurs.
    
    Args:
        database_url: URL de la base de données
        **kwargs: Arguments additionnels
        
    Returns:
        UserManagementEngine: Instance du moteur
    """    global _user_management_engine
    
    if _user_management_engine is None:
        _user_management_engine = UserManagementEngine(database_url, **kwargs)
    
    return _user_management_engine


def init_user_management_database(database_url: str = None, drop_existing: bool = False):
    """    Fonction utilitaire pour initialiser la base de données.
    
    Args:
        database_url: URL de la base de données
        drop_existing: Si True, supprime les tables existantes
    """    engine = get_user_management_engine(database_url)
    engine.init_database(drop_existing)


# Export des classes principales pour utilisation externe
__all__ = [
    # Moteur principal
    'UserManagementEngine',
    'get_user_management_engine',
    'init_user_management_database',
    
    # Modèles User Management
    'User', 'UserProfile', 'UserActivity', 'UserSession', 'UserSecurityLog', 'UserAIProfile',
    'UserRepository', 'UserType', 'UserStatus', 'OnboardingStep',
    
    # Modèles Creator
    'CreatorAccount', 'CreatorProfile', 'CreatorMetrics', 'CreatorAccountRepository',
    'CreatorType', 'CreatorStatus', 'VerificationLevel',
    
    # Modèles Subscription
    'SubscriptionPlan', 'UserSubscription', 'SubscriptionPayment', 'SubscriptionRepository',
    'SubscriptionTier', 'SubscriptionStatus', 'BillingCycle',
    
    # Modèles Preferences
    'UserPreferences', 'NotificationSettings', 'PrivacySettings', 'UserPreferencesRepository',
    
    # Modèles Security
    'UserSecurity', 'SecurityLog', 'TwoFactorAuth', 'SecurityRepository',
    
    # Modèles Collaboration
    'CollaborationNetwork', 'Collaboration', 'CollaborationInvitation', 'CollaborationNetworkRepository',
    'CollaborationType', 'CollaborationStatus', 'NetworkTier',
    
    # Modèles Platform Integration
    'PlatformIntegration', 'ContentDistribution', 'SynchronizationTask', 'PlatformIntegrationRepository',
    'PlatformType', 'IntegrationStatus', 'SyncFrequency',
    
    # Modèles Monetization
    'RevenueTransaction', 'RevenueProjection', 'RevenueAnalytics', 'PayoutRequest',
    'MonetizationRepository', 'RevenueSource', 'Currency',
    
    # Base commune
    'Base'
]


if __name__ == "__main__":
    # Test de base pour vérifier le bon fonctionnement
    logger.info("Test du module User Management...")
    
    try:
        engine = get_user_management_engine()
        health = engine.get_system_health()
        
        print("=== SANTÉ DU SYSTÈME USER MANAGEMENT ===")
        print(f"Statut: {health['status']}")
        print(f"Connexion DB: {health['database_connection']}")
        print(f"Modules chargés: {len(health['modules_loaded'])}")
        print(f"Version: {health['system_version']}")
        
        if health['status'] == 'healthy':
            print("✅ Module User Management opérationnel")
        else:
            print("❌ Problème détecté:", health.get('error', 'Inconnu'))
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        logger.error(f"Erreur test module: {str(e)}")
        
    print("\n=== FIN TEST USER MANAGEMENT ===") 
    AIPersonalizationProfile, UserPreferencesRepository,
    NotificationChannel, NotificationFrequency, PrivacyLevel, AIPersonality
)

from .account_security import (
    UserSecurity, UserSecurityLog, TrustedDevice, APIKey, APIUsageLog,
    SecurityRepository, SecurityEventType, ThreatLevel, DeviceType, SecurityStatus
)

# Configuration des relations inter-modules
def configure_relationships():
    """    Configure toutes les relations entre les modèles de différents modules.
    Cette fonction doit être appelée après l'import de tous les modèles.
    """    
    # Relations User avec autres modules
    User.creator_account = relationship("CreatorAccount", back_populates="user", uselist=False)
    User.subscriptions = relationship("UserSubscription", back_populates="user")
    User.preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    User.profile = relationship("UserProfile", back_populates="user", uselist=False)
    User.activities = relationship("UserActivity", back_populates="user")
    User.sessions = relationship("UserSession", back_populates="user")
    User.security = relationship("UserSecurity", back_populates="user", uselist=False)
    User.security_logs = relationship("UserSecurityLog", back_populates="user")
    User.ai_profile = relationship("AIPersonalizationProfile", back_populates="user", uselist=False)
    
    # Relations CreatorAccount
    CreatorAccount.user = relationship("User", back_populates="creator_account")
    CreatorAccount.profile = relationship("CreatorProfile", back_populates="creator_account", uselist=False)
    CreatorAccount.metrics = relationship("CreatorMetrics", back_populates="creator_account")
    
    # Relations UserSubscription
    UserSubscription.user = relationship("User", back_populates="subscriptions")
    UserSubscription.plan = relationship("SubscriptionPlan", back_populates="subscriptions", foreign_keys=[UserSubscription.plan_id])
    UserSubscription.next_plan = relationship("SubscriptionPlan", foreign_keys=[UserSubscription.next_plan_id])
    UserSubscription.payments = relationship("SubscriptionPayment", back_populates="subscription")
    UserSubscription.usage_logs = relationship("SubscriptionUsage", back_populates="subscription")
    
    # Relations SubscriptionPlan
    SubscriptionPlan.subscriptions = relationship("UserSubscription", back_populates="plan", foreign_keys=[UserSubscription.plan_id])
    
    # Relations SubscriptionPayment
    SubscriptionPayment.subscription = relationship("UserSubscription", back_populates="payments")
    
    # Relations SubscriptionUsage
    SubscriptionUsage.subscription = relationship("UserSubscription", back_populates="usage_logs")
    
    # Relations UserPreferences
    UserPreferences.user = relationship("User", back_populates="preferences")
    UserPreferences.notification_settings = relationship("NotificationSettings", back_populates="preferences", uselist=False)
    UserPreferences.privacy_settings = relationship("PrivacySettings", back_populates="preferences", uselist=False)
    
    # Relations NotificationSettings
    NotificationSettings.preferences = relationship("UserPreferences", back_populates="notification_settings")
    
    # Relations PrivacySettings
    PrivacySettings.preferences = relationship("UserPreferences", back_populates="privacy_settings")
    
    # Relations AIPersonalizationProfile
    AIPersonalizationProfile.user = relationship("User", back_populates="ai_profile")
    
    # Relations UserProfile
    UserProfile.user = relationship("User", back_populates="profile")
    
    # Relations UserActivity
    UserActivity.user = relationship("User", back_populates="activities")
    
    # Relations UserSession
    UserSession.user = relationship("User", back_populates="sessions")
    
    # Relations CreatorProfile
    CreatorProfile.creator_account = relationship("CreatorAccount", back_populates="profile")
    
    # Relations CreatorMetrics
    CreatorMetrics.creator_account = relationship("CreatorAccount", back_populates="metrics")
    
    # Relations UserSecurity
    UserSecurity.user = relationship("User", back_populates="security")
    UserSecurity.security_logs = relationship("UserSecurityLog", back_populates="user_security")
    UserSecurity.trusted_devices = relationship("TrustedDevice", back_populates="user_security")
    UserSecurity.api_keys = relationship("APIKey", back_populates="user_security")
    
    # Relations UserSecurityLog
    UserSecurityLog.user_security = relationship("UserSecurity", back_populates="security_logs")
    UserSecurityLog.user = relationship("User", back_populates="security_logs")
    
    # Relations TrustedDevice
    TrustedDevice.user_security = relationship("UserSecurity", back_populates="trusted_devices")
    
    # Relations APIKey
    APIKey.user_security = relationship("UserSecurity", back_populates="api_keys")
    APIKey.usage_logs = relationship("APIUsageLog", back_populates="api_key")
    
    # Relations APIUsageLog
    APIUsageLog.api_key = relationship("APIKey", back_populates="usage_logs")
    
    logger.info("Relations entre modèles configurées avec succès")


class UserManagementDatabase:
    """    Classe principale pour la gestion de la base de données utilisateur.
    Fournit une interface unifiée pour tous les repositories.
    """    
    def __init__(self, database_url: str, echo: bool = False):
        """        Initialise la base de données de gestion utilisateur.
        
        Args:
            database_url: URL de connexion à la base de données
            echo: Activer les logs SQL
        """        self.engine = create_engine(database_url, echo=echo)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.metadata = MetaData()
        
        # Configuration des relations
        configure_relationships()
        
        # Initialisation des repositories
        self._repositories = {}
        
        logger.info("Base de données User Management initialisée")
    
    def create_all_tables(self):
        """Crée toutes les tables de la base de données."""        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Toutes les tables User Management créées avec succès")
        except Exception as e:
            logger.error(f"Erreur création tables: {str(e)}")
            raise
    
    def get_session(self):
        """Retourne une nouvelle session de base de données."""        return self.SessionLocal()
    
    def get_user_repository(self) -> UserRepository:
        """Retourne le repository des utilisateurs."""        session = self.get_session()
        return UserRepository(session)
    
    def get_creator_repository(self) -> CreatorAccountRepository:
        """Retourne le repository des créateurs."""        session = self.get_session()
        return CreatorAccountRepository(session)
    
    def get_subscription_repository(self) -> SubscriptionRepository:
        """Retourne le repository des abonnements."""        session = self.get_session()
        return SubscriptionRepository(session)
    
    def get_preferences_repository(self) -> UserPreferencesRepository:
        """Retourne le repository des préférences."""        session = self.get_session()
        return UserPreferencesRepository(session)
    
    def get_security_repository(self, encryption_key: str = None) -> SecurityRepository:
        """Retourne le repository de sécurité."""        session = self.get_session()
        return SecurityRepository(session, encryption_key)
    
    def initialize_default_data(self):
        """        Initialise les données par défaut (plans d'abonnement, etc.).
        """        try:
            session = self.get_session()
            
            # Vérifier si les plans existent déjà
            existing_plans = session.query(SubscriptionPlan).count()
            if existing_plans > 0:
                logger.info("Plans d'abonnement déjà initialisés")
                session.close()
                return
            
            # Création des plans par défaut
            plans = [
                SubscriptionPlan(
                    name="Free",
                    tier=SubscriptionTier.FREE,
                    description="Plan gratuit avec fonctionnalités de base",
                    price_monthly=0.00,
                    max_uploads_per_month=10,
                    max_storage_gb=1,
                    max_ai_requests_per_month=100,
                    max_collaborations=1,
                    max_platforms=2,
                    features=["basic_upload", "basic_analytics", "community_support"],
                    ai_features_enabled=True,
                    protection_features_enabled=False,
                    analytics_level="basic",
                    trial_days=0
                ),
                SubscriptionPlan(
                    name="Creator Pro",
                    tier=SubscriptionTier.CREATOR_PRO,
                    description="Plan professionnel pour créateurs sérieux",
                    price_monthly=29.99,
                    price_yearly=299.99,
                    max_uploads_per_month=500,
                    max_storage_gb=50,
                    max_ai_requests_per_month=5000,
                    max_collaborations=10,
                    max_platforms=10,
                    features=[
                        "unlimited_upload", "advanced_analytics", "ai_recommendations",
                        "content_protection", "collaboration_tools", "priority_support"
                    ],
                    ai_features_enabled=True,
                    protection_features_enabled=True,
                    analytics_level="advanced",
                    priority_support=True,
                    trial_days=14
                ),
                SubscriptionPlan(
                    name="Enterprise",
                    tier=SubscriptionTier.ENTERPRISE,
                    description="Solution enterprise avec support dédié",
                    price_monthly=199.99,
                    price_yearly=1999.99,
                    max_uploads_per_month=-1,  # Illimité
                    max_storage_gb=-1,  # Illimité
                    max_ai_requests_per_month=-1,  # Illimité
                    max_collaborations=-1,  # Illimité
                    max_platforms=-1,  # Illimité
                    features=[
                        "everything", "white_label", "api_access", "custom_integration",
                        "dedicated_support", "sla_guarantee", "advanced_security"
                    ],
                    ai_features_enabled=True,
                    protection_features_enabled=True,
                    analytics_level="enterprise",
                    priority_support=True,
                    trial_days=30
                )
            ]
            
            for plan in plans:
                session.add(plan)
            
            session.commit()
            session.close()
            
            logger.info("Données par défaut initialisées avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation données par défaut: {str(e)}")
            if session:
                session.rollback()
                session.close()
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """        Retourne les statistiques de la base de données utilisateur.
        
        Returns:
            Dict[str, Any]: Statistiques globales
        """        try:
            session = self.get_session()
            
            stats = {
                'users': {
                    'total': session.query(User).count(),
                    'active': session.query(User).filter(User.status == UserStatus.ACTIVE).count(),
                    'creators': session.query(User).join(CreatorAccount).count()
                },
                'subscriptions': {
                    'total': session.query(UserSubscription).count(),
                    'active': session.query(UserSubscription).filter(
                        UserSubscription.status == SubscriptionStatus.ACTIVE
                    ).count(),
                    'trial': session.query(UserSubscription).filter(
                        UserSubscription.status == SubscriptionStatus.TRIAL
                    ).count()
                },
                'security': {
                    'two_factor_enabled': session.query(UserSecurity).filter(
                        UserSecurity.two_factor_enabled == True
                    ).count(),
                    'locked_accounts': session.query(UserSecurity).filter(
                        UserSecurity.account_locked == True
                    ).count()
                },
                'activity': {
                    'total_sessions': session.query(UserSession).count(),
                    'active_sessions': session.query(UserSession).filter(
                        UserSession.is_active == True
                    ).count()
                }
            }
            
            session.close()
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques: {str(e)}")
            if session:
                session.close()
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """        Effectue un contrôle de santé de la base de données.
        
        Returns:
            Dict[str, Any]: Résultats du contrôle de santé
        """        try:
            session = self.get_session()
            
            # Test de connexion
            session.execute("SELECT 1")
            
            # Vérification des tables principales
            tables_status = {}
            for table_name in ['users', 'creator_accounts', 'user_subscriptions', 'user_security']:
                try:
                    count = session.execute(f"SELECT COUNT(*) FROM {table_name}").scalar()
                    tables_status[table_name] = {'status': 'ok', 'count': count}
                except Exception as e:
                    tables_status[table_name] = {'status': 'error', 'error': str(e)}
            
            session.close()
            
            return {
                'status': 'healthy',
                'database_connection': 'ok',
                'tables': tables_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur contrôle de santé: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Instance globale (singleton)
_db_instance = None

def get_user_management_db(database_url: str = None, echo: bool = False) -> UserManagementDatabase:
    """    Retourne l'instance singleton de la base de données.
    
    Args:
        database_url: URL de la base de données (requis pour la première initialisation)
        echo: Activer les logs SQL
        
    Returns:
        UserManagementDatabase: Instance de la base de données
    """    global _db_instance
    
    if _db_instance is None:
        if database_url is None:
            raise ValueError("database_url requis pour la première initialisation")
        _db_instance = UserManagementDatabase(database_url, echo)
    
    return _db_instance


# Export des classes et enums principaux
__all__ = [
    # Classes principales
    'UserManagementDatabase',
    'get_user_management_db',
    
    # Modèles
    'User', 'UserProfile', 'UserActivity', 'UserSession',
    'CreatorAccount', 'CreatorProfile', 'CreatorMetrics',
    'SubscriptionPlan', 'UserSubscription', 'SubscriptionPayment', 'SubscriptionUsage',
    'UserPreferences', 'NotificationSettings', 'PrivacySettings', 'AIPersonalizationProfile',
    'UserSecurity', 'UserSecurityLog', 'TrustedDevice', 'APIKey', 'APIUsageLog',
    
    # Repositories
    'UserRepository', 'CreatorAccountRepository', 'SubscriptionRepository',
    'UserPreferencesRepository', 'SecurityRepository',
    
    # Enums
    'UserType', 'UserStatus', 'OnboardingStep',
    'CreatorType', 'CreatorStatus', 'VerificationLevel',
    'SubscriptionTier', 'SubscriptionStatus', 'BillingCycle', 'PaymentStatus',
    'NotificationChannel', 'NotificationFrequency', 'PrivacyLevel', 'AIPersonality',
    'SecurityEventType', 'ThreatLevel', 'DeviceType', 'SecurityStatus'
]
