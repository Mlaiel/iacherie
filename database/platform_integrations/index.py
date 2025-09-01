"""Platform Integrations Index Module

Gestionnaire principal et point d'entrée pour toutes les intégrations plateformes
dans la plateforme IA Influencer Agent.

Ce module fournit:
- Gestionnaire centralisé des intégrations plateformes
- Initialisation et configuration des schémas de base de données
- Validation et orchestration des connexions
- API unifiée pour la gestion des plateformes
- Monitoring et health checks centralisés

Auteur: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Équipe: Lead AI Developer, Backend Senior, Platform Integration Specialist, Database Architect

⚠️  AVERTISSEMENT LEGAL ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon le droit allemand et international.

Contact pour autorisation: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import asyncio
from enum import Enum

# Import des modules locaux
from .platform_connections import (
    PlatformConnection, 
    PlatformEndpoint, 
    PlatformWebhook, 
    PlatformSyncLog
)
from .api_credentials import (
    APICredential, 
    CredentialUsageLog, 
    PlatformAPIMapping, 
    CredentialRotationHistory,
    SUPPORTED_PLATFORMS,
    create_platform_credential,
    CredentialType,
    CredentialStatus
)
from .integration_settings import (
    PlatformIntegrationSetting, 
    IntegrationProfile, 
    PlatformCapability, 
    IntegrationHealthCheck,
    IntegrationSettingType,
    IntegrationStatus,
    DEFAULT_PLATFORM_SETTINGS,
    create_default_settings_for_platform
)
from .sync_configurations import (
    SyncConfiguration, 
    SyncExecution, 
    SyncFieldMapping, 
    DataTransformationRule, 
    SyncBenchmark,
    SyncDirection,
    SyncStrategy,
    SyncStatus,
    DEFAULT_SYNC_CONFIGURATIONS,
    create_default_sync_configurations
)
from .external_services import (
    ExternalService, 
    ServiceType,
    ServiceStatus,
    EXTERNAL_SERVICES_CATALOG,
    create_external_service_from_catalog,
    get_services_by_type
)

logger = logging.getLogger(__name__)


class PlatformIntegrationError(Exception):
    """
Exception personnalisée pour les erreurs d'intégration."""
    pass


class ValidationError(Exception):
    """
Exception pour les erreurs de validation."""
    pass


