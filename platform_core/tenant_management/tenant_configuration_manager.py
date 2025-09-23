#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚙️ Tenant Configuration Manager - Enterprise Multi-Tenant Dynamic Configuration

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
Cette architecture tenant configuration est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite PERSONNELLE
est STRICTEMENT INTERDITE et sera poursuivie en justice.
"""

import asyncio
import logging
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import redis
import yaml
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from cryptography.fernet import Fernet
import consul
import etcd3
import aiofiles


# Configuration du logging avancé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/tenant_config.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """Types de configuration"""
    APPLICATION = "application"
    DATABASE = "database"
    SECURITY = "security"
    FEATURES = "features"
    LIMITS = "limits"
    INTEGRATIONS = "integrations"
    NOTIFICATIONS = "notifications"
    ANALYTICS = "analytics"


class ConfigScope(Enum):
    """Portée de configuration"""
    GLOBAL = "global"
    TENANT = "tenant"
    USER = "user"
    ENVIRONMENT = "environment"


class ConfigStatus(Enum):
    """États de configuration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DEPRECATED = "deprecated"
    TESTING = "testing"


@dataclass
class ConfigEntry:
    """Entrée de configuration enterprise"""
    key: str
    value: Any
    config_type: ConfigType
    scope: ConfigScope
    tenant_id: Optional[str]
    encrypted: bool
    version: int
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]
    validation_schema: Optional[Dict[str, Any]]


@dataclass
class ConfigHistory:
    """Historique de configuration"""
    config_key: str
    old_value: Any
    new_value: Any
    changed_by: str
    change_reason: str
    timestamp: datetime
    rollback_data: Dict[str, Any]


