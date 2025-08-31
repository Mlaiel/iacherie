"""Platform Integration Database Models and Operations

Gestion complète des intégrations multi-plateformes pour distribution
automatisée et synchronisation des comptes créateurs.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & Platform Integration Specialist

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle de Fahed Mlaiel.
Toute utilisation, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de 
poursuites judiciaires selon la loi allemande.
Email: mlaiel@live.de pour autorisation d'utilisation.
"""from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey, Decimal
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum as PyEnum
import logging
import uuid
import json
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

Base = declarative_base()


class PlatformType(PyEnum):
    """Types de plateformes supportées."""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    SOUNDCLOUD = "soundcloud"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    DEEZER = "deezer"
    PODCAST_PLATFORMS = "podcast_platforms"


class IntegrationStatus(PyEnum):
    """Statuts d'intégration des plateformes."""    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    EXPIRED = "expired"
    ERROR = "error"
    SUSPENDED = "suspended"
    RATE_LIMITED = "rate_limited"


class SyncFrequency(PyEnum):
    """Fréquences de synchronisation."""    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"


class DistributionChannel(PyEnum):
    """Canaux de distribution."""    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORMS = "video_platforms"
    SOCIAL_MEDIA = "social_media"
    PODCAST_NETWORKS = "podcast_networks"
    BLOG_PLATFORMS = "blog_platforms"
    PHOTO_GALLERIES = "photo_galleries"


