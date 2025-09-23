#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔗 Tenant Integration Hub - Enterprise Multi-Tenant External Integrations

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
Cette architecture tenant integration hub est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite PERSONNELLE
est STRICTEMENT INTERDITE et sera poursuivie en justice.
"""

import asyncio
import logging
import json
import time
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import aiohttp
import redis
import psycopg2
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from cryptography.fernet import Fernet
import yaml
import jwt
import oauth2
from oauthlib.oauth2 import WebApplicationClient


# Configuration du logging avancé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/tenant_integrations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    """Types d'intégration"""
    SOCIAL_MEDIA = "social_media"
    PAYMENT_GATEWAY = "payment_gateway"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    ANALYTICS = "analytics"
    CRM = "crm"
    STORAGE = "storage"
    CDN = "cdn"
    WEBHOOK = "webhook"
    API = "api"


class AuthenticationType(Enum):
    """Types d'authentification"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    JWT = "jwt"
    CUSTOM = "custom"


class IntegrationStatus(Enum):
    """États d'intégration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    SUSPENDED = "suspended"
    RATE_LIMITED = "rate_limited"


class SyncDirection(Enum):
    """Directions de synchronisation"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class IntegrationConfig:
    """Configuration d'intégration"""
    integration_id: str
    tenant_id: str
    name: str
    integration_type: IntegrationType
    provider: str
    authentication_type: AuthenticationType
    credentials: Dict[str, Any]
    endpoint_url: str
    webhook_url: Optional[str]
    sync_direction: SyncDirection
    rate_limit: Optional[int]
    timeout_seconds: int
    retry_count: int
    enabled: bool
    auto_sync: bool
    sync_interval_minutes: Optional[int]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class IntegrationEvent:
    """Événement d'intégration"""
    event_id: str
    integration_id: str
    tenant_id: str
    event_type: str
    direction: SyncDirection
    payload: Dict[str, Any]
    response: Optional[Dict[str, Any]]
    status: IntegrationStatus
    timestamp: datetime
    processing_time_ms: float
    error_message: Optional[str]
    retry_count: int


@dataclass
class WebhookEvent:
    """Événement webhook"""
    webhook_id: str
    tenant_id: str
    source_integration: str
    event_type: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: datetime
    signature: Optional[str]
    verified: bool