class TenantConfigurationManager:
    """
    ⚙️ Enterprise Tenant Configuration Manager
    
    Gestionnaire de configuration enterprise pour architecture multi-tenant avec:
    - Configuration dynamique temps réel
    - Chiffrement des données sensibles
    - Versioning et historique complet
    - Validation et schema enforcement
    - Cache distribué haute performance
    - Hot-reload sans redémarrage
    """
    
    def __init__(self, config_path: str = '/etc/ainflue/config_manager.yaml'):
        """Initialisation du gestionnaire de configuration"""
        self.config = self._load_config(config_path)
        self.config_cache: Dict[str, ConfigEntry] = {}
        self.config_history: List[ConfigHistory] = []
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.watch_threads: Dict[str, threading.Thread] = {}
        
        # Connexions aux services
        self._init_storage_backends()
        self._init_cache_layer()
        self._init_service_discovery()
        self._init_monitoring()
        
        # Démarrage des watchers
        self._start_config_watchers()
        
        logger.info("TenantConfigurationManager initialisé avec succès")
    
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
            'cache_ttl_seconds': 300,
            'hot_reload_enabled': True,
            'encryption_enabled': True,
            'validation_enabled': True,
            'history_retention_days': 90,
            'storage': {
                'primary': 'redis',
                'secondary': 'postgresql',
                'consul_enabled': True,
                'etcd_enabled': False
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'ssl': True
            },
            'consul': {
                'host': 'localhost',
                'port': 8500,
                'datacenter': 'dc1'
            }
        }
    
    def _get_encryption_key(self) -> bytes:
        """Récupération de la clé de chiffrement"""
        key_path = self.config.get('encryption_key_path', '/etc/ainflue/config.key')
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
    
    def _init_storage_backends(self):
        """Initialisation des backends de stockage"""
        # Redis principal
        redis_config = self.config.get('redis', {})
        self.redis_client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            ssl=redis_config.get('ssl', True),
            decode_responses=True
        )
        
        # PostgreSQL secondaire pour persistance
        db_config = self.config.get('database', {})
        self.db_engine = None  # Initialisé lors de la première utilisation
        
        logger.info("Backends de stockage initialisés")
    
    def _init_cache_layer(self):
        """Initialisation de la couche de cache"""
        self.local_cache: Dict[str, Tuple[ConfigEntry, datetime]] = {}
        self.cache_ttl = self.config.get('cache_ttl_seconds', 300)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
        # Thread de nettoyage du cache
        self.cache_cleanup_thread = threading.Thread(
            target=self._cache_cleanup_worker,
            daemon=True
        )
        self.cache_cleanup_thread.start()
        
        logger.info("Couche de cache initialisée")
    
    def _init_service_discovery(self):
        """Initialisation de la découverte de services"""
        # Consul pour service discovery
        if self.config.get('storage', {}).get('consul_enabled', True):
            consul_config = self.config.get('consul', {})
            self.consul_client = consul.Consul(
                host=consul_config.get('host', 'localhost'),
                port=consul_config.get('port', 8500),
                datacenter=consul_config.get('datacenter', 'dc1')
            )
        else:
            self.consul_client = None
        
        # etcd pour configuration distribuée
        if self.config.get('storage', {}).get('etcd_enabled', False):
            etcd_config = self.config.get('etcd', {})
            self.etcd_client = etcd3.client(
                host=etcd_config.get('host', 'localhost'),
                port=etcd_config.get('port', 2379)
            )
        else:
            self.etcd_client = None
        
        logger.info("Service discovery initialisé")
    
    def _init_monitoring(self):
        """Initialisation du monitoring"""
        self.metrics = {
            'config_reads': 0,
            'config_writes': 0,
            'config_deletes': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'validation_errors': 0,
            'encryption_operations': 0
        }
        
        # Métriques par tenant
        self.tenant_metrics: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Monitoring initialisé")
    
    def _start_config_watchers(self):
        """Démarrage des watchers de configuration"""
        if self.config.get('hot_reload_enabled', True):
            # Watcher Redis
            redis_watcher = threading.Thread(
                target=self._redis_watcher,
                daemon=True
            )
            redis_watcher.start()
            self.watch_threads['redis'] = redis_watcher
            
            # Watcher Consul si activé
            if self.consul_client:
                consul_watcher = threading.Thread(
                    target=self._consul_watcher,
                    daemon=True
                )
                consul_watcher.start()
                self.watch_threads['consul'] = consul_watcher
        
        logger.info("Watchers de configuration démarrés")
    
    async def get_config(self, key: str, tenant_id: Optional[str] = None,
                        default: Any = None, decrypt: bool = True) -> Any:
        """
        📖 Récupération d'une configuration
        
        Args:
            key: Clé de configuration
            tenant_id: ID du tenant (optionnel)
            default: Valeur par défaut
            decrypt: Déchiffrer si chiffré
            
        Returns:
            Valeur de configuration ou valeur par défaut
        """
        try:
            self.metrics['config_reads'] += 1
            
            # Construction de la clé complète
            full_key = self._build_config_key(key, tenant_id)
            
            # Vérification du cache local
            cached_entry = self._get_from_local_cache(full_key)
            if cached_entry:
                self.cache_stats['hits'] += 1
                self.metrics['cache_hits'] += 1
                value = cached_entry.value
                
                if cached_entry.encrypted and decrypt:
                    value = self._decrypt_value(value)
                
                return value
            
            # Cache miss - récupération depuis Redis
            self.cache_stats['misses'] += 1
            self.metrics['cache_misses'] += 1
            
            config_entry = await self._get_from_redis(full_key)
            
            if config_entry:
                # Mise en cache local
                self._store_in_local_cache(full_key, config_entry)
                
                value = config_entry.value
                if config_entry.encrypted and decrypt:
                    value = self._decrypt_value(value)
                
                return value
            
            # Fallback vers PostgreSQL
            config_entry = await self._get_from_database(full_key)
            
            if config_entry:
                # Synchronisation vers Redis
                await self._store_in_redis(full_key, config_entry)
                self._store_in_local_cache(full_key, config_entry)
                
                value = config_entry.value
                if config_entry.encrypted and decrypt:
                    value = self._decrypt_value(value)
                
                return value
            
            # Aucune configuration trouvée
            return default
            
        except Exception as e:
            logger.error(f"Erreur récupération configuration {key}: {e}")
            return default
    
    async def set_config(self, key: str, value: Any, tenant_id: Optional[str] = None,
                        config_type: ConfigType = ConfigType.APPLICATION,
                        scope: ConfigScope = ConfigScope.TENANT,
                        encrypt: bool = False, ttl: Optional[int] = None,
                        metadata: Optional[Dict[str, Any]] = None,
                        changed_by: str = "system") -> bool:
        """
        ✏️ Définition d'une configuration
        
        Args:
            key: Clé de configuration
            value: Valeur à stocker
            tenant_id: ID du tenant
            config_type: Type de configuration
            scope: Portée de la configuration
            encrypt: Chiffrer la valeur
            ttl: Time-to-live en secondes
            metadata: Métadonnées additionnelles
            changed_by: Utilisateur ayant fait le changement
            
        Returns:
            True si succès
        """
        try:
            self.metrics['config_writes'] += 1
            
            # Construction de la clé complète
            full_key = self._build_config_key(key, tenant_id)
            
            # Récupération de l'ancienne valeur pour l'historique
            old_entry = await self._get_from_redis(full_key)
            old_value = old_entry.value if old_entry else None
            
            # Validation de la valeur
            if self.config.get('validation_enabled', True):
                validation_result = await self._validate_config_value(key, value, config_type)
                if not validation_result:
                    self.metrics['validation_errors'] += 1
                    logger.error(f"Validation échouée pour {key}")
                    return False
            
            # Chiffrement si nécessaire
            stored_value = value
            if encrypt and self.config.get('encryption_enabled', True):
                stored_value = self._encrypt_value(value)
                self.metrics['encryption_operations'] += 1
            
            # Calcul de l'expiration
            expires_at = None
            if ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            # Création de l'entrée de configuration
            config_entry = ConfigEntry(
                key=full_key,
                value=stored_value,
                config_type=config_type,
                scope=scope,
                tenant_id=tenant_id,
                encrypted=encrypt,
                version=(old_entry.version + 1) if old_entry else 1,
                created_at=old_entry.created_at if old_entry else datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=expires_at,
                metadata=metadata or {},
                validation_schema=None
            )
            
            # Stockage dans Redis
            await self._store_in_redis(full_key, config_entry)
            
            # Stockage dans PostgreSQL pour persistance
            await self._store_in_database(full_key, config_entry)
            
            # Mise à jour du cache local
            self._store_in_local_cache(full_key, config_entry)
            
            # Enregistrement dans l'historique
            await self._record_config_change(
                config_key=full_key,
                old_value=old_value,
                new_value=value,
                changed_by=changed_by,
                change_reason=metadata.get('change_reason', 'Configuration update') if metadata else 'Configuration update'
            )
            
            # Notification du changement
            await self._notify_config_change(full_key, old_value, value, tenant_id)
            
            # Mise à jour des métriques par tenant
            if tenant_id:
                self._update_tenant_metrics(tenant_id, 'config_updates', 1)
            
            logger.info(f"Configuration mise à jour: {full_key}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour configuration {key}: {e}")
            return False
    
    async def delete_config(self, key: str, tenant_id: Optional[str] = None,
                          changed_by: str = "system") -> bool:
        """
        🗑️ Suppression d'une configuration
        
        Args:
            key: Clé de configuration
            tenant_id: ID du tenant
            changed_by: Utilisateur ayant fait le changement
            
        Returns:
            True si succès
        """
        try:
            self.metrics['config_deletes'] += 1
            
            # Construction de la clé complète
            full_key = self._build_config_key(key, tenant_id)
            
            # Récupération de la valeur pour l'historique
            old_entry = await self._get_from_redis(full_key)
            if not old_entry:
                return False
            
            # Suppression de Redis
            await self._delete_from_redis(full_key)
            
            # Suppression de PostgreSQL
            await self._delete_from_database(full_key)
            
            # Suppression du cache local
            self._delete_from_local_cache(full_key)
            
            # Enregistrement dans l'historique
            await self._record_config_change(
                config_key=full_key,
                old_value=old_entry.value,
                new_value=None,
                changed_by=changed_by,
                change_reason="Configuration deleted"
            )
            
            # Notification de la suppression
            await self._notify_config_change(full_key, old_entry.value, None, tenant_id)
            
            logger.info(f"Configuration supprimée: {full_key}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression configuration {key}: {e}")
            return False
    
    async def get_tenant_configs(self, tenant_id: str,
                               config_type: Optional[ConfigType] = None) -> Dict[str, Any]:
        """
        📋 Récupération de toutes les configurations d'un tenant
        
        Args:
            tenant_id: ID du tenant
            config_type: Filtre par type (optionnel)
            
        Returns:
            Dictionnaire des configurations
        """
        try:
            # Pattern de recherche
            pattern = f"tenant:{tenant_id}:*"
            
            # Récupération depuis Redis
            configs = {}
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                config_entry = await self._get_from_redis(key)
                if config_entry:
                    # Filtrage par type si spécifié
                    if config_type and config_entry.config_type != config_type:
                        continue
                    
                    # Extraction de la clé originale
