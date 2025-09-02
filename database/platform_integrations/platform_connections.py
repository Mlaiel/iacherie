"""Platform Connections Database Module

Gestion des connexions aux plateformes externes (Spotify, YouTube, Instagram, TikTok, etc.)
pour la plateforme IA Influencer Agent.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer, Backend Senior, DevOps Engineer, Database Architect
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Dict, List, Any, Optional
import uuid
import logging
from datetime import datetime

from backend.database.models.base import BaseModel

logger = logging.getLogger(__name__)


class PlatformConnection(BaseModel):
    """
    Modèle pour les connexions aux plateformes externes.
    
    Stocke les informations de connexion, tokens d'accès et statut
    pour chaque plateforme intégrée.
    """
    
    __tablename__ = "platform_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    platform_type = Column(String(30), nullable=False)  # social, music, video, blog
    
    # Identifiants de connexion
    external_user_id = Column(String(255), nullable=False)
    username = Column(String(100))
    display_name = Column(String(255))
    profile_url = Column(Text)
    avatar_url = Column(Text)
    
    # Tokens d'authentification
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime(timezone=True))
    
    # Scopes et permissions
    granted_scopes = Column(JSONB, default=list)
    required_scopes = Column(JSONB, default=list)
    permissions_level = Column(String(20), default="read")  # read, write, admin
    
    # Statut de la connexion
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    last_sync = Column(DateTime(timezone=True))
    sync_frequency = Column(String(20), default="daily")  # realtime, hourly, daily, weekly
    
    # Métadonnées et configuration
    connection_metadata = Column(JSONB, default=dict)
    api_quota_remaining = Column(Integer, default=0)
    api_quota_reset_at = Column(DateTime(timezone=True))
    
    # Métriques de performance
    total_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    last_success = Column(DateTime(timezone=True))
    last_error = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        try:
            logger.info(f"Executing __repr__")
            
            # Implementation for __repr__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__repr__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__repr__ failed: {e}")
            raise
    @property
    def is_token_expired(self) -> bool:
        """Vérifie si le token d'accès est expiré."""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() > self.token_expires_at
    
    @property
    def connection_health_score(self) -> float:
        """
Calcule un score de santé de la connexion (0-100)."""
        if self.total_requests == 0:
            return 100.0
        
        success_rate = (self.total_requests - self.failed_requests) / self.total_requests
        health_score = success_rate * 100
        
        # Pénalité si token expiré
        if self.is_token_expired:
            health_score *= 0.5
            
        # Pénalité si pas vérifié
        if not self.is_verified:
            health_score *= 0.8
            
        return max(0.0, min(100.0, health_score))
    
    def update_sync_status(self, success: bool, error_message: str = None):
        """
Met à jour le statut de synchronisation."""
        self.total_requests += 1
        if success:
            self.last_success = datetime.utcnow()
            self.last_sync = datetime.utcnow()
        else:
            self.failed_requests += 1
            if error_message:
                self.last_error = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convertit la connexion en dictionnaire."""
        return {
            "id": str(self.id),
            "platform_name": self.platform_name,
            "platform_type": self.platform_type,
            "username": self.username,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "permissions_level": self.permissions_level,
            "sync_frequency": self.sync_frequency,
            "health_score": self.connection_health_score,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class PlatformEndpoint(BaseModel):
    """
    Modèle pour les endpoints d'API des plateformes.
    
    Stocke les informations sur les endpoints disponibles,
    leurs limitations et performances.
    """
    
    __tablename__ = "platform_endpoints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    endpoint_name = Column(String(100), nullable=False)
    endpoint_url = Column(Text, nullable=False)
    http_method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    
    # Configuration de l'endpoint
    required_scopes = Column(JSONB, default=list)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    timeout_seconds = Column(Integer, default=30)
    
    # Documentation et métadonnées
    description = Column(Text)
    parameters_schema = Column(JSONB, default=dict)
    response_schema = Column(JSONB, default=dict)
    example_request = Column(JSONB, default=dict)
    example_response = Column(JSONB, default=dict)
    
    # Métriques de performance
    average_response_time = Column(Integer, default=0)  # en millisecondes
    success_rate = Column(Integer, default=100)  # pourcentage
    last_availability_check = Column(DateTime(timezone=True))
    is_available = Column(Boolean, default=True)
    
    # Versioning
    api_version = Column(String(20), default="v1")
    deprecated = Column(Boolean, default=False)
    deprecation_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        try:
            logger.info(f"Executing __repr__")
            
            # Implementation for __repr__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__repr__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__repr__ failed: {e}")
            raise
    is_available = Column(Boolean, default=True)
    
    # Versioning
    api_version = Column(String(20), default="v1")
    deprecated = Column(Boolean, default=False)
    deprecation_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformEndpoint(platform={self.platform_name}, endpoint={self.endpoint_name})>"


class PlatformWebhook(BaseModel):
    """
    Modèle pour les webhooks des plateformes.
    
    Gère les notifications en temps réel des plateformes
    externes (nouvelles publications, interactions, etc.).
    """
    
    __tablename__ = "platform_webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Configuration du webhook
    webhook_url = Column(Text, nullable=False)
    webhook_secret = Column(String(255))
    event_types = Column(JSONB, default=list)  # ['post_created', 'like_received', etc.]
    
    # Statut et validation
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    verification_challenge = Column(String(255))
    
    # Métriques de réception
    total_events_received = Column(Integer, default=0)
    last_event_received = Column(DateTime(timezone=True))
    failed_deliveries = Column(Integer, default=0)
    
    # Configuration avancée
    retry_policy = Column(JSONB, default={"max_retries": 3, "backoff_factor": 2})
        try:
            logger.info(f"Executing __repr__")
            
            # Implementation for __repr__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__repr__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__repr__ failed: {e}")
            raise
    Gère les notifications en temps réel des plateformes
    externes (nouvelles publications, interactions, etc.).
    """
    
    __tablename__ = "platform_webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Configuration du webhook
    webhook_url = Column(Text, nullable=False)
    webhook_secret = Column(String(255))
    event_types = Column(JSONB, default=list)  # ['post_created', 'like_received', etc.]
    
    # Statut et validation
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    verification_challenge = Column(String(255))
    
    # Métriques de réception
    total_events_received = Column(Integer, default=0)
    last_event_received = Column(DateTime(timezone=True))
    failed_deliveries = Column(Integer, default=0)
    
    # Configuration avancée
    retry_policy = Column(JSONB, default={"max_retries": 3, "backoff_factor": 2})
        try:
            logger.info(f"Executing __repr__")
            
            # Implementation for __repr__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__repr__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__repr__ failed: {e}")
            raise
    """
    
    __tablename__ = "platform_webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Configuration du webhook
    webhook_url = Column(Text, nullable=False)
    webhook_secret = Column(String(255))
    event_types = Column(JSONB, default=list)  # ['post_created', 'like_received', etc.]
    
    # Statut et validation
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    verification_challenge = Column(String(255))
    
    # Métriques de réception
    total_events_received = Column(Integer, default=0)
    last_event_received = Column(DateTime(timezone=True))
    failed_deliveries = Column(Integer, default=0)
    
    # Configuration avancée
    retry_policy = Column(JSONB, default={"max_retries": 3, "backoff_factor": 2})
        try:
            logger.info(f"Executing __repr__")
            
            # Implementation for __repr__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__repr__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__repr__ failed: {e}")
            raise
    retry_policy = Column(JSONB, default={"max_retries": 3, "backoff_factor": 2})
    filter_conditions = Column(JSONB, default=dict)
    transformation_rules = Column(JSONB, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformWebhook(platform={self.platform_name}, active={self.is_active})>"


class PlatformSyncLog(BaseModel):
    """
    Modèle pour les logs de synchronisation avec les plateformes.
    
    Enregistre l'historique des synchronisations pour audit,
    monitoring et debugging.
    """
    
    __tablename__ = "platform_sync_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Informations de synchronisation
    sync_type = Column(String(50), nullable=False)  # full, incremental, webhook
    sync_direction = Column(String(20), nullable=False)  # inbound, outbound, bidirectional
    
    # Résultats de la synchronisation
    sync_status = Column(String(20), nullable=False, index=True)  # success, failure, partial
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Timing et performance
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer, default=0)
    
    # Détails et erreurs
    sync_details = Column(JSONB, default=dict)
    error_details = Column(JSONB, default=dict)
    warning_messages = Column(JSONB, default=list)
    
    # Métadonnées
    triggered_by = Column(String(50))  # system, user, webhook, schedule
    execution_context = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        try:
            logger.info(f"Executing __repr__")
            
            # Implementation for __repr__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__repr__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__repr__ failed: {e}")
            raise
    sync_type = Column(String(50), nullable=False)  # full, incremental, webhook
    sync_direction = Column(String(20), nullable=False)  # inbound, outbound, bidirectional
    
    # Résultats de la synchronisation
    sync_status = Column(String(20), nullable=False, index=True)  # success, failure, partial
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Timing et performance
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer, default=0)
    
    # Détails et erreurs
    sync_details = Column(JSONB, default=dict)
    error_details = Column(JSONB, default=dict)
    warning_messages = Column(JSONB, default=list)
    
    # Métadonnées
    triggered_by = Column(String(50))  # system, user, webhook, schedule
    execution_context = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        try:
            logger.info(f"Executing __repr__")
            
            # Implementation for __repr__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__repr__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__repr__ failed: {e}")
            raise
    sync_direction = Column(String(20), nullable=False)  # inbound, outbound, bidirectional
    
    # Résultats de la synchronisation
    sync_status = Column(String(20), nullable=False, index=True)  # success, failure, partial
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Timing et performance
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer, default=0)
    
    # Détails et erreurs
    sync_details = Column(JSONB, default=dict)
    error_details = Column(JSONB, default=dict)
    warning_messages = Column(JSONB, default=list)
    
    # Métadonnées
    triggered_by = Column(String(50))  # system, user, webhook, schedule
    execution_context = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PlatformSyncLog(platform={self.platform_name}, status={self.sync_status})>"
    
    @property
    def success_rate(self) -> float:
        """Calcule le taux de succès de cette synchronisation."""
        if self.records_processed == 0:
            return 100.0
        return ((self.records_processed - self.records_failed) / self.records_processed) * 100
        if not self.is_verified:
            health_score *= 0.8
            
        return min(100.0, max(0.0, health_score))
    
    def update_api_usage(self, success: bool = True, error_message: str = None):
        """
