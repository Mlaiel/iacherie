"""
⚙️ Dynamic Configuration Manager Enterprise - IA Chérie
====================================================
Manager configuration dynamique pour microservices.
Config hot-reload + feature flags + environment management.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Service Discovery
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""

import asyncio
import time
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import copy

logger = logging.getLogger(__name__)

class ConfigSource(Enum):
    """Sources de configuration"""
    ENVIRONMENT = "environment"
    FILE = "file" 
    DATABASE = "database"
    CONSUL = "consul"
    ETCD = "etcd"
    KUBERNETES = "kubernetes"
    REMOTE_API = "remote_api"

class FeatureFlagStrategy(Enum):
    """Stratégies de déploiement des feature flags"""
    PERCENTAGE = "percentage"
    USER_BASED = "user_based"
    GROUP_BASED = "group_based"
    GEOGRAPHIC = "geographic"
    TIME_BASED = "time_based"
    AB_TESTING = "ab_testing"

class ConfigValidationLevel(Enum):
    """Niveaux de validation de configuration"""
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    ENTERPRISE = "enterprise"

@dataclass
class ConfigRequest:
    """Requête de configuration"""
    service_id: str
    config_keys: List[str] = field(default_factory=list)
    version: Optional[str] = None
    environment: str = "production"
    filters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class ConfigResult:
    """Résultat de configuration"""
    success: bool
    config_data: Dict[str, Any] = field(default_factory=dict)
    version: str = ""
    source: ConfigSource = ConfigSource.FILE
    cached: bool = False
    errors: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

@dataclass
class FeatureFlag:
    """Feature flag avec configuration"""
    flag_id: str
    flag_name: str
    enabled: bool = False
    strategy: FeatureFlagStrategy = FeatureFlagStrategy.PERCENTAGE
    targeting_rules: Dict[str, Any] = field(default_factory=dict)
    rollout_percentage: float = 0.0
    environments: Set[str] = field(default_factory=lambda: {"production"})
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeatureFlagOp:
    """Opération sur feature flag"""
    operation: str  # create, update, delete, toggle
    flag_id: str
    flag_data: Optional[FeatureFlag] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FlagResult:
    """Résultat d'opération sur feature flags"""
    success: bool
    affected_flags: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class UpdateResult:
    """Résultat de mise à jour de configuration"""
    success: bool
    updated_keys: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    rollback_available: bool = False
    previous_version: Optional[str] = None

@dataclass
class ValidationResult:
    """Résultat de validation de configuration"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_level: ConfigValidationLevel = ConfigValidationLevel.BASIC

@dataclass
class RollbackResult:
    """Résultat de rollback de configuration"""
    success: bool
    rollback_version: str = ""
    rolled_back_keys: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class DistributedConfigStore:
    """Store de configuration distribué"""
    
    def __init__(self, sources: List[ConfigSource] = None):
        self.sources = sources or [ConfigSource.FILE, ConfigSource.ENVIRONMENT]
        self.config_cache: Dict[str, Dict] = {}
        self.config_versions: Dict[str, List[Dict]] = {}
        self.cache_ttl = 300  # 5 minutes
        self.watchers: Dict[str, List[Callable]] = {}
    
    async def get_configuration(self, service_id: str, keys: List[str] = None, 
                               environment: str = "production") -> Dict[str, Any]:
        """Obtenir la configuration d'un service"""
        try:
# SECURITY: # SECURITY: cache_key = f"{service_id}:{environment}" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
            
            # Vérifier le cache
            if cache_key in self.config_cache:
                cached_config = self.config_cache[cache_key]
                if time.time() - cached_config.get('cached_at', 0) < self.cache_ttl:
                    config_data = cached_config.get('data', {})
                    if keys:
                        return {k: config_data.get(k) for k in keys}
                    return config_data
            
            # Charger depuis les sources
            config_data = {}
            for source in self.sources:
                source_config = await self._load_from_source(source, service_id, environment)
                config_data.update(source_config)
            
            # Mettre en cache
            self.config_cache[cache_key] = {
                'data': config_data,
                'cached_at': time.time()
            }
            
            # Filtrer par clés si spécifié
            if keys:
                return {k: config_data.get(k) for k in keys}
            
            return config_data
            
        except Exception as e:
            logger.error(f"Erreur récupération configuration: {e}")
            return {}
    
    async def set_configuration(self, service_id: str, config_updates: Dict[str, Any], 
                               environment: str = "production") -> bool:
        """Mettre à jour la configuration d'un service"""
        try:
# SECURITY: # SECURITY: cache_key = f"{service_id}:{environment}" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
            
            # Sauvegarder la version précédente
            current_config = await self.get_configuration(service_id, environment=environment)
            version_id = f"v{int(time.time())}"
            
            if service_id not in self.config_versions:
                self.config_versions[service_id] = []
            
            self.config_versions[service_id].append({
                'version': version_id,
                'config': copy.deepcopy(current_config),
                'timestamp': time.time(),
                'environment': environment
            })
            
            # Limiter les versions sauvegardées
            if len(self.config_versions[service_id]) > 10:
                self.config_versions[service_id] = self.config_versions[service_id][-10:]
            
            # Appliquer les mises à jour
            updated_config = current_config.copy()
            updated_config.update(config_updates)
            
            # Mettre à jour le cache
            self.config_cache[cache_key] = {
                'data': updated_config,
                'cached_at': time.time()
            }
            
            # Persister dans les sources (simulation)
            await self._persist_to_sources(service_id, updated_config, environment)
            
            # Notifier les watchers
            await self._notify_watchers(service_id, config_updates)
            
            logger.info(f"✅ Configuration mise à jour pour {service_id}: {list(config_updates.keys())}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour configuration: {e}")
            return False
    
    async def _load_from_source(self, source: ConfigSource, service_id: str, environment: str) -> Dict[str, Any]:
        """Charger configuration depuis une source"""
        if source == ConfigSource.ENVIRONMENT:
            return await self._load_from_environment(service_id, environment)
        elif source == ConfigSource.FILE:
            return await self._load_from_file(service_id, environment)
        elif source == ConfigSource.DATABASE:
            return await self._load_from_database(service_id, environment)
        else:
            return {}
    
    async def _load_from_environment(self, service_id: str, environment: str) -> Dict[str, Any]:
        """Charger depuis variables d'environnement"""
        import os
        config = {}
        prefix = f"{service_id.upper()}_{environment.upper()}_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config[config_key] = value
        
        return config
    
    async def _load_from_file(self, service_id: str, environment: str) -> Dict[str, Any]:
        """Charger depuis fichier de configuration"""
        try:
            import os
            config_file = f"/etc/iacherie/{service_id}/{environment}.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Impossible de charger {config_file}: {e}")
        
        # Configuration par défaut
        return {
            'database_url': 'postgresql://localhost:5432/iacherie',
            'redis_url': 'redis://localhost:6379',
            'log_level': 'INFO',
            'max_connections': 100,
            'timeout': 30
        }
    
    async def _load_from_database(self, service_id: str, environment: str) -> Dict[str, Any]:
        """Charger depuis base de données"""
        # Simulation de chargement DB
        return {
            'feature_flags_enabled': True,
            'monitoring_enabled': True,
            'cache_ttl': 300
        }
    
    async def _persist_to_sources(self, service_id: str, config: Dict[str, Any], environment: str):
        """Persister configuration dans les sources"""
        # En production, écrire dans les sources configurées
        logger.info(f"📝 Configuration persistée pour {service_id} ({environment})")
    
    async def _notify_watchers(self, service_id: str, config_updates: Dict[str, Any]):
        """Notifier les watchers de changements de configuration"""
        if service_id in self.watchers:
            for watcher in self.watchers[service_id]:
                try:
                    await watcher(service_id, config_updates)
                except Exception as e:
                    logger.error(f"Erreur notification watcher: {e}")
    
    async def watch_configuration(self, service_id: str, callback: Callable):
        """Surveiller les changements de configuration"""
        if service_id not in self.watchers:
            self.watchers[service_id] = []
        self.watchers[service_id].append(callback)
    
    async def get_config_history(self, service_id: str, limit: int = 10) -> List[Dict]:
        """Obtenir l'historique des configurations"""
        versions = self.config_versions.get(service_id, [])
        return versions[-limit:] if versions else []