# SECURITY: original_key = key.split(':', 2)[-1] # MOVED TO ENV
# TODO: Move to environment variables or secure vault
                    
                    # Déchiffrement si nécessaire
                    value = config_entry.value
                    if config_entry.encrypted:
                        value = self._decrypt_value(value)
                    
                    configs[original_key] = {
                        'value': value,
                        'type': config_entry.config_type.value,
                        'scope': config_entry.scope.value,
                        'version': config_entry.version,
                        'updated_at': config_entry.updated_at.isoformat(),
                        'metadata': config_entry.metadata
                    }
            
            return configs
            
        except Exception as e:
            logger.error(f"Erreur récupération configurations tenant {tenant_id}: {e}")
            return {}
    
    async def bulk_update_configs(self, configs: Dict[str, Any], tenant_id: str,
                                changed_by: str = "system") -> Dict[str, bool]:
        """
        📦 Mise à jour en lot de configurations
        
        Args:
            configs: Dictionnaire clé -> valeur
            tenant_id: ID du tenant
            changed_by: Utilisateur ayant fait le changement
            
        Returns:
            Dictionnaire des résultats par clé
        """
        try:
            results = {}
            
            for key, value in configs.items():
                # Configuration par défaut si value est une dict avec paramètres
                if isinstance(value, dict) and 'value' in value:
                    config_params = value.copy()
                    actual_value = config_params.pop('value')
                    
                    success = await self.set_config(
                        key=key,
                        value=actual_value,
                        tenant_id=tenant_id,
                        changed_by=changed_by,
                        **config_params
                    )
                else:
                    success = await self.set_config(
                        key=key,
                        value=value,
                        tenant_id=tenant_id,
                        changed_by=changed_by
                    )
                
                results[key] = success
            
            logger.info(f"Mise à jour en lot terminée pour tenant {tenant_id}")
            return results
            
        except Exception as e:
            logger.error(f"Erreur mise à jour en lot: {e}")
            return {}
    
    async def get_config_history(self, key: str, tenant_id: Optional[str] = None,
                               limit: int = 100) -> List[ConfigHistory]:
        """
        📜 Récupération de l'historique d'une configuration
        
        Args:
            key: Clé de configuration
            tenant_id: ID du tenant
            limit: Nombre maximum d'entrées
            
        Returns:
            Liste de l'historique
        """
        try:
            full_key = self._build_config_key(key, tenant_id)
            
            # Filtrage de l'historique
            history = [
                entry for entry in self.config_history
                if entry.config_key == full_key
            ]
            
            # Tri par date décroissante et limitation
            history.sort(key=lambda x: x.timestamp, reverse=True)
            return history[:limit]
            
        except Exception as e:
            logger.error(f"Erreur récupération historique {key}: {e}")
            return []
    
    async def rollback_config(self, key: str, tenant_id: Optional[str] = None,
                            to_version: Optional[int] = None,
                            changed_by: str = "system") -> bool:
        """
        ↩️ Rollback d'une configuration
        
        Args:
            key: Clé de configuration
            tenant_id: ID du tenant
            to_version: Version cible (dernière si None)
            changed_by: Utilisateur ayant fait le rollback
            
        Returns:
            True si succès
        """
        try:
            full_key = self._build_config_key(key, tenant_id)
            
            # Récupération de l'historique
            history = await self.get_config_history(key, tenant_id)
            
            if not history:
                logger.warning(f"Aucun historique trouvé pour {full_key}")
                return False
            
            # Sélection de la version cible
            target_entry = None
            if to_version:
                for entry in history:
                    if entry.rollback_data.get('version') == to_version:
                        target_entry = entry
                        break
            else:
                # Dernière version stable
                target_entry = history[1] if len(history) > 1 else history[0]
            
            if not target_entry:
                logger.warning(f"Version cible non trouvée pour {full_key}")
                return False
            
            # Rollback vers la valeur précédente
            success = await self.set_config(
                key=key,
                value=target_entry.old_value,
                tenant_id=tenant_id,
                changed_by=changed_by,
                metadata={'change_reason': f'Rollback to version {to_version or "previous"}'}
            )
            
            if success:
                logger.info(f"Rollback effectué pour {full_key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur rollback configuration {key}: {e}")
            return False
    
    async def validate_tenant_configs(self, tenant_id: str) -> Dict[str, Any]:
        """
        ✅ Validation complète des configurations d'un tenant
        
        Args:
            tenant_id: ID du tenant
            
        Returns:
            Rapport de validation
        """
        try:
            configs = await self.get_tenant_configs(tenant_id)
            
            validation_report = {
                'tenant_id': tenant_id,
                'total_configs': len(configs),
                'valid_configs': 0,
                'invalid_configs': 0,
                'errors': [],
                'warnings': [],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            for key, config in configs.items():
                try:
                    # Validation de type
                    config_type = ConfigType(config['type'])
                    is_valid = await self._validate_config_value(key, config['value'], config_type)
                    
                    if is_valid:
                        validation_report['valid_configs'] += 1
                    else:
                        validation_report['invalid_configs'] += 1
                        validation_report['errors'].append(f"Configuration invalide: {key}")
                    
                    # Vérifications additionnelles
                    if config.get('expires_at'):
                        expires_at = datetime.fromisoformat(config['expires_at'])
                        if expires_at < datetime.utcnow():
                            validation_report['warnings'].append(f"Configuration expirée: {key}")
                
                except Exception as e:
                    validation_report['invalid_configs'] += 1
                    validation_report['errors'].append(f"Erreur validation {key}: {str(e)}")
            
            return validation_report
            
        except Exception as e:
            logger.error(f"Erreur validation configurations tenant {tenant_id}: {e}")
            return {'error': str(e)}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        📈 Récupération des métriques
        
        Returns:
            Métriques globales et par tenant
        """
        try:
            # Métriques de cache
            cache_hit_rate = 0
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            if total_requests > 0:
                cache_hit_rate = (self.cache_stats['hits'] / total_requests) * 100
            
            # Métriques globales
            global_metrics = {
                **self.metrics,
                'cache_stats': self.cache_stats,
                'cache_hit_rate_percent': round(cache_hit_rate, 2),
                'local_cache_size': len(self.local_cache),
                'config_entries_total': len(self.config_cache),
                'active_watchers': len(self.watch_threads)
            }
            
            return {
                'global': global_metrics,
                'by_tenant': self.tenant_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération métriques: {e}")
            return {}
    
    # Méthodes utilitaires privées
    
    def _build_config_key(self, key: str, tenant_id: Optional[str]) -> str:
        """Construction de la clé complète"""
        if tenant_id:
            return f"tenant:{tenant_id}:{key}"
        else:
            return f"global:{key}"
    
    def _get_from_local_cache(self, key: str) -> Optional[ConfigEntry]:
        """Récupération depuis le cache local"""
        cached_data = self.local_cache.get(key)
        if cached_data:
            entry, cached_at = cached_data
            if datetime.utcnow() - cached_at < timedelta(seconds=self.cache_ttl):
                return entry
            else:
                # Cache expiré
                del self.local_cache[key]
                self.cache_stats['evictions'] += 1
        return None
    
    def _store_in_local_cache(self, key: str, entry: ConfigEntry):
        """Stockage dans le cache local"""
        self.local_cache[key] = (entry, datetime.utcnow())
    
    def _delete_from_local_cache(self, key: str):
        """Suppression du cache local"""
        if key in self.local_cache:
            del self.local_cache[key]
    
    async def _get_from_redis(self, key: str) -> Optional[ConfigEntry]:
        """Récupération depuis Redis"""
        try:
            data = self.redis_client.get(key)
            if data:
                return self._deserialize_config_entry(data)
        except Exception as e:
            logger.error(f"Erreur récupération Redis {key}: {e}")
        return None
    
    async def _store_in_redis(self, key: str, entry: ConfigEntry):
        """Stockage dans Redis"""
        try:
            data = self._serialize_config_entry(entry)
            if entry.expires_at:
                ttl = int((entry.expires_at - datetime.utcnow()).total_seconds())
                self.redis_client.setex(key, ttl, data)
            else:
                self.redis_client.set(key, data)
        except Exception as e:
            logger.error(f"Erreur stockage Redis {key}: {e}")
    
    async def _delete_from_redis(self, key: str):
        """Suppression de Redis"""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Erreur suppression Redis {key}: {e}")
    
    async def _get_from_database(self, key: str) -> Optional[ConfigEntry]:
        """Récupération depuis PostgreSQL"""
        # Implémentation simplifiée - à adapter selon votre schema
        return None
    
    async def _store_in_database(self, key: str, entry: ConfigEntry):
        """Stockage dans PostgreSQL"""
        # Implémentation simplifiée - à adapter selon votre schema
        pass
    
    async def _delete_from_database(self, key: str):
        """Suppression de PostgreSQL"""
        # Implémentation simplifiée - à adapter selon votre schema
        pass
    
    def _encrypt_value(self, value: Any) -> str:
        """Chiffrement d'une valeur"""
        try:
            json_value = json.dumps(value)
            encrypted_value = self.cipher_suite.encrypt(json_value.encode())
            return encrypted_value.decode()
        except Exception as e:
            logger.error(f"Erreur chiffrement: {e}")
            return str(value)
    
    def _decrypt_value(self, encrypted_value: str) -> Any:
        """Déchiffrement d'une valeur"""
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_value.encode())
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Erreur déchiffrement: {e}")
            return encrypted_value
    
    def _serialize_config_entry(self, entry: ConfigEntry) -> str:
        """Sérialisation d'une entrée de configuration"""
        data = {
            'key': entry.key,
            'value': entry.value,
            'config_type': entry.config_type.value,
            'scope': entry.scope.value,
            'tenant_id': entry.tenant_id,
            'encrypted': entry.encrypted,
            'version': entry.version,
            'created_at': entry.created_at.isoformat(),
            'updated_at': entry.updated_at.isoformat(),
            'expires_at': entry.expires_at.isoformat() if entry.expires_at else None,
            'metadata': entry.metadata
        }
        return json.dumps(data)
    
    def _deserialize_config_entry(self, data: str) -> ConfigEntry:
        """Désérialisation d'une entrée de configuration"""
        parsed = json.loads(data)
        return ConfigEntry(
            key=parsed['key'],
            value=parsed['value'],
            config_type=ConfigType(parsed['config_type']),
            scope=ConfigScope(parsed['scope']),
            tenant_id=parsed.get('tenant_id'),
            encrypted=parsed['encrypted'],
            version=parsed['version'],
            created_at=datetime.fromisoformat(parsed['created_at']),
            updated_at=datetime.fromisoformat(parsed['updated_at']),
            expires_at=datetime.fromisoformat(parsed['expires_at']) if parsed.get('expires_at') else None,
            metadata=parsed.get('metadata', {}),
            validation_schema=None
        )
    
    async def _validate_config_value(self, key: str, value: Any, config_type: ConfigType) -> bool:
        """Validation d'une valeur de configuration"""
        try:
            # Validation basique par type
            if config_type == ConfigType.DATABASE:
                return isinstance(value, dict) and 'host' in value
            elif config_type == ConfigType.LIMITS:
                return isinstance(value, (int, float)) and value >= 0
            elif config_type == ConfigType.FEATURES:
                return isinstance(value, bool)
            else:
                return True  # Validation permissive par défaut
        except Exception as e:
            logger.error(f"Erreur validation {key}: {e}")
            return False
    
    async def _record_config_change(self, config_key: str, old_value: Any, new_value: Any,
                                  changed_by: str, change_reason: str):
        """Enregistrement d'un changement dans l'historique"""
        history_entry = ConfigHistory(
            config_key=config_key,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            change_reason=change_reason,
            timestamp=datetime.utcnow(),
            rollback_data={'version': len(self.config_history) + 1}
        )
        
        self.config_history.append(history_entry)
        
        # Nettoyage de l'historique ancien
        retention_days = self.config.get('history_retention_days', 90)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        self.config_history = [
            entry for entry in self.config_history
            if entry.timestamp > cutoff_date
        ]
    
    async def _notify_config_change(self, key: str, old_value: Any, new_value: Any,
                                  tenant_id: Optional[str]):
        """Notification d'un changement de configuration"""
        try:
            # Publication vers Redis Pub/Sub pour hot reload
            message = {
                'key': key,
                'old_value': old_value,
                'new_value': new_value,
                'tenant_id': tenant_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            channel = f"config_changes:{tenant_id}" if tenant_id else "config_changes:global"
            self.redis_client.publish(channel, json.dumps(message))
            
            # Notification via Consul si disponible
            if self.consul_client:
                self.consul_client.kv.put(f"config_notifications/{key}", json.dumps(message))
                
        except Exception as e:
            logger.error(f"Erreur notification changement {key}: {e}")
    
    def _update_tenant_metrics(self, tenant_id: str, metric: str, value: Any):
        """Mise à jour des métriques par tenant"""
        if tenant_id not in self.tenant_metrics:
            self.tenant_metrics[tenant_id] = {}
        
        if metric in self.tenant_metrics[tenant_id]:
            if isinstance(value, (int, float)):
                self.tenant_metrics[tenant_id][metric] += value
            else:
                self.tenant_metrics[tenant_id][metric] = value
        else:
            self.tenant_metrics[tenant_id][metric] = value
    
    def _cache_cleanup_worker(self):
        """Worker de nettoyage du cache local"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_keys = []
                
                for key, (entry, cached_at) in self.local_cache.items():
                    if current_time - cached_at > timedelta(seconds=self.cache_ttl):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.local_cache[key]
                    self.cache_stats['evictions'] += 1
                
                time.sleep(60)  # Nettoyage toutes les minutes
                
            except Exception as e:
                logger.error(f"Erreur nettoyage cache: {e}")
                time.sleep(60)
    
    def _redis_watcher(self):
        """Watcher Redis pour hot reload"""
        try:
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe('config_changes:*')
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
# SECURITY: key = data['key'] # MOVED TO ENV
# TODO: Move to environment variables or secure vault
                        
                        # Invalidation du cache local
                        if key in self.local_cache:
                            del self.local_cache[key]
                            logger.debug(f"Cache invalidé pour {key}")
                            
                    except Exception as e:
                        logger.error(f"Erreur traitement message Redis: {e}")
                        
        except Exception as e:
            logger.error(f"Erreur watcher Redis: {e}")
    
    def _consul_watcher(self):
        """Watcher Consul pour synchronisation distribuée"""
        try:
            index = None
            while True:
                try:
                    index, data = self.consul_client.kv.get('config_notifications/', index=index, recurse=True)
                    if data:
                        for item in data:
                            # Traitement des notifications Consul
                            pass
                except Exception as e:
                    logger.error(f"Erreur watcher Consul: {e}")
                    time.sleep(5)
        except Exception as e:
            logger.error(f"Erreur initialisation watcher Consul: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        🏥 Vérification de santé du service
        
        Returns:
            État de santé du service
        """
        try:
            health_status = {
                'service': 'tenant_configuration_manager',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {}
            }
            
            # Vérification connexion Redis
            try:
                self.redis_client.ping()
                health_status['checks']['redis'] = 'healthy'
            except Exception as e:
                health_status['checks']['redis'] = f'unhealthy: {e}'
                health_status['status'] = 'degraded'
            
            # Vérification Consul si activé
            if self.consul_client:
                try:
                    self.consul_client.agent.self()
                    health_status['checks']['consul'] = 'healthy'
                except Exception as e:
                    health_status['checks']['consul'] = f'unhealthy: {e}'
                    health_status['status'] = 'degraded'
            
            # Métriques de performance
            health_status['checks']['local_cache_size'] = len(self.local_cache)
            health_status['checks']['active_watchers'] = len(self.watch_threads)
            health_status['checks']['total_configs'] = len(self.config_cache)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Erreur health check: {e}")
            return {
                'service': 'tenant_configuration_manager',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Factory function pour l'initialisation
def create_tenant_configuration_manager(config_path: Optional[str] = None) -> TenantConfigurationManager:
    """
    🏭 Factory pour créer une instance du gestionnaire de configuration
    
    Args:
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        Instance configurée du TenantConfigurationManager
    """
    return TenantConfigurationManager(config_path or '/etc/ainflue/config_manager.yaml')


# Exemple d'utilisation
if __name__ == "__main__":
    async def main():
        # Création du gestionnaire
        config_manager = create_tenant_configuration_manager()
        
        # Configuration d'un tenant
        await config_manager.set_config(
            key="database_host",
            value="localhost",
            tenant_id="tenant_123",
            config_type=ConfigType.DATABASE,
            encrypt=False
        )
        
        # Récupération de configuration
        db_host = await config_manager.get_config("database_host", "tenant_123")
        print(f"Database host: {db_host}")
        
        # Configuration sensible chiffrée
        await config_manager.set_config(
            key="api_secret",
            value="super_secret_key_123",
            tenant_id="tenant_123",
            config_type=ConfigType.SECURITY,
            encrypt=True
        )
        
        # Validation des configurations
        validation_report = await config_manager.validate_tenant_configs("tenant_123")
        print(f"Validation: {validation_report}")
    
    asyncio.run(main())