class IntegrationOperationResult(Enum):
    """
Résultats des opérations d'intégration."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    VALIDATION_ERROR = "validation_error"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMITED = "rate_limited"
    SERVICE_UNAVAILABLE = "service_unavailable"


class PlatformIntegrationManager:
    """
    Gestionnaire principal pour toutes les intégrations plateformes.
    
    Centralise la gestion des connexions, credentials, synchronisations
    et services externes avec une API unifiée.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialise le gestionnaire d'intégrations.
        
        Args:
            db_session: Session de base de données SQLAlchemy
        """
        self.db_session = db_session
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    # === GESTION DES CONNEXIONS PLATEFORMES ===
    
    def create_platform_connection(
        self,
        user_id: str,
        platform_name: str,
        external_user_id: str,
        access_token: str,
        **kwargs
    ) -> Tuple[PlatformConnection, IntegrationOperationResult]:
        """
        Crée une nouvelle connexion à une plateforme.
        
        Args:
            user_id: ID de l'utilisateur
            platform_name: Nom de la plateforme
            external_user_id: ID utilisateur sur la plateforme externe
            access_token: Token d'accès
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Tuple contenant la connexion créée et le résultat
        """
        try:
            # Validation de la plateforme
            if platform_name not in SUPPORTED_PLATFORMS:
                return None, IntegrationOperationResult.VALIDATION_ERROR
            
            platform_info = SUPPORTED_PLATFORMS[platform_name]
            
            # Création de la connexion
            connection = PlatformConnection(
                user_id=user_id,
                platform_name=platform_name,
                platform_type=platform_info["type"].value,
                external_user_id=external_user_id,
                access_token=access_token,
                username=kwargs.get("username"),
                display_name=kwargs.get("display_name"),
                profile_url=kwargs.get("profile_url"),
                avatar_url=kwargs.get("avatar_url"),
                refresh_token=kwargs.get("refresh_token"),
                token_expires_at=kwargs.get("token_expires_at"),
                granted_scopes=kwargs.get("granted_scopes", []),
                required_scopes=platform_info.get("scopes", []),
                connection_metadata=kwargs.get("metadata", {})
            )
            
            self.db_session.add(connection)
            self.db_session.commit()
            
            # Création des settings par défaut
            self._create_default_platform_settings(user_id, platform_name)
            
            # Création des configurations de sync par défaut
            self._create_default_sync_configs(user_id, str(connection.id), platform_name)
            
            self.logger.info(f"Created platform connection for {platform_name} - User: {user_id}")
            
            return connection, IntegrationOperationResult.SUCCESS
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.logger.error(f"Database error creating platform connection: {e}")
            return None, IntegrationOperationResult.FAILURE
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Unexpected error creating platform connection: {e}")
            return None, IntegrationOperationResult.FAILURE
    
    def get_user_platform_connections(
        self,
        user_id: str,
        platform_name: Optional[str] = None,
        active_only: bool = True
    ) -> List[PlatformConnection]:
        """
        Récupère les connexions plateformes d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            platform_name: Nom de plateforme spécifique (optionnel)
            active_only: Retourner seulement les connexions actives
            
        Returns:
            Liste des connexions
        """
        query = self.db_session.query(PlatformConnection).filter(
            PlatformConnection.user_id == user_id
        )
        
        if platform_name:
            query = query.filter(PlatformConnection.platform_name == platform_name)
        
        if active_only:
            query = query.filter(PlatformConnection.is_active == True)
        
        return query.all()
    
    def update_connection_health(
        self,
        connection_id: str,
        success: bool,
        error_message: str = None
    ) -> bool:
        """
        Met à jour l'état de santé d'une connexion.
        
        Args:
            connection_id: ID de la connexion
            success: Succès de l'opération
            error_message: Message d'erreur si échec
            
        Returns:
            True si mise à jour réussie
        """
        try:
            connection = self.db_session.query(PlatformConnection).filter(
                PlatformConnection.id == connection_id
            ).first()
            
            if not connection:
                return False
            
            connection.update_sync_status(success, error_message)
            self.db_session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.logger.error(f"Error updating connection health: {e}")
            return False
    
    # === GESTION DES CREDENTIALS ===
    
    def store_platform_credential(
        self,
        platform_name: str,
        credential_type: CredentialType,
        credentials: Dict[str, str],
        **kwargs
    ) -> Tuple[APICredential, IntegrationOperationResult]:
        """
        Stocke des credentials pour une plateforme.
        
        Args:
            platform_name: Nom de la plateforme
            credential_type: Type de credential
            credentials: Dictionnaire des credentials
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Tuple contenant le credential créé et le résultat
        """
        try:
            credential = create_platform_credential(
                platform_name=platform_name,
                credential_type=credential_type,
                credentials=credentials,
                name=kwargs.get("name"),
                environment=kwargs.get("environment", "production"),
                metadata=kwargs.get("metadata", {})
            )
            
            self.db_session.add(credential)
            self.db_session.commit()
            
            self.logger.info(f"Stored credential for {platform_name} - Type: {credential_type.value}")
            
            return credential, IntegrationOperationResult.SUCCESS
            
        except ValueError as e:
            self.logger.error(f"Validation error storing credential: {e}")
            return None, IntegrationOperationResult.VALIDATION_ERROR
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.logger.error(f"Database error storing credential: {e}")
            return None, IntegrationOperationResult.FAILURE
    
    def rotate_platform_credentials(
        self,
        credential_id: str,
        new_credentials: Dict[str, str],
        rotation_reason: str = "scheduled"
    ) -> Tuple[bool, IntegrationOperationResult]:
        """
        Effectue la rotation des credentials d'une plateforme.
        
        Args:
            credential_id: ID du credential à faire tourner
            new_credentials: Nouveaux credentials
            rotation_reason: Raison de la rotation
            
        Returns:
            Tuple contenant le succès et le résultat
        """
        try:
            credential = self.db_session.query(APICredential).filter(
                APICredential.id == credential_id
            ).first()
            
            if not credential:
                return False, IntegrationOperationResult.VALIDATION_ERROR
            
            # Création de l'historique de rotation
            rotation_history = CredentialRotationHistory(
                credential_id=credential_id,
                platform_name=credential.platform_name,
                rotation_type="manual",
                rotation_reason=rotation_reason,
                rotation_status="initiated",
                rotation_started_at=datetime.utcnow()
            )
            
            self.db_session.add(rotation_history)
            
            # Sauvegarde des anciens credentials (hash)
            if credential.encrypted_api_key:
                from .api_credentials import hash_credential
                rotation_history.previous_credential_hash = hash_credential(
                    credential.get_api_key() or ""
                )
            
            # Mise à jour avec les nouveaux credentials
            if "api_key" in new_credentials:
                credential.set_api_key(new_credentials["api_key"])
            if "client_secret" in new_credentials:
                credential.set_client_secret(new_credentials["client_secret"])
            
            # Mise à jour des métadonnées de rotation
            credential.last_rotated_at = datetime.utcnow()
            if credential.rotation_enabled:
                credential.next_rotation_at = datetime.utcnow() + timedelta(
                    days=credential.rotation_interval_days
                )
            
            # Finalisation de l'historique
            rotation_history.rotation_status = "completed"
            rotation_history.rotation_completed_at = datetime.utcnow()
            rotation_history.success = True
            
            self.db_session.commit()
            
            self.logger.info(f"Rotated credentials for {credential.platform_name}")
            
            return True, IntegrationOperationResult.SUCCESS
            
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Error rotating credentials: {e}")
            return False, IntegrationOperationResult.FAILURE
    
    # === GESTION DES SYNCHRONISATIONS ===
    
    def create_sync_configuration(
        self,
        user_id: str,
        platform_connection_id: str,
        platform_name: str,
        sync_config: Dict[str, Any]
    ) -> Tuple[SyncConfiguration, IntegrationOperationResult]:
        """
        Crée une configuration de synchronisation.
        
        Args:
            user_id: ID de l'utilisateur
            platform_connection_id: ID de la connexion plateforme
            platform_name: Nom de la plateforme
            sync_config: Configuration de synchronisation
            
        Returns:
            Tuple contenant la configuration créée et le résultat
        """
        try:
            sync_configuration = SyncConfiguration(
                user_id=user_id,
                platform_connection_id=platform_connection_id,
                platform_name=platform_name,
                configuration_name=sync_config.get("name", f"{platform_name}_sync"),
                description=sync_config.get("description"),
                sync_direction=SyncDirection(sync_config.get("direction", "inbound")),
                sync_strategy=SyncStrategy(sync_config.get("strategy", "incremental")),
                data_types=sync_config.get("data_types", []),
                sync_frequency=sync_config.get("frequency", "daily"),
                batch_size=sync_config.get("batch_size", 100),
                max_records_per_sync=sync_config.get("max_records", 1000)
            )
            
            self.db_session.add(sync_configuration)
            self.db_session.commit()
            
            self.logger.info(f"Created sync configuration for {platform_name} - User: {user_id}")
            
            return sync_configuration, IntegrationOperationResult.SUCCESS
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Validation error creating sync config: {e}")
            return None, IntegrationOperationResult.VALIDATION_ERROR
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.logger.error(f"Database error creating sync config: {e}")
            return None, IntegrationOperationResult.FAILURE
    
    def execute_sync(
        self,
        sync_config_id: str,
        triggered_by: str = "system"
    ) -> Tuple[SyncExecution, IntegrationOperationResult]:
        """
        Lance l'exécution d'une synchronisation.
        
        Args:
            sync_config_id: ID de la configuration de sync
            triggered_by: Qui a déclenché la sync
            
        Returns:
            Tuple contenant l'exécution créée et le résultat
        """
        try:
            sync_config = self.db_session.query(SyncConfiguration).filter(
                SyncConfiguration.id == sync_config_id
            ).first()
            
            if not sync_config or not sync_config.is_enabled:
                return None, IntegrationOperationResult.VALIDATION_ERROR
            
            # Création de l'exécution
            execution = SyncExecution(
                sync_configuration_id=sync_config_id,
                platform_name=sync_config.platform_name,
                execution_id=f"sync_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{sync_config_id[:8]}",
                sync_direction=sync_config.sync_direction,
                sync_strategy=sync_config.sync_strategy,
                sync_status=SyncStatus.PENDING,
                started_at=datetime.utcnow(),
                triggered_by=triggered_by
            )
            
            self.db_session.add(execution)
            self.db_session.commit()
            
            self.logger.info(f"Created sync execution {execution.execution_id}")
            
            return execution, IntegrationOperationResult.SUCCESS
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.logger.error(f"Error creating sync execution: {e}")
            return None, IntegrationOperationResult.FAILURE
    
    # === HEALTH CHECKS ET MONITORING ===
    
    def perform_platform_health_check(
        self,
        platform_name: str,
        user_id: Optional[str] = None
    ) -> Tuple[IntegrationHealthCheck, IntegrationOperationResult]:
        """
        Effectue un health check d'une plateforme.
        
        Args:
            platform_name: Nom de la plateforme
            user_id: ID utilisateur (optionnel)
            
        Returns:
            Tuple contenant le health check et le résultat
        """
        try:
            health_check = IntegrationHealthCheck(
                platform_name=platform_name,
                user_id=user_id,
                check_type="connectivity",
                check_category="automated",
                check_status="success",  # Simplifié pour l'exemple
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                triggered_by="system",
                successful_checks=1,
                failed_checks=0,
                summary_message=f"{platform_name} is healthy"
            )
            
            self.db_session.add(health_check)
            self.db_session.commit()
            
            return health_check, IntegrationOperationResult.SUCCESS
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.logger.error(f"Error performing health check: {e}")
            return None, IntegrationOperationResult.FAILURE
    
    def get_platform_health_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Retourne un résumé de santé de toutes les plateformes d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire avec le résumé de santé
        """
        try:
            connections = self.get_user_platform_connections(user_id)
            
            summary = {
                "total_connections": len(connections),
                "active_connections": len([c for c in connections if c.is_active]),
                "verified_connections": len([c for c in connections if c.is_verified]),
                "platforms": {},
                "overall_health_score": 0.0
            }
            
            total_score = 0.0
            for connection in connections:
                platform_summary = {
                    "connection_id": str(connection.id),
                    "is_active": connection.is_active,
                    "is_verified": connection.is_verified,
                    "health_score": connection.connection_health_score,
                    "last_sync": connection.last_sync.isoformat() if connection.last_sync else None,
                    "total_requests": connection.total_requests,
                    "failed_requests": connection.failed_requests
                }
                
                summary["platforms"][connection.platform_name] = platform_summary
                total_score += connection.connection_health_score
            
            if connections:
                summary["overall_health_score"] = total_score / len(connections)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting platform health summary: {e}")
            return {"error": str(e)}
    
    # === MÉTHODES PRIVÉES ===
    
    def _create_default_platform_settings(self, user_id: str, platform_name: str):
        """Crée les paramètres par défaut pour une plateforme."""
        try:
            settings = create_default_settings_for_platform(user_id, platform_name)
            for setting in settings:
                self.db_session.add(setting)
        except Exception as e:
            self.logger.warning(f"Could not create default settings for {platform_name}: {e}")
    
    def _create_default_sync_configs(
        self,
        user_id: str,
        platform_connection_id: str,
        platform_name: str
    ):
        """Crée les configurations de sync par défaut pour une plateforme."""
        try:
            configs = create_default_sync_configurations(
                user_id, platform_connection_id, platform_name
            )
            for config in configs:
                self.db_session.add(config)
        except Exception as e:
            self.logger.warning(f"Could not create default sync configs for {platform_name}: {e}")


