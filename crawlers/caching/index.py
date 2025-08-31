#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-Influencer Cache Index - Système de Gestion et Indexation de Cache Industriel
===============================================================================

Index et orchestrateur principal pour le système de cache industriel de la plateforme IA-Influencer.
Fournit une interface unifiée, la découverte automatique des modules et la gestion centralisée.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Copyright: Tous droits réservés. Utilisation, reproduction ou distribution non autorisée interdite.

⚠️ LOGICIEL PROPRIÉTAIRE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Créateurs → Upload → Index Cache → Répartition Intelligente → 
Performance Optimisée → Protection Renforcée → Monétisation Accélérée

Spécialités de l'équipe:
- Lead Dev IA: Architecture intelligence artificielle avancée
- Backend Senior: Infrastructure robuste et scalable  
- ML Engineer: Optimisations algorithmiques et prédictives
- DBA: Gestion base de données haute performance
- Sécurité: Protection multi-couche et chiffrement
- Microservices: Architecture distribuée résiliente
- Audio: Traitement optimisé contenus audio/musique
- DevOps: Déploiement et monitoring automatisé
- IA Prompt Engineer: Optimisation interactions IA
"""import asyncio
import logging
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Type, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import yaml
import pickle
import hashlib
import inspect
from collections import defaultdict, OrderedDict
import weakref
import gc

# Configuration et utilitaires
from ..utils.logger import get_logger
from ..config.cache_config import CacheIndexConfig
from .exceptions import CacheIndexError, ModuleDiscoveryError, IndexRegistrationError

# Imports des composants cache
from .cache_manager import IndustrialCacheManager, CacheConfig, CacheLevel
from .redis_cache import IndustrialRedisCache, RedisConfig, RedisMode
from .memory_cache import IndustrialMemoryCache, MemoryCacheConfig, EvictionPolicy
from .distributed_cache import IndustrialDistributedCache, DistributedCacheConfig
from .compression import IndustrialCacheCompressor, CompressionAlgorithm
from .monitoring import CacheMonitor, AlertSeverity, MonitoringConfig


class CacheModuleType(Enum):
    """Types de modules de cache supportés."""    CORE = "core"
    STORAGE = "storage"
    UTILITY = "utility"
    EXTENSION = "extension"
    PLUGIN = "plugin"
    STRATEGY = "strategy"
    MONITOR = "monitor"
    SECURITY = "security"


class CacheIndexStatus(Enum):
    """États possibles de l'index de cache."""    INITIALIZING = "initializing"
    READY = "ready"
    DEGRADED = "degraded"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"


@dataclass
class ModuleInfo:
    """Informations sur un module de cache."""    name: str
    module_type: CacheModuleType
    class_type: Type
    version: str
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    performance_tier: int = 1
    is_enabled: bool = True
    load_priority: int = 100
    health_status: str = "unknown"
    last_check: Optional[datetime] = None
    error_count: int = 0
    instance: Optional[Any] = None


@dataclass
class CacheIndexStats:
    """Statistiques de l'index de cache."""    total_modules: int = 0
    active_modules: int = 0
    failed_modules: int = 0
    total_cache_hits: int = 0
    total_cache_misses: int = 0
    average_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    redis_connections: int = 0
    distributed_nodes: int = 0
    compression_ratio: float = 0.0
    encryption_overhead: float = 0.0
    uptime_seconds: int = 0
    error_rate: float = 0.0
    throughput_per_second: float = 0.0