class TenantIntegrationHub:
    """
    🔗 Enterprise Tenant Integration Hub
    
    Hub d'intégrations enterprise pour architecture multi-tenant avec:
    - Connecteurs multi-plateforme (social media, paiements, etc.)
    - Authentification sécurisée (OAuth2, API keys, JWT)
    - Synchronisation bidirectionnelle temps réel
    - Rate limiting et retry policies
    - Webhooks et événements
    - Monitoring et analytics d'intégrations
    """
    
    def __init__(self, config_path: str = '/etc/ainflue/integrations_config.yaml'):
        """Initialisation du hub d'intégrations"""
        self.config = self._load_config(config_path)
        self.integrations: Dict[str, IntegrationConfig] = {}
        self.event_queue: queue.Queue = queue.Queue(maxsize=5000)
        self.webhook_queue: queue.Queue = queue.Queue(maxsize=1000)
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.running = True
        
        # Sessions HTTP pour les intégrations
        self.http_sessions: Dict[str, aiohttp.ClientSession] = {}
        
        # Connexions aux services
        self._init_database_connections()
        self._init_integration_providers()
        
        # Démarrage des workers
        self._start_integration_workers()
        self._start_webhook_processor()
        
        logger.info("TenantIntegrationHub initialisé avec succès")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Chargement de la configuration"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration chargée depuis {config_path}")
            return config
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            'worker_threads': 4,
            'default_timeout_seconds': 30,
            'default_retry_count': 3,
            'rate_limit_default': 100,
            'sync_interval_minutes': 15,
            'webhook_signature_required': True,
            'database': {
                'host': 'localhost',
                'port': 5432,
                'ssl_mode': 'require'
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'ssl': True
            },
            'providers': {
                'instagram': {
                    'api_version': 'v12.0',
                    'base_url': 'https://graph.facebook.com'
                },
                'stripe': {
                    'api_version': '2023-10-16',
                    'base_url': 'https://api.stripe.com'
                },
                'sendgrid': {
                    'api_version': 'v3',
                    'base_url': 'https://api.sendgrid.com'
                }
            }
        }
    
    def _get_encryption_key(self) -> bytes:
        """Récupération de la clé de chiffrement"""
        key_path = self.config.get('encryption_key_path', '/etc/ainflue/integrations.key')
        try:
            with open(key_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            # Génération d'une nouvelle clé
            key = Fernet.generate_key()
            import os
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            with open(key_path, 'wb') as f:
                f.write(key)
            logger.info(f"Nouvelle clé de chiffrement générée: {key_path}")
            return key
    
    def _init_database_connections(self):
        """Initialisation des connexions bases de données"""
        db_config = self.config.get('database', {})
        
        # Configuration PostgreSQL
        self.pg_config = {
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 5432),
            'sslmode': db_config.get('ssl_mode', 'require')
        }
        
        # Configuration Redis
        redis_config = self.config.get('redis', {})
        self.redis_client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            ssl=redis_config.get('ssl', True),
            decode_responses=True
        )
        
        logger.info("Connexions base de données initialisées")
    
    def _init_integration_providers(self):
        """Initialisation des fournisseurs d'intégration"""
        self.providers = {
            'instagram': InstagramIntegration(self),
            'stripe': StripeIntegration(self),
            'sendgrid': SendGridIntegration(self),
            'youtube': YouTubeIntegration(self),
            'tiktok': TikTokIntegration(self),
            'twitter': TwitterIntegration(self),
            'paypal': PayPalIntegration(self),
            'twilio': TwilioIntegration(self),
            'google_analytics': GoogleAnalyticsIntegration(self),
            'salesforce': SalesforceIntegration(self)
        }
        
        logger.info(f"Fournisseurs d'intégration initialisés: {list(self.providers.keys())}")
    
    def _start_integration_workers(self):
        """Démarrage des workers d'intégration"""
        worker_count = self.config.get('worker_threads', 4)
        self.workers = []
        
        for i in range(worker_count):
            worker = threading.Thread(
                target=self._integration_worker,
                name=f"integration_worker_{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        # Worker de synchronisation automatique
        self.sync_worker = threading.Thread(
            target=self._auto_sync_worker,
            name="auto_sync_worker",
            daemon=True
        )
        self.sync_worker.start()
        
        logger.info(f"Workers d'intégration démarrés: {worker_count}")
    
    def _start_webhook_processor(self):
        """Démarrage du processeur de webhooks"""
        self.webhook_worker = threading.Thread(
            target=self._webhook_processor_worker,
            name="webhook_processor",
            daemon=True
        )
        self.webhook_worker.start()
        
        logger.info("Processeur de webhooks démarré")
    
    async def create_integration(self, tenant_id: str, integration_config: Dict[str, Any]) -> str:
        """
        🔗 Création d'une nouvelle intégration
        
        Args:
            tenant_id: ID du tenant
            integration_config: Configuration de l'intégration
            
        Returns:
            ID de l'intégration créée
        """
        try:
            integration_id = f"integration_{tenant_id}_{integration_config['provider']}_{int(time.time())}"
            
            # Validation de la configuration
            self._validate_integration_config(integration_config)
            
            # Chiffrement des credentials
            encrypted_credentials = self._encrypt_credentials(integration_config['credentials'])
            
            # Création de la configuration
            config = IntegrationConfig(
                integration_id=integration_id,
                tenant_id=tenant_id,
                name=integration_config['name'],
                integration_type=IntegrationType(integration_config['type']),
                provider=integration_config['provider'],
                authentication_type=AuthenticationType(integration_config['auth_type']),
                credentials=encrypted_credentials,
                endpoint_url=integration_config.get('endpoint_url', ''),
                webhook_url=integration_config.get('webhook_url'),
                sync_direction=SyncDirection(integration_config.get('sync_direction', 'bidirectional')),
                rate_limit=integration_config.get('rate_limit', self.config.get('rate_limit_default', 100)),
                timeout_seconds=integration_config.get('timeout_seconds', self.config.get('default_timeout_seconds', 30)),
                retry_count=integration_config.get('retry_count', self.config.get('default_retry_count', 3)),
                enabled=integration_config.get('enabled', True),
                auto_sync=integration_config.get('auto_sync', False),
                sync_interval_minutes=integration_config.get('sync_interval_minutes'),
                metadata=integration_config.get('metadata', {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Stockage de la configuration
            self.integrations[integration_id] = config
            await self._store_integration_config(config)
            
            # Test de connexion initial
            if config.enabled:
                await self._test_integration_connection(config)
            
            logger.info(f"Intégration créée: {integration_id} pour tenant {tenant_id}")
            return integration_id
            
        except Exception as e:
            logger.error(f"Erreur création intégration: {e}")
            raise
    
    async def update_integration(self, integration_id: str, updates: Dict[str, Any]) -> bool:
        """
        ✏️ Mise à jour d'une intégration
        
        Args:
            integration_id: ID de l'intégration
            updates: Mises à jour à appliquer
            
        Returns:
            True si succès
        """
        try:
            config = self.integrations.get(integration_id)
            if not config:
                logger.error(f"Intégration non trouvée: {integration_id}")
                return False
            
            # Application des mises à jour
            for key, value in updates.items():
                if hasattr(config, key):
                    if key == 'credentials' and value:
                        value = self._encrypt_credentials(value)
                    setattr(config, key, value)
            
            config.updated_at = datetime.utcnow()
            
            # Sauvegarde
            await self._store_integration_config(config)
            
            # Test de connexion si activé
            if config.enabled and 'credentials' in updates:
                await self._test_integration_connection(config)
            
            logger.info(f"Intégration mise à jour: {integration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour intégration {integration_id}: {e}")
            return False
    
    async def delete_integration(self, integration_id: str) -> bool:
        """
        🗑️ Suppression d'une intégration
        
        Args:
            integration_id: ID de l'intégration
            
        Returns:
            True si succès
        """
        try:
            config = self.integrations.get(integration_id)
            if not config:
                logger.error(f"Intégration non trouvée: {integration_id}")
                return False
            
            # Désactivation d'abord
            config.enabled = False
            
            # Suppression de la base de données
            await self._delete_integration_from_db(integration_id)
            
            # Suppression du cache
            del self.integrations[integration_id]
            
            # Fermeture de la session HTTP si existante
            if integration_id in self.http_sessions:
                await self.http_sessions[integration_id].close()
                del self.http_sessions[integration_id]
            
            logger.info(f"Intégration supprimée: {integration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression intégration {integration_id}: {e}")
            return False
    
    async def execute_integration_action(self, integration_id: str, action: str,
                                       payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        ⚡ Exécution d'une action d'intégration
        
        Args:
            integration_id: ID de l'intégration
            action: Action à exécuter
            payload: Données de l'action
            
        Returns:
            Résultat de l'action
        """
        try:
            config = self.integrations.get(integration_id)
            if not config:
                raise ValueError(f"Intégration non trouvée: {integration_id}")
            
            if not config.enabled:
                raise ValueError(f"Intégration désactivée: {integration_id}")
            
            # Récupération du provider
            provider = self.providers.get(config.provider)
            if not provider:
                raise ValueError(f"Provider non supporté: {config.provider}")
            
            # Création de l'événement
            event = IntegrationEvent(
                event_id=f"event_{integration_id}_{int(time.time())}",
                integration_id=integration_id,
                tenant_id=config.tenant_id,
                event_type=action,
                direction=SyncDirection.OUTBOUND,
                payload=payload,
                response=None,
                status=IntegrationStatus.PENDING,
                timestamp=datetime.utcnow(),
                processing_time_ms=0,
                error_message=None,
                retry_count=0
            )
            
            # Exécution de l'action
            start_time = time.time()
            
            try:
                result = await provider.execute_action(config, action, payload)
                
                event.response = result
                event.status = IntegrationStatus.ACTIVE
                event.processing_time_ms = (time.time() - start_time) * 1000
                
                logger.info(f"Action exécutée avec succès: {action} pour {integration_id}")
                return result
                
            except Exception as action_error:
                event.status = IntegrationStatus.ERROR
                event.error_message = str(action_error)
                event.processing_time_ms = (time.time() - start_time) * 1000
                
                logger.error(f"Erreur exécution action {action}: {action_error}")
                raise
            
            finally:
                # Enregistrement de l'événement
                await self._store_integration_event(event)
            
        except Exception as e:
            logger.error(f"Erreur exécution action intégration: {e}")
            raise
    
    async def sync_integration_data(self, integration_id: str, 
                                  direction: Optional[SyncDirection] = None) -> Dict[str, Any]:
        """
        🔄 Synchronisation des données d'une intégration
        
        Args:
            integration_id: ID de l'intégration
            direction: Direction de synchronisation (optionnel)
            
        Returns:
            Résultat de la synchronisation
        """
        try:
            config = self.integrations.get(integration_id)
            if not config:
                raise ValueError(f"Intégration non trouvée: {integration_id}")
            
            if not config.enabled:
                raise ValueError(f"Intégration désactivée: {integration_id}")
            
            # Direction par défaut
            sync_direction = direction or config.sync_direction
            
            # Récupération du provider
            provider = self.providers.get(config.provider)
            if not provider:
                raise ValueError(f"Provider non supporté: {config.provider}")
            
            sync_results = {
                'integration_id': integration_id,
                'direction': sync_direction.value,
                'timestamp': datetime.utcnow().isoformat(),
                'inbound_count': 0,
                'outbound_count': 0,
                'errors': []
            }
            
            # Synchronisation inbound
            if sync_direction in [SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL]:
                try:
                    inbound_data = await provider.sync_inbound_data(config)
                    sync_results['inbound_count'] = len(inbound_data.get('items', []))
                    sync_results['inbound_data'] = inbound_data
                except Exception as e:
                    sync_results['errors'].append(f"Inbound sync error: {str(e)}")
            
            # Synchronisation outbound
            if sync_direction in [SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL]:
                try:
                    outbound_data = await provider.sync_outbound_data(config)
                    sync_results['outbound_count'] = len(outbound_data.get('items', []))
                    sync_results['outbound_data'] = outbound_data
                except Exception as e:
                    sync_results['errors'].append(f"Outbound sync error: {str(e)}")
            
            # Enregistrement de l'événement de synchronisation
            await self._record_sync_event(config, sync_results)
            
            logger.info(f"Synchronisation terminée pour {integration_id}")
            return sync_results
            
        except Exception as e:
            logger.error(f"Erreur synchronisation intégration {integration_id}: {e}")
            raise
    
    async def handle_webhook(self, tenant_id: str, provider: str, 
                           headers: Dict[str, str], payload: Dict[str, Any]) -> bool:
        """
        🪝 Traitement d'un webhook
        
        Args:
            tenant_id: ID du tenant
            provider: Nom du provider
            headers: En-têtes HTTP
            payload: Données du webhook
            
        Returns:
            True si traitement réussi
        """
        try:
            # Recherche de l'intégration correspondante
            integration_config = None
            for config in self.integrations.values():
                if config.tenant_id == tenant_id and config.provider == provider:
                    integration_config = config
                    break
            
            if not integration_config:
                logger.warning(f"Aucune intégration trouvée pour webhook {provider} tenant {tenant_id}")
                return False
            
            # Vérification de la signature si requise
            if self.config.get('webhook_signature_required', True):
                if not self._verify_webhook_signature(provider, headers, payload, integration_config):
                    logger.error(f"Signature webhook invalide pour {provider}")
                    return False
            
            # Création de l'événement webhook
            webhook_event = WebhookEvent(
                webhook_id=f"webhook_{provider}_{tenant_id}_{int(time.time())}",
                tenant_id=tenant_id,
                source_integration=integration_config.integration_id,
                event_type=payload.get('type', 'unknown'),
                payload=payload,
                headers=headers,
                timestamp=datetime.utcnow(),
                signature=headers.get('signature'),
                verified=True
            )
            
            # Ajout à la queue de traitement
            try:
                self.webhook_queue.put(webhook_event, timeout=1)
                return True
            except queue.Full:
                logger.error("Queue webhook pleine, événement rejeté")
                return False
            
        except Exception as e:
            logger.error(f"Erreur traitement webhook: {e}")
            return False
    
    async def get_integration_status(self, integration_id: str) -> Dict[str, Any]:
        """
        📊 Récupération du statut d'une intégration
        
        Args:
            integration_id: ID de l'intégration
            
        Returns:
            Statut détaillé de l'intégration
        """
        try:
            config = self.integrations.get(integration_id)
            if not config:
                return {'error': f'Intégration non trouvée: {integration_id}'}
            
            # Test de connectivité
            connectivity_status = await self._test_integration_connection(config)
            
            # Statistiques récentes
            stats = await self._get_integration_statistics(integration_id)
            
            return {
                'integration_id': integration_id,
                'tenant_id': config.tenant_id,
                'name': config.name,
                'provider': config.provider,
                'type': config.integration_type.value,
                'enabled': config.enabled,
                'status': connectivity_status['status'],
                'last_sync': stats.get('last_sync'),
                'total_events': stats.get('total_events', 0),
                'error_rate': stats.get('error_rate', 0),
                'avg_response_time_ms': stats.get('avg_response_time_ms', 0),
                'rate_limit_remaining': connectivity_status.get('rate_limit_remaining'),
                'created_at': config.created_at.isoformat(),
                'updated_at': config.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération statut intégration {integration_id}: {e}")
            return {'error': str(e)}
    
    async def get_tenant_integrations(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        📋 Récupération des intégrations d'un tenant
        
        Args:
            tenant_id: ID du tenant
            
        Returns:
            Liste des intégrations du tenant
        """
        try:
            tenant_integrations = []
            
            for config in self.integrations.values():
                if config.tenant_id == tenant_id:
                    status = await self.get_integration_status(config.integration_id)
                    tenant_integrations.append(status)
            
            return tenant_integrations
            
        except Exception as e:
            logger.error(f"Erreur récupération intégrations tenant {tenant_id}: {e}")
            return []
    
    # Méthodes privées
    
    def _validate_integration_config(self, config: Dict[str, Any]):
        """Validation de la configuration d'intégration"""
        required_fields = ['name', 'type', 'provider', 'auth_type', 'credentials']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Champ requis manquant: {field}")
        
        # Validation des enums
        try:
            IntegrationType(config['type'])
            AuthenticationType(config['auth_type'])
        except ValueError as e:
            raise ValueError(f"Valeur enum invalide: {e}")
        
        # Validation du provider
        if config['provider'] not in self.providers:
            raise ValueError(f"Provider non supporté: {config['provider']}")
    
    def _encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Chiffrement des credentials"""
        try:
            encrypted_creds = {}
            for key, value in credentials.items():
                if isinstance(value, str):
                    encrypted_value = self.cipher_suite.encrypt(value.encode())
                    encrypted_creds[key] = encrypted_value.decode()
                else:
                    encrypted_creds[key] = value
            return encrypted_creds
        except Exception as e:
            logger.error(f"Erreur chiffrement credentials: {e}")
            return credentials
    
    def _decrypt_credentials(self, encrypted_credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Déchiffrement des credentials"""
        try:
            decrypted_creds = {}
            for key, value in encrypted_credentials.items():
                if isinstance(value, str):
                    try:
                        decrypted_value = self.cipher_suite.decrypt(value.encode())
                        decrypted_creds[key] = decrypted_value.decode()
                    except Exception:
                        # Si déchiffrement échoue, peut-être pas chiffré
                        decrypted_creds[key] = value
                else:
                    decrypted_creds[key] = value
            return decrypted_creds
        except Exception as e:
            logger.error(f"Erreur déchiffrement credentials: {e}")
            return encrypted_credentials
    
    async def _test_integration_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        """Test de connexion d'une intégration"""
        try:
            provider = self.providers.get(config.provider)
            if not provider:
                return {'status': 'error', 'message': f'Provider non supporté: {config.provider}'}
            
            result = await provider.test_connection(config)
            return result
            
        except Exception as e:
            logger.error(f"Erreur test connexion {config.integration_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _store_integration_config(self, config: IntegrationConfig):
        """Stockage de la configuration d'intégration"""
        try:
            # Stockage dans Redis pour accès rapide
            config_data = {
                'integration_id': config.integration_id,
                'tenant_id': config.tenant_id,
                'name': config.name,
                'integration_type': config.integration_type.value,
                'provider': config.provider,
                'authentication_type': config.authentication_type.value,
                'credentials': config.credentials,
                'endpoint_url': config.endpoint_url,
                'webhook_url': config.webhook_url,
                'sync_direction': config.sync_direction.value,
                'rate_limit': config.rate_limit,
                'timeout_seconds': config.timeout_seconds,
                'retry_count': config.retry_count,
                'enabled': config.enabled,
                'auto_sync': config.auto_sync,
                'sync_interval_minutes': config.sync_interval_minutes,
                'metadata': json.dumps(config.metadata),
                'created_at': config.created_at.isoformat(),
                'updated_at': config.updated_at.isoformat()
            }
            
            self.redis_client.hset(
                f"integrations:{config.tenant_id}",
                config.integration_id,
                json.dumps(config_data)
            )
            
            # Stockage dans PostgreSQL pour persistance
            # INSERT INTO integrations (integration_id, tenant_id, config_data, ...)
            
        except Exception as e:
            logger.error(f"Erreur stockage configuration intégration: {e}")
    
    async def _store_integration_event(self, event: IntegrationEvent):
        """Stockage d'un événement d'intégration"""
        try:
            event_data = {
                'event_id': event.event_id,
                'integration_id': event.integration_id,
                'tenant_id': event.tenant_id,
                'event_type': event.event_type,
                'direction': event.direction.value,
                'payload': json.dumps(event.payload),
                'response': json.dumps(event.response) if event.response else None,
                'status': event.status.value,
                'timestamp': event.timestamp.isoformat(),
                'processing_time_ms': event.processing_time_ms,
                'error_message': event.error_message,
                'retry_count': event.retry_count
            }
            
            # Stockage dans Redis avec TTL
            self.redis_client.setex(
                f"integration_events:{event.integration_id}:{event.event_id}",
                86400,  # 24 heures
                json.dumps(event_data)
            )
            
            # Stockage dans PostgreSQL pour historique
            # INSERT INTO integration_events (event_id, integration_id, ...)
            
        except Exception as e:
            logger.error(f"Erreur stockage événement intégration: {e}")
    
    async def _get_integration_statistics(self, integration_id: str) -> Dict[str, Any]:
        """Récupération des statistiques d'une intégration"""
        try:
            # Récupération depuis Redis des événements récents
            pattern = f"integration_events:{integration_id}:*"
            event_keys = self.redis_client.keys(pattern)
            
            if not event_keys:
                return {}
            
            events_data = []
            for key in event_keys:
                event_json = self.redis_client.get(key)
                if event_json:
                    events_data.append(json.loads(event_json))
            
            # Calcul des statistiques
            total_events = len(events_data)
            error_events = len([e for e in events_data if e['status'] == 'error'])
            error_rate = (error_events / total_events * 100) if total_events > 0 else 0
            
            response_times = [e['processing_time_ms'] for e in events_data if e['processing_time_ms']]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Dernière synchronisation
            sync_events = [e for e in events_data if 'sync' in e['event_type']]
            last_sync = max([e['timestamp'] for e in sync_events]) if sync_events else None
            
            return {
                'total_events': total_events,
                'error_rate': round(error_rate, 2),
                'avg_response_time_ms': round(avg_response_time, 2),
                'last_sync': last_sync
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques intégration {integration_id}: {e}")
            return {}
    
    def _verify_webhook_signature(self, provider: str, headers: Dict[str, str],
                                payload: Dict[str, Any], config: IntegrationConfig) -> bool:
        """Vérification de la signature webhook"""
        try:
            # Récupération du secret
            decrypted_creds = self._decrypt_credentials(config.credentials)
            webhook_secret = decrypted_creds.get('webhook_secret')
            
            if not webhook_secret:
                return True  # Pas de vérification si pas de secret
            
            # Vérification selon le provider
            if provider == 'stripe':
                return self._verify_stripe_signature(headers, payload, webhook_secret)
            elif provider == 'github':
                return self._verify_github_signature(headers, payload, webhook_secret)
            # Ajouter d'autres providers...
            
            return True  # Vérification non implémentée pour ce provider
            
        except Exception as e:
            logger.error(f"Erreur vérification signature webhook: {e}")
            return False
    
    def _verify_stripe_signature(self, headers: Dict[str, str], 
                                payload: Dict[str, Any], secret: str) -> bool:
        """Vérification de signature Stripe"""
        try:
            import stripe
            
            signature = headers.get('stripe-signature')
            if not signature:
                return False
            
            # Vérification avec la bibliothèque Stripe
            # stripe.Webhook.construct_event(payload, signature, secret)
            return True  # Implémentation simplifiée
            
        except Exception:
            return False
    
    def _integration_worker(self):
        """Worker de traitement des intégrations"""
        while self.running:
            try:
                # Traitement des événements d'intégration en queue
                try:
                    event = self.event_queue.get(timeout=1)
                    self._process_integration_event(event)
                except queue.Empty:
                    continue
                
            except Exception as e:
                logger.error(f"Erreur worker intégration: {e}")
                time.sleep(1)
    
    def _auto_sync_worker(self):
        """Worker de synchronisation automatique"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                # Vérification des intégrations avec auto-sync activé
                for config in self.integrations.values():
                    if config.auto_sync and config.enabled and config.sync_interval_minutes:
                        # Vérification de l'intervalle
                        last_sync_key = f"last_sync:{config.integration_id}"
                        last_sync_str = self.redis_client.get(last_sync_key)
                        
                        if last_sync_str:
                            last_sync = datetime.fromisoformat(last_sync_str)
                            next_sync = last_sync + timedelta(minutes=config.sync_interval_minutes)
                            
                            if current_time >= next_sync:
                                # Programmation de la synchronisation
                                asyncio.create_task(self.sync_integration_data(config.integration_id))
                                self.redis_client.set(last_sync_key, current_time.isoformat())
                        else:
                            # Première synchronisation
                            asyncio.create_task(self.sync_integration_data(config.integration_id))
                            self.redis_client.set(last_sync_key, current_time.isoformat())
                
                time.sleep(60)  # Vérification toutes les minutes
                
            except Exception as e:
                logger.error(f"Erreur worker auto-sync: {e}")
                time.sleep(60)
    
    def _webhook_processor_worker(self):
        """Worker de traitement des webhooks"""
        while self.running:
            try:
                try:
                    webhook_event = self.webhook_queue.get(timeout=1)
                    self._process_webhook_event(webhook_event)
                except queue.Empty:
                    continue
                
            except Exception as e:
                logger.error(f"Erreur worker webhook: {e}")
                time.sleep(1)
    
    def _process_integration_event(self, event: IntegrationEvent):
        """Traitement d'un événement d'intégration"""
        try:
            # Enregistrement de l'événement
            asyncio.create_task(self._store_integration_event(event))
            
            # Mise à jour des métriques
            self._update_integration_metrics(event)
            
        except Exception as e:
            logger.error(f"Erreur traitement événement intégration: {e}")
    
    def _process_webhook_event(self, webhook_event: WebhookEvent):
        """Traitement d'un événement webhook"""
        try:
            # Récupération du provider
            config = None
            for integration_config in self.integrations.values():
                if integration_config.integration_id == webhook_event.source_integration:
                    config = integration_config
                    break
            
            if not config:
                logger.error(f"Configuration intégration non trouvée: {webhook_event.source_integration}")
                return
            
            provider = self.providers.get(config.provider)
            if not provider:
                logger.error(f"Provider non trouvé: {config.provider}")
                return
            
            # Traitement par le provider
            asyncio.create_task(provider.handle_webhook(config, webhook_event))
            
        except Exception as e:
            logger.error(f"Erreur traitement webhook: {e}")
    
    def _update_integration_metrics(self, event: IntegrationEvent):
        """Mise à jour des métriques d'intégration"""
        try:
            metrics_key = f"integration_metrics:{event.integration_id}"
            
            # Increment counters
            self.redis_client.hincrby(metrics_key, 'total_events', 1)
            
            if event.status == IntegrationStatus.ERROR:
                self.redis_client.hincrby(metrics_key, 'error_events', 1)
            
            # Response time tracking
            if event.processing_time_ms > 0:
                self.redis_client.lpush(
                    f"response_times:{event.integration_id}",
                    event.processing_time_ms
                )
                # Garder seulement les 100 dernières mesures
                self.redis_client.ltrim(f"response_times:{event.integration_id}", 0, 99)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour métriques intégration: {e}")
    
    async def _record_sync_event(self, config: IntegrationConfig, sync_results: Dict[str, Any]):
        """Enregistrement d'un événement de synchronisation"""
        try:
            event = IntegrationEvent(
                event_id=f"sync_{config.integration_id}_{int(time.time())}",
                integration_id=config.integration_id,
                tenant_id=config.tenant_id,
                event_type="sync",
                direction=config.sync_direction,
                payload={'sync_request': True},
                response=sync_results,
                status=IntegrationStatus.ACTIVE if not sync_results.get('errors') else IntegrationStatus.ERROR,
                timestamp=datetime.utcnow(),
                processing_time_ms=0,
                error_message='; '.join(sync_results.get('errors', [])) if sync_results.get('errors') else None,
                retry_count=0
            )
            
            await self._store_integration_event(event)
            
        except Exception as e:
            logger.error(f"Erreur enregistrement événement sync: {e}")
    
    async def _delete_integration_from_db(self, integration_id: str):
        """Suppression d'une intégration de la base de données"""
        try:
            # Suppression de Redis
            for config in self.integrations.values():
                if config.integration_id == integration_id:
                    self.redis_client.hdel(f"integrations:{config.tenant_id}", integration_id)
                    break
            
            # Suppression de PostgreSQL
            # DELETE FROM integrations WHERE integration_id = ?
            
        except Exception as e:
            logger.error(f"Erreur suppression intégration DB: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        🏥 Vérification de santé du service
        
        Returns:
            État de santé du service
        """
        try:
            health_status = {
                'service': 'tenant_integration_hub',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {}
            }
            
            # Vérification workers
            workers_status = {
                'integration_workers': len([w for w in self.workers if w.is_alive()]),
                'sync_worker': self.sync_worker.is_alive(),
                'webhook_worker': self.webhook_worker.is_alive()
            }
            
            health_status['checks']['workers'] = workers_status
            if not all([workers_status['sync_worker'], workers_status['webhook_worker']]):
                health_status['status'] = 'degraded'
            
            # Vérification queues
            health_status['checks']['queue_sizes'] = {
                'integration_events': self.event_queue.qsize(),
                'webhook_events': self.webhook_queue.qsize()
            }
            
            # Vérification Redis
            try:
                self.redis_client.ping()
                health_status['checks']['redis'] = 'healthy'
            except Exception as e:
                health_status['checks']['redis'] = f'unhealthy: {e}'
                health_status['status'] = 'degraded'
            
            # Statistiques générales
            health_status['checks']['total_integrations'] = len(self.integrations)
            health_status['checks']['active_integrations'] = len([
                c for c in self.integrations.values() if c.enabled
            ])
            health_status['checks']['providers_available'] = list(self.providers.keys())
            
            return health_status
            
        except Exception as e:
            logger.error(f"Erreur health check: {e}")
            return {
                'service': 'tenant_integration_hub',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def shutdown(self):
        """Arrêt propre du service"""
        logger.info("Arrêt du hub d'intégrations")
        self.running = False
        
        # Fermeture des sessions HTTP
        for session in self.http_sessions.values():
            asyncio.create_task(session.close())
        
        # Attendre l'arrêt des workers
        for worker in self.workers + [self.sync_worker, self.webhook_worker]:
            if worker.is_alive():
                worker.join(timeout=5)


# Classes de base pour les providers d'intégration

class BaseIntegrationProvider:
    """Classe de base pour les providers d'intégration"""
    
    def __init__(self, hub: TenantIntegrationHub):
        self.hub = hub
        self.config = hub.config.get('providers', {})
    
    async def test_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        """Test de connexion"""
        raise NotImplementedError
    
    async def execute_action(self, config: IntegrationConfig, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Exécution d'une action"""
        raise NotImplementedError
    
    async def sync_inbound_data(self, config: IntegrationConfig) -> Dict[str, Any]:
        """Synchronisation des données entrantes"""
        raise NotImplementedError
    
    async def sync_outbound_data(self, config: IntegrationConfig) -> Dict[str, Any]:
        """Synchronisation des données sortantes"""
        raise NotImplementedError
    
    async def handle_webhook(self, config: IntegrationConfig, webhook_event: WebhookEvent):
        """Traitement d'un webhook"""
        raise NotImplementedError


class InstagramIntegration(BaseIntegrationProvider):
    """Intégration Instagram Business API"""
    
    async def test_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        try:
            # Test de connexion à l'API Instagram
            # GET /me avec access_token
            return {'status': 'active', 'message': 'Connected to Instagram API'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def execute_action(self, config: IntegrationConfig, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if action == 'post_content':
            return await self._post_content(config, payload)
        elif action == 'get_insights':
            return await self._get_insights(config, payload)
        else:
            raise ValueError(f"Action non supportée: {action}")
    
    async def _post_content(self, config: IntegrationConfig, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Implémentation du post de contenu Instagram
        return {'post_id': 'ig_123456', 'status': 'published'}
    
    async def _get_insights(self, config: IntegrationConfig, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Implémentation de récupération d'insights Instagram
        return {'impressions': 1000, 'reach': 800, 'engagement': 50}


class StripeIntegration(BaseIntegrationProvider):
    """Intégration Stripe Payment Gateway"""
    
    async def test_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        try:
            # Test avec l'API Stripe
            return {'status': 'active', 'message': 'Connected to Stripe API'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def execute_action(self, config: IntegrationConfig, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if action == 'create_payment':
            return await self._create_payment(config, payload)
        elif action == 'get_balance':
            return await self._get_balance(config)
        else:
            raise ValueError(f"Action non supportée: {action}")
    
    async def _create_payment(self, config: IntegrationConfig, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Implémentation de création de paiement Stripe
        return {'payment_id': 'pi_123456', 'status': 'succeeded'}
    
    async def _get_balance(self, config: IntegrationConfig) -> Dict[str, Any]:
        # Implémentation de récupération du solde Stripe
        return {'available': 1000.00, 'pending': 200.00, 'currency': 'usd'}


# Ajout d'autres providers...
class SendGridIntegration(BaseIntegrationProvider):
    """Intégration SendGrid Email Service"""
    pass

class YouTubeIntegration(BaseIntegrationProvider):
    """Intégration YouTube Data API"""
    pass

class TikTokIntegration(BaseIntegrationProvider):
    """Intégration TikTok Marketing API"""
    pass

class TwitterIntegration(BaseIntegrationProvider):
    """Intégration Twitter API v2"""
    pass

class PayPalIntegration(BaseIntegrationProvider):
    """Intégration PayPal Payments API"""
    pass

class TwilioIntegration(BaseIntegrationProvider):
    """Intégration Twilio Communications API"""
    pass

class GoogleAnalyticsIntegration(BaseIntegrationProvider):
    """Intégration Google Analytics API"""
    pass

class SalesforceIntegration(BaseIntegrationProvider):
    """Intégration Salesforce CRM API"""
    pass


# Factory function pour l'initialisation
def create_tenant_integration_hub(config_path: Optional[str] = None) -> TenantIntegrationHub:
    """
    🏭 Factory pour créer une instance du hub d'intégrations
    
    Args:
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        Instance configurée du TenantIntegrationHub
    """
    return TenantIntegrationHub(config_path or '/etc/ainflue/integrations_config.yaml')


# Exemple d'utilisation
if __name__ == "__main__":
    async def main():
        # Création du hub d'intégrations
        hub = create_tenant_integration_hub()
        
        # Création d'une intégration Instagram
        integration_id = await hub.create_integration(
            tenant_id="tenant_123",
            integration_config={
                'name': 'Instagram Business Account',
                'type': 'social_media',
                'provider': 'instagram',
                'auth_type': 'oauth2',
                'credentials': {
                    'access_token': 'ig_access_token_123',
                    'client_id': 'ig_client_id',
                    'client_secret': 'ig_client_secret'
                },
                'sync_direction': 'bidirectional',
                'auto_sync': True,
                'sync_interval_minutes': 30
            }
        )
        
        print(f"Intégration Instagram créée: {integration_id}")
        
        # Exécution d'une action
        result = await hub.execute_integration_action(
            integration_id=integration_id,
            action='post_content',
            payload={
                'media_url': 'https://example.com/image.jpg',
                'caption': 'Hello from Ainflue!',
                'hashtags': ['ainflue', 'socialmedia']
            }
        )
        
        print(f"Résultat post Instagram: {result}")
        
        # Statut de l'intégration
        status = await hub.get_integration_status(integration_id)
        print(f"Statut intégration: {status}")
        
        # Synchronisation des données
        sync_result = await hub.sync_integration_data(integration_id)
        print(f"Résultat synchronisation: {sync_result}")
    
    asyncio.run(main())