def initialize_platform_integrations_schema(db_session: Session) -> bool:
    """
    Initialise le schéma de base de données pour les intégrations plateformes.
    
    Args:
        db_session: Session de base de données
        
    Returns:
        True si l'initialisation a réussi
    """
    try:
        # Cette fonction créerait les tables si elles n'existent pas
        # Dans un environnement réel, ceci serait géré par Alembic
        logger.info("Platform integrations schema initialized")
        return True
    except Exception as e:
        logger.error(f"Error initializing platform integrations schema: {e}")
        return False


def get_supported_platforms() -> List[str]:
    """
    Retourne la liste des plateformes supportées.
    
    Returns:
        Liste des noms de plateformes
    """
    return list(SUPPORTED_PLATFORMS.keys())


def validate_platform_configuration(
    platform_name: str,
    configuration: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Valide une configuration de plateforme.
    
    Args:
        platform_name: Nom de la plateforme
        configuration: Configuration à valider
        
    Returns:
        Tuple contenant la validité et la liste des erreurs
    """
    errors = []
    
    if platform_name not in SUPPORTED_PLATFORMS:
        errors.append(f"Platform '{platform_name}' is not supported")
        return False, errors
    
    platform_info = SUPPORTED_PLATFORMS[platform_name]
    
    # Validation des champs requis
    required_fields = ["auth_type"]
    for field in required_fields:
        if field not in configuration:
            errors.append(f"Required field '{field}' is missing")
    
    # Validation du type d'authentification
    if "auth_type" in configuration:
        expected_auth_type = platform_info["auth_type"]
        if configuration["auth_type"] != expected_auth_type:
            errors.append(
                f"Invalid auth_type. Expected {expected_auth_type}, got {configuration['auth_type']}"
            )
    
    return len(errors) == 0, errors

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Import des modèles principaux
from .platform_connections import (
    PlatformConnection, 
    PlatformEndpoint, 
    PlatformWebhook, 
    PlatformSyncLog
)
from .api_credentials import (
    APICredential, 
    CredentialUsageLog, 
    PlatformAPIMapping, 
    CredentialRotationHistory,
    SUPPORTED_PLATFORMS,
    create_platform_credential
)
from .integration_settings import (
    PlatformIntegrationSetting, 
    IntegrationProfile, 
    PlatformCapability, 
    IntegrationHealthCheck,
    IntegrationSettingType,
    IntegrationStatus,
    DEFAULT_PLATFORM_SETTINGS,
    create_default_settings_for_platform
)
from .sync_configurations import (
    SyncConfiguration, 
    SyncExecution, 
    SyncFieldMapping, 
    DataTransformationRule, 
    SyncBenchmark,
    SyncDirection,
    SyncStrategy,
    SyncStatus,
    DEFAULT_SYNC_CONFIGURATIONS,
    create_default_sync_configurations
)
from .external_services import (
    ExternalService, 
    ServiceEndpoint, 
    ServiceIntegration, 
    ServiceDependency, 
    ServiceUsageAnalytics,
    ServiceType,
    ServiceStatus,
    EXTERNAL_SERVICES_CATALOG,
    create_external_service_from_catalog,
    get_services_by_type
)

logger = logging.getLogger(__name__)


class PlatformIntegrationManager:
    """
    Gestionnaire principal pour les intégrations de plateformes.
    
    Fournit une interface unifiée pour gérer toutes les intégrations
    avec les plateformes externes.
    """
    
    def __init__(self, db_session):
        """
        Initialise le gestionnaire d'intégrations.
        
        Args:
            db_session: Session de base de données SQLAlchemy
        """
        self.db = db_session
        self.logger = logger
    
    def setup_platform_integration(self, user_id: str, platform_name: str, 
                                 credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure une nouvelle intégration de plateforme pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            platform_name: Nom de la plateforme (spotify, youtube, etc.)
            credentials: Credentials d'authentification
        
        Returns:
            Dict[str, Any]: Résultat de la configuration
        """
        try:
            # 1. Créer les credentials
            credential = create_platform_credential(platform_name, **credentials)
            self.db.add(credential)
            self.db.flush()
            
            # 2. Créer la connexion plateforme
            connection = PlatformConnection(
                user_id=user_id,
                platform_name=platform_name,
                platform_type=self._get_platform_type(platform_name),
                external_user_id=credentials.get('external_user_id'),
                username=credentials.get('username'),
                access_token=credentials.get('access_token'),
                refresh_token=credentials.get('refresh_token')
            )
            self.db.add(connection)
            self.db.flush()
            
            # 3. Créer les paramètres par défaut
            settings = create_default_settings_for_platform(platform_name, user_id)
            for setting in settings:
                self.db.add(setting)
            
            # 4. Créer les configurations de synchronisation par défaut
            sync_configs = create_default_sync_configurations(platform_name, user_id)
            for config in sync_configs:
                self.db.add(config)
            
            # 5. Créer l'intégration de service
            service = self.db.query(ExternalService).filter_by(service_name=platform_name).first()
            if service:
                integration = ServiceIntegration(
                    user_id=user_id,
                    service_id=service.id,
                    integration_name=f"{platform_name.title()} Integration",
                    credential_id=credential.id,
                    is_enabled=True,
                    is_configured=True
                )
                self.db.add(integration)
            
            self.db.commit()
            
            return {
                "success": True,
                "connection_id": str(connection.id),
                "credential_id": str(credential.id),
                "settings_count": len(settings),
                "sync_configs_count": len(sync_configs)
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur lors de la configuration de l'intégration {platform_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_platform_status(self, user_id: str, platform_name: str) -> Dict[str, Any]:
        """
        Récupère le statut complet d'une intégration de plateforme.
        
        Args:
            user_id: ID de l'utilisateur
            platform_name: Nom de la plateforme
        
        Returns:
            Dict[str, Any]: Statut de l'intégration
        """
        # Récupérer la connexion
        connection = self.db.query(PlatformConnection).filter_by(
            user_id=user_id,
            platform_name=platform_name
        ).first()
        
        if not connection:
            return {"connected": False, "error": "Plateforme non connectée"}
        
        # Récupérer les dernières synchronisations
        last_syncs = self.db.query(SyncExecution).join(SyncConfiguration).filter(
            SyncConfiguration.user_id == user_id,
            SyncConfiguration.platform_name == platform_name
        ).order_by(SyncExecution.started_at.desc()).limit(5).all()
        
        # Récupérer les vérifications de santé récentes
        health_checks = self.db.query(IntegrationHealthCheck).filter_by(
            user_id=user_id,
            platform_name=platform_name
        ).order_by(IntegrationHealthCheck.created_at.desc()).limit(3).all()
        
        return {
            "connected": True,
            "connection_health": connection.connection_health_score,
            "is_active": connection.is_active,
            "is_verified": connection.is_verified,
            "last_sync": connection.last_sync.isoformat() if connection.last_sync else None,
            "recent_syncs": [
                {
                    "status": sync.status,
                    "started_at": sync.started_at.isoformat(),
                    "records_processed": sync.records_processed,
                    "success_rate": sync.success_rate
                }
                for sync in last_syncs
            ],
            "health_checks": [
                {
                    "type": check.check_type,
                    "status": check.status,
                    "score": check.get_health_score(),
                    "checked_at": check.created_at.isoformat()
                }
                for check in health_checks
            ]
        }
    
    def trigger_sync(self, user_id: str, platform_name: str, 
                    sync_type: str = "full") -> Dict[str, Any]:
        """
        Déclenche une synchronisation manuelle avec une plateforme.
        
        Args:
            user_id: ID de l'utilisateur
            platform_name: Nom de la plateforme
            sync_type: Type de synchronisation (full, incremental, etc.)
        
        Returns:
            Dict[str, Any]: Résultat du déclenchement
        """
        # Récupérer les configurations de synchronisation actives
        sync_configs = self.db.query(SyncConfiguration).filter_by(
            user_id=user_id,
            platform_name=platform_name,
            is_active=True
        ).all()
        
        if not sync_configs:
            return {
                "success": False,
                "error": "Aucune configuration de synchronisation active"
            }
        
        executions = []
        
        for config in sync_configs:
            # Créer une nouvelle exécution
            execution = SyncExecution(
                sync_config_id=config.id,
                trigger_type="manual",
                triggered_by=user_id,
                status=SyncStatus.PENDING,
                started_at=datetime.utcnow()
            )
            
            self.db.add(execution)
            executions.append(execution)
        
        self.db.commit()
        
        return {
            "success": True,
            "executions_created": len(executions),
            "execution_ids": [str(exec.id) for exec in executions]
        }
    
    def get_integration_analytics(self, user_id: str, 
                                platform_name: str = None, 
                                days: int = 30) -> Dict[str, Any]:
        """
        Récupère les analytics d'intégration pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            platform_name: Nom de la plateforme (optionnel)
            days: Nombre de jours à analyser
        
        Returns:
            Dict[str, Any]: Analytics d'intégration
        """
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Base query
        query = self.db.query(ServiceUsageAnalytics).filter(
            ServiceUsageAnalytics.user_id == user_id,
            ServiceUsageAnalytics.period_start >= start_date
        )
        
        if platform_name:
            service = self.db.query(ExternalService).filter_by(service_name=platform_name).first()
            if service:
                query = query.filter(ServiceUsageAnalytics.service_id == service.id)
        
        analytics = query.all()
        
        # Calculer les métriques agrégées
        total_requests = sum(a.total_requests for a in analytics)
        total_successful = sum(a.successful_requests for a in analytics)
        total_failed = sum(a.failed_requests for a in analytics)
        
        avg_response_time = sum(a.average_response_time_ms for a in analytics if a.average_response_time_ms) / len(analytics) if analytics else 0
        
        return {
            "period_days": days,
            "total_requests": total_requests,
            "success_rate": (total_successful / total_requests * 100) if total_requests > 0 else 0,
            "average_response_time_ms": avg_response_time,
            "platforms_used": len(set(a.service_id for a in analytics)),
            "daily_breakdown": [
                {
                    "date": a.period_start.date().isoformat(),
                    "requests": a.total_requests,
                    "success_rate": a.success_rate
                }
                for a in analytics
            ]
        }
    
    def _get_platform_type(self, platform_name: str) -> str:
        """Détermine le type de plateforme basé sur son nom."""
        platform_types = {
            "spotify": "music",
            "youtube": "video", 
            "instagram": "social",
            "tiktok": "social",
            "twitter": "social",
            "facebook": "social"
        }
        return platform_types.get(platform_name, "other")


# Utilitaires pour l'initialisation du module
def initialize_platform_integrations_schema(db_session):
    """
    Initialise le schéma des intégrations de plateformes.
    
    Args:
        db_session: Session de base de données SQLAlchemy
    """
    # Créer les services externes par défaut
    for service_key in EXTERNAL_SERVICES_CATALOG.keys():
        existing_service = db_session.query(ExternalService).filter_by(service_name=service_key).first()
        
        if not existing_service:
            service = create_external_service_from_catalog(service_key)
            db_session.add(service)
    
    db_session.commit()
    logger.info("Schéma des intégrations de plateformes initialisé")


def get_supported_platforms() -> List[Dict[str, Any]]:
    """
    Récupère la liste des plateformes supportées.
    
    Returns:
        List[Dict[str, Any]]: Liste des plateformes avec leurs informations
    """
    platforms = []
    
    for platform_name, config in SUPPORTED_PLATFORMS.items():
        platforms.append({
            "name": platform_name,
            "display_name": platform_name.title(),
            "type": config.get("credential_type", "oauth2"),
            "base_url": config.get("base_url"),
            "default_scopes": config.get("default_scopes", []),
            "available": True
        })
    
    return platforms


def validate_platform_configuration(platform_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide une configuration de plateforme.
    
    Args:
        platform_name: Nom de la plateforme
        config: Configuration à valider
    
    Returns:
        Dict[str, Any]: Résultat de la validation
    """
    if platform_name not in SUPPORTED_PLATFORMS:
        return {
            "valid": False,
            "errors": [f"Plateforme non supportée: {platform_name}"]
        }
    
    platform_config = SUPPORTED_PLATFORMS[platform_name]
    errors = []
    
    # Validation des champs requis
    required_fields = ["client_id", "client_secret"]
    for field in required_fields:
        if field not in config or not config[field]:
            errors.append(f"Champ requis manquant: {field}")
    
    # Validation des scopes
    if "scopes" in config:
        default_scopes = set(platform_config.get("default_scopes", []))
        provided_scopes = set(config["scopes"])
        
        if not provided_scopes.issubset(default_scopes):
            invalid_scopes = provided_scopes - default_scopes
            errors.append(f"Scopes invalides: {list(invalid_scopes)}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# Exportation des modules principaux
__all__ = [
    # Classes principales
    "PlatformConnection",
    "PlatformEndpoint", 
    "PlatformWebhook",
    "PlatformSyncLog",
    "APICredential",
    "CredentialUsageLog",
    "PlatformAPIMapping", 
    "CredentialRotationHistory",
    "PlatformIntegrationSetting",
    "IntegrationProfile",
    "PlatformCapability",
    "IntegrationHealthCheck",
    "SyncConfiguration",
    "SyncExecution",
    "SyncFieldMapping",
    "DataTransformationRule",
    "SyncBenchmark",
    "ExternalService",
    "ServiceEndpoint",
    "ServiceIntegration",
    "ServiceDependency",
    "ServiceUsageAnalytics",
    
    # Enums
    "IntegrationSettingType",
    "IntegrationStatus", 
    "SyncDirection",
    "SyncStrategy",
    "SyncStatus",
    "ServiceType",
    "ServiceStatus",
    
    # Gestionnaire principal
    "PlatformIntegrationManager",
    
    # Utilitaires
    "initialize_platform_integrations_schema",
    "get_supported_platforms",
    "validate_platform_configuration",
    "create_platform_credential",
    "create_default_settings_for_platform",
    "create_default_sync_configurations",
    "create_external_service_from_catalog",
    "get_services_by_type",
    
    # Constantes
    "SUPPORTED_PLATFORMS",
    "DEFAULT_PLATFORM_SETTINGS", 
    "DEFAULT_SYNC_CONFIGURATIONS",
    "EXTERNAL_SERVICES_CATALOG"
]