class IndustrialCacheIndex:
    """    Index et orchestrateur principal du système de cache industriel.
    
    Fournit:
    - Découverte automatique des modules
    - Gestion centralisée des instances
    - Routage intelligent des requêtes
    - Monitoring et métriques unifiées
    - Interface API simplifiée
    - Gestion des dépendances
    - Auto-healing et récupération
    """    
    def __init__(self, config: Optional[CacheIndexConfig] = None):
        """Initialise l'index de cache industriel."""        self.config = config or CacheIndexConfig()
        self.logger = get_logger(__name__)
        
        # État de l'index
        self.status = CacheIndexStatus.INITIALIZING
        self.start_time = datetime.now()
        self.modules: Dict[str, ModuleInfo] = {}
        self.instances: Dict[str, Any] = {}
        self.dependencies: Dict[str, List[str]] = defaultdict(list)
        
        # Statistiques et monitoring
        self.stats = CacheIndexStats()
        self.monitor: Optional[CacheMonitor] = None
        self.health_check_interval = 60  # secondes
        self.last_health_check = datetime.now()
        
        # Optimisations performance
        self.request_cache: Dict[str, Any] = {}
        self.routing_table: Dict[str, str] = {}
        self.load_balancer: Dict[str, List[str]] = defaultdict(list)
        
        # Gestionnaire d'événements
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.metrics_collectors: List[Callable] = []
        
        # Initialisation asynchrone
        self._initialization_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._background_tasks: List[asyncio.Task] = []
        
        self.logger.info("🚀 Index de cache industriel initialisé")
    
    async def initialize(self) -> bool:
        """Initialise complètement l'index de cache."""        async with self._initialization_lock:
            try:
                self.logger.info("🔄 Démarrage de l'initialisation de l'index de cache...")
                
                # 1. Découverte des modules
                await self._discover_modules()
                
                # 2. Validation des dépendances
                await self._validate_dependencies()
                
                # 3. Initialisation des instances
                await self._initialize_instances()
                
                # 4. Configuration du monitoring
                await self._setup_monitoring()
                
                # 5. Démarrage des tâches de fond
                await self._start_background_tasks()
                
                # 6. Validation finale
                await self._perform_health_check()
                
                self.status = CacheIndexStatus.READY
                self.logger.info("✅ Index de cache industriel prêt")
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Erreur initialisation index: {e}")
                self.status = CacheIndexStatus.ERROR
                return False
    
    async def _discover_modules(self) -> None:
        """Découvre automatiquement tous les modules de cache disponibles."""        self.logger.info("🔍 Découverte des modules de cache...")
        
        # Modules core obligatoires
        core_modules = {
            'cache_manager': (IndustrialCacheManager, CacheModuleType.CORE, 1),
            'redis_cache': (IndustrialRedisCache, CacheModuleType.STORAGE, 2),
            'memory_cache': (IndustrialMemoryCache, CacheModuleType.STORAGE, 3),
            'distributed_cache': (IndustrialDistributedCache, CacheModuleType.STORAGE, 4),
            'compression': (IndustrialCacheCompressor, CacheModuleType.UTILITY, 5)
        }
        
        for name, (class_type, module_type, priority) in core_modules.items():
            try:
                module_info = ModuleInfo(
                    name=name,
                    module_type=module_type,
                    class_type=class_type,
                    version=getattr(class_type, '__version__', '1.0.0'),
                    load_priority=priority,
                    capabilities=self._extract_capabilities(class_type),
                    dependencies=self._extract_dependencies(class_type)
                )
                
                self.modules[name] = module_info
                self.logger.debug(f"✅ Module découvert: {name}")
                
            except Exception as e:
                self.logger.error(f"❌ Erreur découverte module {name}: {e}")
        
        # Découverte automatique des modules optionnels
        await self._discover_optional_modules()
        
        self.stats.total_modules = len(self.modules)
        self.logger.info(f"🎯 {self.stats.total_modules} modules découverts")
    
    async def _discover_optional_modules(self) -> None:
        """Découvre les modules optionnels et extensions."""        optional_modules = [
            'encryption', 'metrics', 'strategies', 'persistence',
            'synchronization', 'optimization', 'preloading',
            'monitoring', 'policies', 'serializers'
        ]
        
        for module_name in optional_modules:
            try:
                # Import dynamique
                module_path = f".{module_name}"
                module = __import__(module_path, fromlist=[''], level=1)
                
                # Recherche de la classe principale
                main_class = self._find_main_class(module, module_name)
                if main_class:
                    module_info = ModuleInfo(
                        name=module_name,
                        module_type=CacheModuleType.UTILITY,
                        class_type=main_class,
                        version=getattr(main_class, '__version__', '1.0.0'),
                        load_priority=50,
                        capabilities=self._extract_capabilities(main_class)
                    )
                    
                    self.modules[module_name] = module_info
                    self.logger.debug(f"✅ Module optionnel découvert: {module_name}")
                    
            except ImportError:
                self.logger.debug(f"⚠️ Module optionnel non disponible: {module_name}")
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur découverte module {module_name}: {e}")
    
    def _find_main_class(self, module: Any, module_name: str) -> Optional[Type]:
        """Trouve la classe principale d'un module."""        # Patterns de nommage communs
        class_patterns = [
            f"Industrial{module_name.title().replace('_', '')}",
            f"{module_name.title().replace('_', '')}Manager",
            f"Cache{module_name.title().replace('_', '')}",
            f"{module_name.title().replace('_', '')}"
        ]
        
        for pattern in class_patterns:
            if hasattr(module, pattern):
                class_obj = getattr(module, pattern)
                if inspect.isclass(class_obj):
                    return class_obj
        
        # Fallback: première classe trouvée
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if not name.startswith('_') and obj.__module__ == module.__name__:
                return obj
        
        return None
    
    def _extract_capabilities(self, class_type: Type) -> List[str]:
        """Extrait les capacités d'une classe de cache."""        capabilities = []
        
        # Analyse des méthodes
        methods = [name for name, _ in inspect.getmembers(class_type, inspect.ismethod)]
        if 'get' in methods and 'set' in methods:
            capabilities.append('basic_cache')
        if 'get_many' in methods and 'set_many' in methods:
            capabilities.append('bulk_operations')
        if 'compress' in methods or hasattr(class_type, 'compression'):
            capabilities.append('compression')
        if 'encrypt' in methods or hasattr(class_type, 'encryption'):
            capabilities.append('encryption')
        if 'cluster' in methods or hasattr(class_type, 'cluster'):
            capabilities.append('clustering')
        if 'distribute' in methods or hasattr(class_type, 'distributed'):
            capabilities.append('distribution')
        if 'monitor' in methods or hasattr(class_type, 'monitoring'):
            capabilities.append('monitoring')
        
        # Analyse des attributs de classe
        if hasattr(class_type, 'SUPPORTS_TTL'):
            capabilities.append('ttl_support')
        if hasattr(class_type, 'SUPPORTS_PERSISTENCE'):
            capabilities.append('persistence')
        if hasattr(class_type, 'SUPPORTS_REPLICATION'):
            capabilities.append('replication')
        
        return capabilities
    
    def _extract_dependencies(self, class_type: Type) -> List[str]:
        """Extrait les dépendances d'une classe."""        dependencies = []
        
        # Analyse du constructeur
        try:
            signature = inspect.signature(class_type.__init__)
            for param_name, param in signature.parameters.items():
                if param_name != 'self' and param.annotation != inspect.Parameter.empty:
                    dep_name = getattr(param.annotation, '__name__', str(param.annotation))
                    if 'Cache' in dep_name:
                        dependencies.append(dep_name.lower())
        except Exception:
            pass
        
        # Dépendances hardcodées connues
        class_name = class_type.__name__.lower()
        if 'redis' in class_name:
            dependencies.append('redis')
        if 'distributed' in class_name:
            dependencies.extend(['redis', 'memory'])
        if 'manager' in class_name:
            dependencies.extend(['memory', 'redis'])
        
        return dependencies
    
    async def _validate_dependencies(self) -> None:
        """Valide les dépendances entre modules."""        self.logger.info("🔍 Validation des dépendances...")
        
        for module_name, module_info in self.modules.items():
            for dep in module_info.dependencies:
                if dep not in self.modules:
                    self.logger.warning(f"⚠️ Dépendance manquante pour {module_name}: {dep}")
                    module_info.is_enabled = False
                else:
                    self.dependencies[module_name].append(dep)
        
        # Tri topologique pour l'ordre d'initialisation
        self._sort_modules_by_dependencies()
    
    def _sort_modules_by_dependencies(self) -> None:
        """Trie les modules selon leurs dépendances."""        # Algorithme de tri topologique simple
        sorted_modules = []
        visited = set()
        temp_visited = set()
        
        def visit(module_name: str):
            if module_name in temp_visited:
                return  # Cycle détecté, ignorer
            if module_name in visited:
                return
            
            temp_visited.add(module_name)
            for dep in self.dependencies.get(module_name, []):
                if dep in self.modules:
                    visit(dep)
            
            temp_visited.remove(module_name)
            visited.add(module_name)
            sorted_modules.append(module_name)
        
        for module_name in self.modules:
            if module_name not in visited:
                visit(module_name)
        
        # Mise à jour des priorités
        for i, module_name in enumerate(sorted_modules):
            self.modules[module_name].load_priority = i + 1
    
    async def _initialize_instances(self) -> None:
        """Initialise les instances des modules par ordre de priorité."""        self.logger.info("🚀 Initialisation des instances de modules...")
        
        # Tri par priorité
        modules_by_priority = sorted(
            self.modules.items(),
            key=lambda x: x[1].load_priority
        )
        
        for module_name, module_info in modules_by_priority:
            if not module_info.is_enabled:
                continue
            
            try:
                # Configuration spécifique au module
                config = self._get_module_config(module_name)
                
                # Création de l'instance
                if config:
                    instance = module_info.class_type(config)
                else:
                    instance = module_info.class_type()
                
                # Initialisation si supportée
                if hasattr(instance, 'initialize') and callable(instance.initialize):
                    if asyncio.iscoroutinefunction(instance.initialize):
                        await instance.initialize()
                    else:
                        instance.initialize()
                
                self.instances[module_name] = instance
                module_info.instance = instance
                module_info.health_status = "healthy"
                
                self.logger.debug(f"✅ Instance initialisée: {module_name}")
                self.stats.active_modules += 1
                
            except Exception as e:
                self.logger.error(f"❌ Erreur initialisation {module_name}: {e}")
                module_info.health_status = "failed"
                module_info.error_count += 1
                self.stats.failed_modules += 1
    
    def _get_module_config(self, module_name: str) -> Optional[Any]:
        """Obtient la configuration spécifique d'un module."""        config_map = {
            'cache_manager': CacheConfig(),
            'redis_cache': RedisConfig(),
            'memory_cache': MemoryCacheConfig(),
            'distributed_cache': DistributedCacheConfig(),
            'monitoring': MonitoringConfig()
        }
        
        return config_map.get(module_name)
    
    async def _setup_monitoring(self) -> None:
        """Configure le système de monitoring."""        if 'monitoring' in self.instances:
            self.monitor = self.instances['monitoring']
            
            # Configuration des métriques
            await self._setup_metrics_collection()
            
            # Configuration des alertes
            await self._setup_alerting()
    
    async def _setup_metrics_collection(self) -> None:
        """Configure la collecte de métriques."""        if not self.monitor:
            return
        
        # Métriques système
        self.metrics_collectors.extend([
            self._collect_system_metrics,
            self._collect_cache_metrics,
            self._collect_performance_metrics
        ])
    
    async def _setup_alerting(self) -> None:
        """Configure le système d'alertes."""        if not self.monitor:
            return
        
        # Alertes critiques
        critical_alerts = [
            ("high_error_rate", self._check_error_rate, AlertSeverity.CRITICAL),
            ("memory_pressure", self._check_memory_pressure, AlertSeverity.WARNING),
            ("slow_response", self._check_response_time, AlertSeverity.WARNING)
        ]
        
        for alert_name, check_func, severity in critical_alerts:
            self.monitor.add_alert_rule(alert_name, check_func, severity)
    
    async def _start_background_tasks(self) -> None:
        """Démarre les tâches de fond."""        # Vérification de santé périodique
        health_task = asyncio.create_task(self._health_check_loop())
        self._background_tasks.append(health_task)
        
        # Collecte de métriques
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self._background_tasks.append(metrics_task)
        
        # Nettoyage automatique
        cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._background_tasks.append(cleanup_task)
        
        self.logger.info("🔄 Tâches de fond démarrées")
    
    async def _health_check_loop(self) -> None:
        """Boucle de vérification de santé."""        while not self._shutdown_event.is_set():
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Erreur vérification santé: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _perform_health_check(self) -> None:
        """Effectue une vérification complète de santé."""        self.last_health_check = datetime.now()
        
        for module_name, module_info in self.modules.items():
            if module_name not in self.instances:
                continue
            
            try:
                instance = self.instances[module_name]
                
                # Test de santé basique
                if hasattr(instance, 'health_check'):
                    health_result = await instance.health_check()
                    module_info.health_status = "healthy" if health_result else "degraded"
                else:
                    # Test ping basique
                    if hasattr(instance, 'ping'):
                        await instance.ping()
                    module_info.health_status = "healthy"
                
                module_info.last_check = datetime.now()
                
            except Exception as e:
                module_info.health_status = "failed"
                module_info.error_count += 1
                self.logger.warning(f"⚠️ Santé dégradée {module_name}: {e}")
    
    async def _metrics_collection_loop(self) -> None:
        """Boucle de collecte de métriques."""        while not self._shutdown_event.is_set():
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(30)  # Collecte toutes les 30 secondes
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Erreur collecte métriques: {e}")
                await asyncio.sleep(30)
    
    async def _collect_all_metrics(self) -> None:
        """Collecte toutes les métriques."""        for collector in self.metrics_collectors:
            try:
                await collector()
            except Exception as e:
                self.logger.error(f"❌ Erreur collecteur métriques: {e}")
    
    async def _collect_system_metrics(self) -> None:
        """Collecte les métriques système."""        import psutil
        
        # Mémoire
        memory = psutil.virtual_memory()
        self.stats.memory_usage_mb = memory.used / (1024 * 1024)
        
        # Uptime
        self.stats.uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
        
        # Modules actifs
        self.stats.active_modules = sum(
            1 for info in self.modules.values() 
            if info.health_status == "healthy"
        )
    
    async def _collect_cache_metrics(self) -> None:
        """Collecte les métriques de cache."""        total_hits = 0
        total_misses = 0
        total_response_time = 0.0
        instance_count = 0
        
        for instance in self.instances.values():
            if hasattr(instance, 'get_stats'):
                try:
                    stats = instance.get_stats()
                    total_hits += getattr(stats, 'hits', 0)
                    total_misses += getattr(stats, 'misses', 0)
                    total_response_time += getattr(stats, 'average_response_time', 0.0)
                    instance_count += 1
                except Exception:
                    pass
        
        self.stats.total_cache_hits = total_hits
        self.stats.total_cache_misses = total_misses
        if instance_count > 0:
            self.stats.average_response_time = total_response_time / instance_count
    
    async def _collect_performance_metrics(self) -> None:
        """Collecte les métriques de performance."""        # Calcul du taux d'erreur
        total_errors = sum(info.error_count for info in self.modules.values())
        total_operations = self.stats.total_cache_hits + self.stats.total_cache_misses
        
        if total_operations > 0:
            self.stats.error_rate = total_errors / total_operations
        
        # Calcul du débit
        if self.stats.uptime_seconds > 0:
            self.stats.throughput_per_second = total_operations / self.stats.uptime_seconds
    
    async def _cleanup_loop(self) -> None:
        """Boucle de nettoyage automatique."""        while not self._shutdown_event.is_set():
            try:
                await self._perform_cleanup()
                await asyncio.sleep(300)  # Nettoyage toutes les 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Erreur nettoyage: {e}")
                await asyncio.sleep(300)
    
    async def _perform_cleanup(self) -> None:
        """Effectue le nettoyage automatique."""        # Nettoyage du cache de requêtes
        current_time = time.time()
        expired_keys = [
            key for key, (value, timestamp) in self.request_cache.items()
            if current_time - timestamp > 300  # 5 minutes
        ]
        
        for key in expired_keys:
            del self.request_cache[key]
        
        # Garbage collection
        if len(expired_keys) > 100:
            gc.collect()
    
    # Méthodes de vérification d'alertes
    async def _check_error_rate(self) -> bool:
        """Vérifie le taux d'erreur."""        return self.stats.error_rate > 0.05  # 5%
    
    async def _check_memory_pressure(self) -> bool:
        """Vérifie la pression mémoire."""        return self.stats.memory_usage_mb > 1024  # 1GB
    
    async def _check_response_time(self) -> bool:
        """Vérifie le temps de réponse."""        return self.stats.average_response_time > 100  # 100ms
    
    # API publique
    async def get_cache_manager(self) -> Optional[IndustrialCacheManager]:
        """Obtient le gestionnaire de cache principal."""        return self.instances.get('cache_manager')
    
    async def get_module_instance(self, module_name: str) -> Optional[Any]:
        """Obtient l'instance d'un module spécifique."""        return self.instances.get(module_name)
    
    def get_modules_by_type(self, module_type: CacheModuleType) -> List[ModuleInfo]:
        """Obtient tous les modules d'un type spécifique."""        return [
            info for info in self.modules.values()
            if info.module_type == module_type
        ]
    
    def get_healthy_modules(self) -> List[str]:
        """Obtient la liste des modules en bonne santé."""        return [
            name for name, info in self.modules.items()
            if info.health_status == "healthy"
        ]
    
    async def reload_module(self, module_name: str) -> bool:
        """Recharge un module spécifique."""        if module_name not in self.modules:
            return False
        
        try:
            # Arrêt propre de l'instance existante
            if module_name in self.instances:
                instance = self.instances[module_name]
                if hasattr(instance, 'shutdown'):
                    await instance.shutdown()
                del self.instances[module_name]
            
            # Réinitialisation
            module_info = self.modules[module_name]
            config = self._get_module_config(module_name)
            
            if config:
                instance = module_info.class_type(config)
            else:
                instance = module_info.class_type()
            
            if hasattr(instance, 'initialize'):
                await instance.initialize()
            
            self.instances[module_name] = instance
            module_info.instance = instance
            module_info.health_status = "healthy"
            module_info.error_count = 0
            
            self.logger.info(f"✅ Module rechargé: {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur rechargement {module_name}: {e}")
            return False
    
    async def get_status_report(self) -> Dict[str, Any]:
        """Génère un rapport d'état complet."""        return {
            'index_status': self.status.value,
            'uptime_seconds': self.stats.uptime_seconds,
            'modules': {
                name: {
                    'type': info.module_type.value,
                    'health': info.health_status,
                    'errors': info.error_count,
                    'last_check': info.last_check.isoformat() if info.last_check else None
                }
                for name, info in self.modules.items()
            },
            'statistics': {
                'total_modules': self.stats.total_modules,
                'active_modules': self.stats.active_modules,
                'failed_modules': self.stats.failed_modules,
                'cache_hits': self.stats.total_cache_hits,
                'cache_misses': self.stats.total_cache_misses,
                'error_rate': self.stats.error_rate,
                'avg_response_time': self.stats.average_response_time,
                'throughput_per_second': self.stats.throughput_per_second,
                'memory_usage_mb': self.stats.memory_usage_mb
            }
        }
    
    async def shutdown(self) -> None:
        """Arrêt propre de l'index de cache."""        self.logger.info("🛑 Arrêt de l'index de cache...")
        
        self.status = CacheIndexStatus.SHUTDOWN
        self._shutdown_event.set()
        
        # Arrêt des tâches de fond
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
        
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Arrêt des instances
        for module_name, instance in self.instances.items():
            try:
                if hasattr(instance, 'shutdown'):
                    await instance.shutdown()
                self.logger.debug(f"✅ Module arrêté: {module_name}")
            except Exception as e:
                self.logger.error(f"❌ Erreur arrêt {module_name}: {e}")
        
        self.logger.info("✅ Index de cache arrêté")