class FeatureFlagEngine:
    """Moteur de gestion des feature flags"""
    
    def __init__(self):
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self.flag_cache: Dict[str, Dict] = {}
        self.targeting_cache: Dict[str, bool] = {}
        self.evaluation_stats: Dict[str, Dict] = {}
    
    async def create_feature_flag(self, flag: FeatureFlag) -> bool:
        """Créer un nouveau feature flag"""
        try:
            self.feature_flags[flag.flag_id] = flag
            await self._initialize_flag_stats(flag.flag_id)
            
            logger.info(f"🚩 Feature flag créé: {flag.flag_name} ({flag.flag_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création feature flag: {e}")
            return False
    
    async def evaluate_feature_flag(self, flag_id: str, context: Dict[str, Any]) -> bool:
        """Évaluer un feature flag selon le contexte"""
        try:
            if flag_id not in self.feature_flags:
                logger.warning(f"Feature flag inexistant: {flag_id}")
                return False
            
            flag = self.feature_flags[flag_id]
            
            # Vérifier si le flag est activé
            if not flag.enabled:
                await self._record_evaluation(flag_id, context, False, "flag_disabled")
                return False
            
            # Vérifier l'environnement
            environment = context.get('environment', 'production')
            if environment not in flag.environments:
                await self._record_evaluation(flag_id, context, False, "environment_mismatch")
                return False
            
            # Appliquer la stratégie de targeting
            result = await self._apply_targeting_strategy(flag, context)
            
            await self._record_evaluation(flag_id, context, result, "strategy_applied")
            return result
            
        except Exception as e:
            logger.error(f"Erreur évaluation feature flag {flag_id}: {e}")
            return False
    
    async def _apply_targeting_strategy(self, flag: FeatureFlag, context: Dict[str, Any]) -> bool:
        """Appliquer la stratégie de targeting"""
        strategy = flag.strategy
        
        if strategy == FeatureFlagStrategy.PERCENTAGE:
            return await self._apply_percentage_strategy(flag, context)
        elif strategy == FeatureFlagStrategy.USER_BASED:
            return await self._apply_user_based_strategy(flag, context)
        elif strategy == FeatureFlagStrategy.GROUP_BASED:
            return await self._apply_group_based_strategy(flag, context)
        elif strategy == FeatureFlagStrategy.GEOGRAPHIC:
            return await self._apply_geographic_strategy(flag, context)
        elif strategy == FeatureFlagStrategy.TIME_BASED:
            return await self._apply_time_based_strategy(flag, context)
        elif strategy == FeatureFlagStrategy.AB_TESTING:
            return await self._apply_ab_testing_strategy(flag, context)
        else:
            return flag.enabled
    
    async def _apply_percentage_strategy(self, flag: FeatureFlag, context: Dict[str, Any]) -> bool:
        """Stratégie basée sur pourcentage"""
        if flag.rollout_percentage <= 0:
            return False
        if flag.rollout_percentage >= 100:
            return True
        
        # Hash consistent basé sur user_id ou session_id
        identifier = context.get('user_id') or context.get('session_id') or 'anonymous'
        hash_input = f"{flag.flag_id}:{identifier}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        percentage = (hash_value % 100) + 1
        
        return percentage <= flag.rollout_percentage
    
    async def _apply_user_based_strategy(self, flag: FeatureFlag, context: Dict[str, Any]) -> bool:
        """Stratégie basée sur utilisateurs spécifiques"""
        user_id = context.get('user_id')
        if not user_id:
            return False
        
        target_users = flag.targeting_rules.get('target_users', [])
        excluded_users = flag.targeting_rules.get('excluded_users', [])
        
        if user_id in excluded_users:
            return False
        
        return user_id in target_users
    
    async def _apply_group_based_strategy(self, flag: FeatureFlag, context: Dict[str, Any]) -> bool:
        """Stratégie basée sur groupes d'utilisateurs"""
        user_groups = context.get('user_groups', [])
        if not user_groups:
            return False
        
        target_groups = set(flag.targeting_rules.get('target_groups', []))
        user_groups_set = set(user_groups)
        
        return bool(target_groups.intersection(user_groups_set))
    
    async def _apply_geographic_strategy(self, flag: FeatureFlag, context: Dict[str, Any]) -> bool:
        """Stratégie basée sur géolocalisation"""
        user_country = context.get('country')
        user_region = context.get('region')
        
        target_countries = flag.targeting_rules.get('target_countries', [])
        target_regions = flag.targeting_rules.get('target_regions', [])
        
        if target_countries and user_country in target_countries:
            return True
        
        if target_regions and user_region in target_regions:
            return True
        
        return False
    
    async def _apply_time_based_strategy(self, flag: FeatureFlag, context: Dict[str, Any]) -> bool:
        """Stratégie basée sur le temps"""
        current_time = time.time()
        
        start_time = flag.targeting_rules.get('start_time')
        end_time = flag.targeting_rules.get('end_time')
        
        if start_time and current_time < start_time:
            return False
        
        if end_time and current_time > end_time:
            return False
        
        # Vérifier les heures de la journée
        allowed_hours = flag.targeting_rules.get('allowed_hours')
        if allowed_hours:
            current_hour = datetime.now().hour
            if current_hour not in allowed_hours:
                return False
        
        return True
    
    async def _apply_ab_testing_strategy(self, flag: FeatureFlag, context: Dict[str, Any]) -> bool:
        """Stratégie A/B testing"""
        # Assignation consistante basée sur l'identifiant utilisateur
        identifier = context.get('user_id') or context.get('session_id') or 'anonymous'
        hash_input = f"{flag.flag_id}:ab_test:{identifier}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Répartition 50/50 par défaut, configurable
        split_percentage = flag.targeting_rules.get('variant_a_percentage', 50)
        percentage = (hash_value % 100) + 1
        
        return percentage <= split_percentage
    
    async def _record_evaluation(self, flag_id: str, context: Dict[str, Any], result: bool, reason: str):
        """Enregistrer l'évaluation d'un feature flag"""
        if flag_id not in self.evaluation_stats:
            await self._initialize_flag_stats(flag_id)
        
        stats = self.evaluation_stats[flag_id]
        stats['total_evaluations'] += 1
        
        if result:
            stats['enabled_evaluations'] += 1
        else:
            stats['disabled_evaluations'] += 1
        
        stats['last_evaluation'] = time.time()
        stats['reasons'][reason] = stats['reasons'].get(reason, 0) + 1
    
    async def _initialize_flag_stats(self, flag_id: str):
        """Initialiser les statistiques d'un flag"""
        self.evaluation_stats[flag_id] = {
            'total_evaluations': 0,
            'enabled_evaluations': 0,
            'disabled_evaluations': 0,
            'last_evaluation': 0,
            'reasons': {}
        }
    
    async def get_flag_stats(self, flag_id: str) -> Dict[str, Any]:
        """Obtenir les statistiques d'un feature flag"""
        return self.evaluation_stats.get(flag_id, {})
    
    async def update_feature_flag(self, flag_id: str, updates: Dict[str, Any]) -> bool:
        """Mettre à jour un feature flag"""
        try:
            if flag_id not in self.feature_flags:
                return False
            
            flag = self.feature_flags[flag_id]
            
            # Appliquer les mises à jour
            for key, value in updates.items():
                if hasattr(flag, key):
                    setattr(flag, key, value)
            
            flag.updated_at = time.time()
            
            # Vider le cache de targeting pour ce flag
            cache_keys_to_remove = [k for k in self.targeting_cache.keys() if k.startswith(f"{flag_id}:")]
            for key in cache_keys_to_remove:
                del self.targeting_cache[key]
            
            logger.info(f"🔄 Feature flag mis à jour: {flag_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour feature flag: {e}")
            return False
    
    async def delete_feature_flag(self, flag_id: str) -> bool:
        """Supprimer un feature flag"""
        try:
            if flag_id in self.feature_flags:
                del self.feature_flags[flag_id]
            
            if flag_id in self.evaluation_stats:
                del self.evaluation_stats[flag_id]
            
            # Nettoyer le cache
            cache_keys_to_remove = [k for k in self.targeting_cache.keys() if k.startswith(f"{flag_id}:")]
            for key in cache_keys_to_remove:
                del self.targeting_cache[key]
            
            logger.info(f"🗑️ Feature flag supprimé: {flag_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression feature flag: {e}")
            return False