class PlatformIntegration(Base):
    """    Intégration principale avec les plateformes externes.
    Gère l'authentification, la synchronisation et la distribution.
    """    __tablename__ = "platform_integrations"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    integration_uuid = Column(String, unique=True, nullable=False)
    creator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    
    # Configuration plateforme
    platform_type = Column(Enum(PlatformType), nullable=False)
    platform_user_id = Column(String, nullable=False)
    platform_username = Column(String(200))
    platform_display_name = Column(String(300))
    
    # Statut et santé
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.DISCONNECTED)
    last_sync_at = Column(DateTime)
    next_sync_at = Column(DateTime)
    sync_frequency = Column(Enum(SyncFrequency), default=SyncFrequency.DAILY)
    
    # Authentification (chiffrée)
    access_token_encrypted = Column(Text)
    refresh_token_encrypted = Column(Text)
    token_expires_at = Column(DateTime)
    scopes_granted = Column(JSON)  # ["read", "write", "manage"]
    
    # Configuration de distribution
    auto_distribution = Column(Boolean, default=False)
    distribution_channels = Column(JSON)  # Canaux activés
    content_filters = Column(JSON)  # Filtres de contenu
    scheduling_preferences = Column(JSON)  # Préférences de planification
    
    # Métriques et performance
    total_uploads = Column(Integer, default=0)
    successful_uploads = Column(Integer, default=0)
    failed_uploads = Column(Integer, default=0)
    total_reach = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    
    # Limites et quotas
    rate_limit_remaining = Column(Integer)
    rate_limit_reset_at = Column(DateTime)
    daily_upload_limit = Column(Integer)
    daily_uploads_used = Column(Integer, default=0)
    
    # Configuration avancée
    webhook_url = Column(String(500))
    api_version = Column(String(20))
    custom_settings = Column(JSON)  # Paramètres spécifiques à la plateforme
    
    # Métadonnées
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__()
        self.integration_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class ContentDistribution(Base):
    """    Distribution de contenu vers les plateformes intégrées.
    """    __tablename__ = "content_distributions"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    distribution_uuid = Column(String, unique=True, nullable=False)
    creator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    integration_id = Column(String, ForeignKey("platform_integrations.id"), nullable=False)
    
    # Contenu source
    content_id = Column(String, nullable=False)  # ID du contenu à distribuer
    content_type = Column(String(50), nullable=False)  # "audio", "video", "image", "text"
    content_title = Column(String(500))
    content_description = Column(Text)
    
    # Configuration distribution
    platform_type = Column(Enum(PlatformType), nullable=False)
    distribution_channel = Column(Enum(DistributionChannel), nullable=False)
    scheduled_at = Column(DateTime)
    published_at = Column(DateTime)
    
    # Métadonnées spécifiques plateforme
    platform_content_id = Column(String(200))  # ID assigné par la plateforme
    platform_url = Column(String(1000))  # URL publique du contenu
    platform_metadata = Column(JSON)  # Métadonnées spécifiques
    
    # Statut et résultats
    status = Column(String(50), default="pending")  # "pending", "processing", "published", "failed"
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Métriques de performance
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    engagement_rate = Column(Decimal(5, 2), default=0.00)
    
    # Configuration SEO
    tags = Column(JSON)  # Tags pour optimisation
    hashtags = Column(JSON)  # Hashtags générés par IA
    seo_optimization = Column(JSON)  # Optimisations SEO
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_metrics_update = Column(DateTime)

    # Relations
    integration = relationship("PlatformIntegration", backref="distributions")

    def __init__(self, **kwargs):
        super().__init__()
        self.distribution_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class SynchronizationTask(Base):
    """    Tâches de synchronisation entre plateformes.
    """    __tablename__ = "synchronization_tasks"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_uuid = Column(String, unique=True, nullable=False)
    integration_id = Column(String, ForeignKey("platform_integrations.id"), nullable=False)
    
    # Configuration tâche
    task_type = Column(String(100), nullable=False)  # "content_sync", "metrics_sync", "profile_sync"
    sync_direction = Column(String(50))  # "import", "export", "bidirectional"
    priority = Column(Integer, default=5)  # 1-10, 10 = haute priorité
    
    # Planification
    scheduled_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    next_run_at = Column(DateTime)
    
    # Paramètres de synchronisation
    sync_parameters = Column(JSON)  # Paramètres spécifiques
    data_filters = Column(JSON)  # Filtres de données
    batch_size = Column(Integer, default=100)
    
    # Statut et résultats
    status = Column(String(50), default="pending")  # "pending", "running", "completed", "failed", "cancelled"
    progress_percentage = Column(Integer, default=0)
    items_processed = Column(Integer, default=0)
    items_total = Column(Integer, default=0)
    
    # Résultats détaillés
    results_summary = Column(JSON)  # Résumé des résultats
    error_details = Column(JSON)  # Détails des erreurs
    performance_metrics = Column(JSON)  # Métriques de performance
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    integration = relationship("PlatformIntegration", backref="sync_tasks")

    def __init__(self, **kwargs):
        super().__init__()
        self.task_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class PlatformAnalytics(Base):
    """    Analytics consolidées des performances cross-platform.
    """    __tablename__ = "platform_analytics"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analytics_uuid = Column(String, unique=True, nullable=False)
    creator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    integration_id = Column(String, ForeignKey("platform_integrations.id"), nullable=False)
    
    # Période d'analyse
    date = Column(DateTime, nullable=False)
    period_type = Column(String(20), default="daily")  # "daily", "weekly", "monthly"
    
    # Métriques d'audience
    followers_count = Column(Integer, default=0)
    followers_growth = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    
    # Métriques d'engagement
    likes_total = Column(Integer, default=0)
    comments_total = Column(Integer, default=0)
    shares_total = Column(Integer, default=0)
    saves_total = Column(Integer, default=0)
    engagement_rate = Column(Decimal(5, 2), default=0.00)
    
    # Métriques de contenu
    new_uploads = Column(Integer, default=0)
    total_content_count = Column(Integer, default=0)
    content_views = Column(Integer, default=0)
    content_reach = Column(Integer, default=0)
    
    # Métriques financières
    revenue_generated = Column(Decimal(10, 2), default=0.00)
    stream_royalties = Column(Decimal(10, 2), default=0.00)
    ad_revenue = Column(Decimal(10, 2), default=0.00)
    
    # Données démographiques
    audience_demographics = Column(JSON)  # Répartition audience
    geographic_distribution = Column(JSON)  # Distribution géographique
    device_usage = Column(JSON)  # Utilisation par device
    
    # Données comportementales
    listening_patterns = Column(JSON)  # Patterns d'écoute
    peak_hours = Column(JSON)  # Heures de pointe
    user_journey = Column(JSON)  # Parcours utilisateur
    
    # Comparaisons et tendances
    previous_period_comparison = Column(JSON)  # Comparaison période précédente
    trend_indicators = Column(JSON)  # Indicateurs de tendance
    performance_score = Column(Decimal(5, 2), default=0.00)
    
    # Métadonnées
    data_freshness = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    integration = relationship("PlatformIntegration", backref="analytics")

    def __init__(self, **kwargs):
        super().__init__()
        self.analytics_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class PlatformIntegrationRepository:
    """    Repository pour la gestion des intégrations de plateformes.
    """    def __init__(self, db_session: Session, encryption_key: bytes = None):
        self.db = db_session
        self.cipher = Fernet(encryption_key) if encryption_key else None

    def create_integration(self, integration_data: Dict[str, Any]) -> PlatformIntegration:
        """Créer une nouvelle intégration de plateforme."""        try:
            # Chiffrer les tokens si disponible
            if self.cipher and 'access_token' in integration_data:
                integration_data['access_token_encrypted'] = self.cipher.encrypt(
                    integration_data.pop('access_token').encode()
                ).decode()
            
            if self.cipher and 'refresh_token' in integration_data:
                integration_data['refresh_token_encrypted'] = self.cipher.encrypt(
                    integration_data.pop('refresh_token').encode()
                ).decode()
            
            integration = PlatformIntegration(**integration_data)
            self.db.add(integration)
            self.db.commit()
            self.db.refresh(integration)
            
            logger.info(f"Intégration créée: {integration.platform_type.value} pour {integration.creator_id}")
            return integration
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création intégration: {str(e)}")
            raise

    def update_integration_status(self, integration_id: str, status: IntegrationStatus, 
                                error_message: str = None) -> bool:
        """Mettre à jour le statut d'une intégration."""        try:
            integration = self.db.query(PlatformIntegration).filter(
                PlatformIntegration.id == integration_id
            ).first()
            
            if not integration:
                return False
            
            integration.status = status
            integration.updated_at = datetime.utcnow()
            
            if error_message:
                integration.last_error = error_message
                integration.error_count += 1
            else:
                integration.error_count = 0
                integration.last_error = None
            
            if status == IntegrationStatus.CONNECTED:
                integration.last_sync_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Statut intégration mis à jour: {integration_id} -> {status.value}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur mise à jour statut: {str(e)}")
            return False

    def schedule_content_distribution(self, distribution_data: Dict[str, Any]) -> ContentDistribution:
        """Planifier une distribution de contenu."""        try:
            distribution = ContentDistribution(**distribution_data)
            self.db.add(distribution)
            self.db.commit()
            self.db.refresh(distribution)
            
            logger.info(f"Distribution planifiée: {distribution.distribution_uuid}")
            return distribution
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur planification distribution: {str(e)}")
            raise

    def create_sync_task(self, task_data: Dict[str, Any]) -> SynchronizationTask:
        """Créer une tâche de synchronisation."""        try:
            task = SynchronizationTask(**task_data)
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Tâche de sync créée: {task.task_uuid}")
            return task
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création tâche sync: {str(e)}")
            raise

    def get_active_integrations(self, creator_id: str) -> List[PlatformIntegration]:
        """Obtenir les intégrations actives d'un créateur."""        try:
            integrations = self.db.query(PlatformIntegration).filter(
                PlatformIntegration.creator_id == creator_id,
                PlatformIntegration.status == IntegrationStatus.CONNECTED
            ).all()
            
            return integrations
            
        except Exception as e:
            logger.error(f"Erreur récupération intégrations: {str(e)}")
            return []

    def get_platform_analytics(self, creator_id: str, platform_type: PlatformType = None, 
                             days: int = 30) -> List[PlatformAnalytics]:
        """Obtenir les analytics de plateforme."""        try:
            query = self.db.query(PlatformAnalytics).filter(
                PlatformAnalytics.creator_id == creator_id,
                PlatformAnalytics.date >= datetime.utcnow() - timedelta(days=days)
            )
            
            if platform_type:
                query = query.join(PlatformIntegration).filter(
                    PlatformIntegration.platform_type == platform_type
                )
            
            analytics = query.order_by(PlatformAnalytics.date.desc()).all()
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erreur récupération analytics: {str(e)}")
            return []

    def update_content_metrics(self, distribution_id: str, metrics: Dict[str, Any]) -> bool:
        """Mettre à jour les métriques d'un contenu distribué."""        try:
            distribution = self.db.query(ContentDistribution).filter(
                ContentDistribution.id == distribution_id
            ).first()
            
            if not distribution:
                return False
            
            distribution.views_count = metrics.get('views_count', distribution.views_count)
            distribution.likes_count = metrics.get('likes_count', distribution.likes_count)
            distribution.shares_count = metrics.get('shares_count', distribution.shares_count)
            distribution.comments_count = metrics.get('comments_count', distribution.comments_count)
            distribution.engagement_rate = metrics.get('engagement_rate', distribution.engagement_rate)
            distribution.last_metrics_update = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Métriques mises à jour: {distribution_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur mise à jour métriques: {str(e)}")
            return False

    def get_cross_platform_performance(self, creator_id: str) -> Dict[str, Any]:
        """Obtenir la performance cross-platform d'un créateur."""        try:
            # Récupérer toutes les intégrations actives
            integrations = self.get_active_integrations(creator_id)
            
            # Récupérer les analytics récentes pour chaque plateforme
            performance_data = {}
            total_metrics = {
                'total_followers': 0,
                'total_engagement': 0,
                'total_content': 0,
                'total_revenue': 0
            }
            
            for integration in integrations:
                platform_analytics = self.db.query(PlatformAnalytics).filter(
                    PlatformAnalytics.integration_id == integration.id,
                    PlatformAnalytics.date >= datetime.utcnow() - timedelta(days=7)
                ).order_by(PlatformAnalytics.date.desc()).first()
                
                if platform_analytics:
                    platform_data = {
                        'platform': integration.platform_type.value,
                        'followers': platform_analytics.followers_count,
                        'engagement_rate': float(platform_analytics.engagement_rate),
                        'content_count': platform_analytics.total_content_count,
                        'revenue': float(platform_analytics.revenue_generated)
                    }
                    
                    performance_data[integration.platform_type.value] = platform_data
                    
                    # Ajouter aux totaux
                    total_metrics['total_followers'] += platform_analytics.followers_count
                    total_metrics['total_engagement'] += platform_analytics.likes_total + platform_analytics.comments_total
                    total_metrics['total_content'] += platform_analytics.total_content_count
                    total_metrics['total_revenue'] += float(platform_analytics.revenue_generated)
            
            return {
                'platforms': performance_data,
                'totals': total_metrics,
                'platform_count': len(integrations)
            }
            
        except Exception as e:
            logger.error(f"Erreur performance cross-platform: {str(e)}")
            return {}

    def get_access_token(self, integration_id: str) -> Optional[str]:
        """Récupérer le token d'accès déchiffré."""        try:
            if not self.cipher:
                logger.warning("Cipher non configuré pour déchiffrer les tokens")
                return None
            
            integration = self.db.query(PlatformIntegration).filter(
                PlatformIntegration.id == integration_id
            ).first()
            
            if not integration or not integration.access_token_encrypted:
                return None
            
            decrypted_token = self.cipher.decrypt(
                integration.access_token_encrypted.encode()
            ).decode()
            
            return decrypted_token
            
        except Exception as e:
            logger.error(f"Erreur déchiffrement token: {str(e)}")
            return None