# Instance globale
_global_cache_index: Optional[IndustrialCacheIndex] = None


async def get_cache_index(config: Optional[CacheIndexConfig] = None) -> IndustrialCacheIndex:
    """Obtient l'instance globale de l'index de cache."""    global _global_cache_index
    
    if _global_cache_index is None:
        _global_cache_index = IndustrialCacheIndex(config)
        await _global_cache_index.initialize()
    
    return _global_cache_index


async def shutdown_cache_index() -> None:
    """Arrête l'instance globale de l'index de cache."""    global _global_cache_index
    
    if _global_cache_index is not None:
        await _global_cache_index.shutdown()
        _global_cache_index = None


# Fonctions utilitaires
def get_available_modules() -> List[str]:
    """Obtient la liste des modules disponibles."""    if _global_cache_index:
        return list(_global_cache_index.modules.keys())
    return []


def get_module_info(module_name: str) -> Optional[ModuleInfo]:
    """Obtient les informations d'un module."""    if _global_cache_index and module_name in _global_cache_index.modules:
        return _global_cache_index.modules[module_name]
    return None


async def health_check() -> Dict[str, Any]:
    """Effectue une vérification de santé rapide."""    if _global_cache_index:
        return await _global_cache_index.get_status_report()
    return {'status': 'not_initialized'}


# Export des principales classes et fonctions
__all__ = [
    'IndustrialCacheIndex',
    'CacheModuleType',
    'CacheIndexStatus',
    'ModuleInfo',
    'CacheIndexStats',
    'get_cache_index',
    'shutdown_cache_index',
    'get_available_modules',
    'get_module_info',
    'health_check'
]