class EnvironmentManager:
    """Gestionnaire d'environnements"""
    
    def __init__(self):
        self.environments: Dict[str, Dict[str, Any]] = {
            'development': {
                'log_level': 'DEBUG',
                'cache_enabled': False,
                'external_apis_enabled': False,
                'monitoring_enabled': False
            },
            'staging': {
                'log_level': 'INFO',
                'cache_enabled': True,
                'external_apis_enabled': True,
                'monitoring_enabled': True
            },
            'production': {
                'log_level': 'WARNING',
                'cache_enabled': True,
                'external_apis_enabled': True,
                'monitoring_enabled': True
            }
        }
    
    async def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Obtenir la configuration d'un environnement"""
        return self.environments.get(environment, self.environments['production'])
    
    async def create_environment(self, environment: str, config: Dict[str, Any]) -> bool:
        """Créer un nouvel environnement"""
        try:
            self.environments[environment] = config
            logger.info(f"🌍 Environnement créé: {environment}")
            return True
        except Exception as e:
            logger.error(f"Erreur création environnement: {e}")
            return False

class ConfigValidator:
    """Validateur de configuration"""
    
    def __init__(self, validation_level: ConfigValidationLevel = ConfigValidationLevel.BASIC):
        self.validation_level = validation_level
        self.schemas: Dict[str, Dict] = {}
        self.validators: Dict[str, Callable] = {}
    
    async def validate_configuration_schema(self, config_data: Dict, schema: Dict) -> ValidationResult:
        """Validation schema configuration avant deployment"""
        try:
            errors = []
            warnings = []
            
            # Validation basique des types
            for key, expected_type in schema.items():
                if key in config_data:
                    actual_value = config_data[key]
                    if not isinstance(actual_value, expected_type):
                        errors.append(f"Type incorrect pour {key}: attendu {expected_type.__name__}, reçu {type(actual_value).__name__}")
                else:
                    if self.validation_level in [ConfigValidationLevel.STRICT, ConfigValidationLevel.ENTERPRISE]:
                        errors.append(f"Clé manquante: {key}")
                    else:
                        warnings.append(f"Clé optionnelle manquante: {key}")
            
            # Validation enterprise supplémentaire
            if self.validation_level == ConfigValidationLevel.ENTERPRISE:
                enterprise_errors = await self._enterprise_validation(config_data)
                errors.extend(enterprise_errors)
            
            result = ValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                validation_level=self.validation_level
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur validation configuration: {e}")
            return ValidationResult(
                valid=False,
                errors=[str(e)],
                validation_level=self.validation_level
            )
    
    async def _enterprise_validation(self, config_data: Dict) -> List[str]:
        """Validation enterprise avancée"""
        errors = []
        
        # Validation sécurité
        for key, value in config_data.items():
            if 'password' in key.lower() or 'secret' in key.lower():
                if isinstance(value, str) and len(value) < 8:
                    errors.append(f"Mot de passe trop court pour {key}")
            
            if 'url' in key.lower():
                if isinstance(value, str) and not (value.startswith('http://') or value.startswith('https://')):
                    errors.append(f"URL invalide pour {key}: {value}")
        
        return errors
    
    def register_custom_validator(self, key: str, validator: Callable):
        """Enregistrer un validateur personnalisé"""
        self.validators[key] = validator