Met à jour les métriques d'utilisation de l'API."""
        self.total_requests += 1
        
        if success:
            self.last_success = datetime.utcnow()
        else:
            self.failed_requests += 1
            if error_message:
                self.last_error = error_message


class PlatformEndpoint(BaseModel):
    """
    Modèle pour les endpoints d'API des plateformes.
    
    Stocke les configurations et limites des endpoints spécifiques
    pour chaque plateforme.
    """
    
    __tablename__ = "platform_endpoints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    endpoint_name = Column(String(100), nullable=False)
    endpoint_url = Column(Text, nullable=False)
    http_method = Column(String(10), default="GET")
    
    # Configuration de l'endpoint
    requires_auth = Column(Boolean, default=True)
    required_scopes = Column(JSONB, default=list)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # Paramètres et réponse
    request_parameters = Column(JSONB, default=dict)
    response_schema = Column(JSONB, default=dict)
    
    # Métriques d'utilisation
    usage_count = Column(Integer, default=0)
    average_response_time = Column(Integer, default=0)  # en millisecondes
    
    # Statut
    is_active = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)
    deprecation_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformEndpoint(platform={self.platform_name}, endpoint={self.endpoint_name})>"


class PlatformWebhook(BaseModel):
    """
    Modèle pour les webhooks des plateformes.
    
    Gestion des webhooks entrants et sortants pour la synchronisation
    en temps réel avec les plateformes externes.
    """
    
    __tablename__ = "platform_webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    webhook_type = Column(String(20), nullable=False)  # incoming, outgoing
    
    # Configuration du webhook
    webhook_url = Column(Text, nullable=False)
    secret_key = Column(String(255))
    event_types = Column(JSONB, default=list)
    
    # Headers et authentification
    headers = Column(JSONB, default=dict)
    auth_method = Column(String(20), default="signature")  # signature, bearer, none
    
    # Statut et métriques
    is_active = Column(Boolean, default=True)
    total_events = Column(Integer, default=0)
    successful_events = Column(Integer, default=0)
    failed_events = Column(Integer, default=0)
    
    last_event_received = Column(DateTime(timezone=True))
    last_event_sent = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformWebhook(type={self.webhook_type}, platform={self.platform_connection_id})>"


class PlatformSyncLog(BaseModel):
    """
    Modèle pour les logs de synchronisation avec les plateformes.
    
    Trace toutes les opérations de synchronisation pour audit et débogage.
    """
    
    __tablename__ = "platform_sync_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Détails de la synchronisation
    sync_type = Column(String(30), nullable=False)  # upload, download, update, delete
    operation = Column(String(50), nullable=False)
    
    # Données synchronisées
    content_type = Column(String(30))  # audio, video, image, post, analytics
    content_id = Column(String(255))
    external_content_id = Column(String(255))
    
    # Statut et résultat
    status = Column(String(20), nullable=False)  # pending, success, failed, partial
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Détails techniques
    request_data = Column(JSONB)
    response_data = Column(JSONB)
    error_message = Column(Text)
    error_code = Column(String(50))
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PlatformSyncLog(operation={self.operation}, status={self.status})>"
    
    @property
    def success_rate(self) -> float:
        """Calcule le taux de succès de la synchronisation."""
        if self.records_processed == 0:
            return 0.0
        return (self.records_successful / self.records_processed) * 100


# Index et contraintes pour optimisation des performances
from sqlalchemy import Index

# Index composites pour les requêtes fréquentes
platform_connection_user_platform_idx = Index(
    'idx_platform_connections_user_platform',
    PlatformConnection.user_id,
    PlatformConnection.platform_name
)

platform_sync_log_connection_status_idx = Index(
    'idx_platform_sync_logs_connection_status',
    PlatformSyncLog.platform_connection_id,
    PlatformSyncLog.status
)

platform_endpoint_platform_active_idx = Index(
    'idx_platform_endpoints_platform_active',
    PlatformEndpoint.platform_name,
    PlatformEndpoint.is_active
)