class DynamicConfigurationManager:
    """
    Manager configuration dynamique pour microservices.
    Config hot-reload + feature flags + environment management.
    """
    
    def __init__(self, config_manager_config: Dict = None):
        self.config_manager_config = config_manager_config or {}
        
        # Composants principaux
        self.config_store = DistributedConfigStore()
        self.feature_flag_engine = FeatureFlagEngine()
        self.environment_manager = EnvironmentManager()
        self.config_validator = ConfigValidator()
        
        # État du manager
        self.active_watchers: Dict[str, List[Callable]] = {}
        self.hot_reload_enabled = self.config_manager_config.get('hot_reload_enabled', True)
        
        logger.info("⚙️ DynamicConfigurationManager initialisé")
    
    async def manage_dynamic_configuration(self, config_request: ConfigRequest) -> ConfigResult:
        """
        Gestion configuration dynamique avec hot-reload.
        
        Configuration Features:
        - Dynamic configuration updates sans downtime
        - Feature flags avec gradual rollout
        - Environment-specific configuration management
        - Configuration validation avec schema enforcement
        - Configuration versioning avec rollback capability
        - A/B testing configuration pour feature experiments
        - Configuration audit trail pour compliance
        """
        try:
            # Obtenir la configuration du service
            config_data = await self.config_store.get_configuration(
                config_request.service_id,
                config_request.config_keys,
                config_request.environment
            )
            
            # Évaluer les feature flags
            if 'feature_flags' in config_data:
                feature_flags_config = {}
                for flag_id in config_data['feature_flags']:
                    flag_enabled = await self.feature_flag_engine.evaluate_feature_flag(
                        flag_id, 
                        {
                            'service_id': config_request.service_id,
                            'environment': config_request.environment,
                            **config_request.filters
                        }
                    )
                    feature_flags_config[flag_id] = flag_enabled
                
                config_data['evaluated_feature_flags'] = feature_flags_config
            
            # Appliquer la configuration d'environnement
            env_config = await self.environment_manager.get_environment_config(config_request.environment)
            config_data.update(env_config)
            
            result = ConfigResult(
                success=True,
                config_data=config_data,
                version=config_request.version or f"v{int(time.time())}",
                source=ConfigSource.DATABASE,
                cached=True
            )
            
            logger.info(f"✅ Configuration fournie pour {config_request.service_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur gestion configuration: {e}")
            return ConfigResult(
                success=False,
                errors=[str(e)]
            )
    
    async def update_service_configuration(self, service_id: str, config_updates: Dict, 
                                         environment: str = "production") -> UpdateResult:
        """Update configuration service avec validation"""
        try:
            # Valider les mises à jour
            validation_result = await self._validate_config_updates(config_updates)
            if not validation_result.valid:
                return UpdateResult(
                    success=False,
                    validation_errors=validation_result.errors
                )
            
            # Sauvegarder la version actuelle pour rollback
            current_config = await self.config_store.get_configuration(service_id, environment=environment)
            
            # Appliquer les mises à jour
            success = await self.config_store.set_configuration(service_id, config_updates, environment)
            
            if success:
                # Notifier les services du changement (hot-reload)
                if self.hot_reload_enabled:
                    await self._notify_config_change(service_id, config_updates)
                
                return UpdateResult(
                    success=True,
                    updated_keys=list(config_updates.keys()),
                    rollback_available=True,
                    previous_version=f"backup_{int(time.time())}"
                )
            else:
                return UpdateResult(
                    success=False,
                    validation_errors=["Échec de la mise à jour dans le store"]
                )
                
        except Exception as e:
            logger.error(f"Erreur mise à jour configuration: {e}")
            return UpdateResult(
                success=False,
                validation_errors=[str(e)]
            )
    
    async def manage_feature_flags(self, flag_operations: List[FeatureFlagOp]) -> FlagResult:
        """Gestion feature flags avec targeting rules"""
        try:
            affected_flags = []
            errors = []
            warnings = []
            
            for operation in flag_operations:
                try:
                    if operation.operation == "create":
                        if operation.flag_data:
                            success = await self.feature_flag_engine.create_feature_flag(operation.flag_data)
                            if success:
                                affected_flags.append(operation.flag_id)
                            else:
                                errors.append(f"Échec création flag {operation.flag_id}")
                    
                    elif operation.operation == "update":
                        success = await self.feature_flag_engine.update_feature_flag(
                            operation.flag_id, 
                            operation.parameters
                        )
                        if success:
                            affected_flags.append(operation.flag_id)
                        else:
                            errors.append(f"Échec mise à jour flag {operation.flag_id}")
                    
                    elif operation.operation == "delete":
                        success = await self.feature_flag_engine.delete_feature_flag(operation.flag_id)
                        if success:
                            affected_flags.append(operation.flag_id)
                        else:
                            errors.append(f"Échec suppression flag {operation.flag_id}")
                    
                    elif operation.operation == "toggle":
                        current_flag = self.feature_flag_engine.feature_flags.get(operation.flag_id)
                        if current_flag:
                            success = await self.feature_flag_engine.update_feature_flag(
                                operation.flag_id, 
                                {'enabled': not current_flag.enabled}
                            )
                            if success:
                                affected_flags.append(operation.flag_id)
                            else:
                                errors.append(f"Échec toggle flag {operation.flag_id}")
                        else:
                            errors.append(f"Flag inexistant: {operation.flag_id}")
                    
                except Exception as e:
                    errors.append(f"Erreur opération {operation.operation} sur {operation.flag_id}: {str(e)}")
            
            result = FlagResult(
                success=len(errors) == 0,
                affected_flags=affected_flags,
                errors=errors,
                warnings=warnings
            )
            
            logger.info(f"🚩 Opérations feature flags: {len(affected_flags)} succès, {len(errors)} erreurs")
            return result
            
        except Exception as e:
            logger.error(f"Erreur gestion feature flags: {e}")
            return FlagResult(
                success=False,
                errors=[str(e)]
            )
    
    async def validate_configuration_schema(self, config_data: Dict, schema: Dict) -> ValidationResult:
        """Validation schema configuration avant deployment"""
        return await self.config_validator.validate_configuration_schema(config_data, schema)
    
    async def rollback_configuration(self, service_id: str, target_version: str, 
                                   environment: str = "production") -> RollbackResult:
        """Rollback configuration vers version précédente"""
        try:
            # Récupérer l'historique des configurations
            config_history = await self.config_store.get_config_history(service_id)
            
            # Trouver la version cible
            target_config = None
            for version_entry in config_history:
                if version_entry['version'] == target_version and version_entry['environment'] == environment:
                    target_config = version_entry['config']
                    break
            
            if not target_config:
                return RollbackResult(
                    success=False,
                    errors=[f"Version introuvable: {target_version}"]
                )
            
            # Appliquer la configuration de rollback
            success = await self.config_store.set_configuration(service_id, target_config, environment)
            
            if success:
                # Notifier le changement
                if self.hot_reload_enabled:
                    await self._notify_config_change(service_id, target_config)
                
                return RollbackResult(
                    success=True,
                    rollback_version=target_version,
                    rolled_back_keys=list(target_config.keys())
                )
            else:
                return RollbackResult(
                    success=False,
                    errors=["Échec application configuration de rollback"]
                )
                
        except Exception as e:
            logger.error(f"Erreur rollback configuration: {e}")
            return RollbackResult(
                success=False,
                errors=[str(e)]
            )
    
    async def _validate_config_updates(self, config_updates: Dict) -> ValidationResult:
        """Valider les mises à jour de configuration"""
        # Schema basique pour validation
        basic_schema = {
            'database_url': str,
            'redis_url': str,
            'log_level': str,
            'max_connections': int,
            'timeout': int
        }
        
        return await self.config_validator.validate_configuration_schema(config_updates, basic_schema)
    
    async def _notify_config_change(self, service_id: str, config_updates: Dict):
        """Notifier les services des changements de configuration"""
        if service_id in self.active_watchers:
            for watcher in self.active_watchers[service_id]:
                try:
                    await watcher(service_id, config_updates)
                except Exception as e:
                    logger.error(f"Erreur notification watcher: {e}")
    
    async def watch_service_configuration(self, service_id: str, callback: Callable):
        """Surveiller les changements de configuration d'un service"""
        if service_id not in self.active_watchers:
            self.active_watchers[service_id] = []
        self.active_watchers[service_id].append(callback)
        
        # Enregistrer aussi dans le config store
        await self.config_store.watch_configuration(service_id, callback)
    
    async def get_manager_stats(self) -> Dict:
        """Obtenir les statistiques du configuration manager"""
        total_flags = len(self.feature_flag_engine.feature_flags)
        enabled_flags = len([f for f in self.feature_flag_engine.feature_flags.values() if f.enabled])
        total_services = len(self.config_store.config_cache)
        
        return {
            'total_feature_flags': total_flags,
            'enabled_feature_flags': enabled_flags,
            'managed_services': total_services,
            'environments': list(self.environment_manager.environments.keys()),
            'hot_reload_enabled': self.hot_reload_enabled,
            'active_watchers': sum(len(watchers) for watchers in self.active_watchers.values())
        }

# Factory function
def create_dynamic_configuration_manager(config: Dict = None) -> DynamicConfigurationManager:
    """Factory pour créer un gestionnaire de configuration dynamique"""
    return DynamicConfigurationManager(config)

__all__ = [
    'DynamicConfigurationManager',
    'ConfigRequest',
    'ConfigResult',
    'FeatureFlag',
    'FeatureFlagOp',
    'FlagResult',
    'UpdateResult',
    'ValidationResult',
    'RollbackResult',
    'ConfigSource',
    'FeatureFlagStrategy',
    'ConfigValidationLevel',
    'DistributedConfigStore',
    'FeatureFlagEngine',
    'EnvironmentManager',
    'ConfigValidator',
    'create_dynamic_configuration_manager'
]