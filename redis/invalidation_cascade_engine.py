"""
Invalidation Cascade Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Invalidation Cascade Engine - Moteur Invalidation Cascade Enterprise
======================================================================

Moteur intelligent d'invalidation cascade avec propagation automatique
et gestion des dépendances pour maintenir la cohérence cache.

**Rôles Experts:**
- **Lead Dev IA**: Algorithmes IA pour invalidation intelligente et cascade
- **Backend Senior**: Architecture invalidation haute performance
- **DBA**: Gestion dépendances et cohérence données
- **Microservices**: Coordination invalidation distribuée

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Union, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
import yaml
import aioredis
from collections import defaultdict, deque
import networkx as nx
import asyncio

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvalidationType(Enum):
    """Types d'invalidation"""
    DIRECT = "direct"  # Invalidation directe
    CASCADE = "cascade"  # Invalidation cascade
    DEPENDENCY = "dependency"  # Basée dépendances
    TAG_BASED = "tag_based"  # Basée tags
    PATTERN = "pattern"  # Pattern matching
    TTL_REFRESH = "ttl_refresh"  # Rafraîchissement TTL
    SELECTIVE = "selective"  # Sélective conditionnelle

class InvalidationTrigger(Enum):
    """Déclencheurs d'invalidation"""
    DATA_UPDATE = "data_update"  # Mise à jour données
    SCHEMA_CHANGE = "schema_change"  # Changement schéma
    MANUAL = "manual"  # Manuel
    SCHEDULED = "scheduled"  # Planifié
    DEPENDENCY_CHANGE = "dependency_change"  # Changement dépendance
    TTL_EXPIRY = "ttl_expiry"  # Expiration TTL
    VERSION_UPDATE = "version_update"  # Mise à jour version
    POLICY_CHANGE = "policy_change"  # Changement politique

class InvalidationStrategy(Enum):
    """Stratégies d'invalidation"""
    IMMEDIATE = "immediate"  # Immédiate
    DEFERRED = "deferred"  # Différée
    BATCH = "batch"  # Par lot
    LAZY = "lazy"  # Lazy (à la demande)
    SMART = "smart"  # Intelligente conditionnelle

@dataclass
class DependencyRule:
    """Règle de dépendance cache"""
    source_pattern: str  # Pattern source
    dependent_patterns: List[str]  # Patterns dépendants
    invalidation_type: InvalidationType
    propagation_depth: int = 3  # Profondeur propagation
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # Priorité (1=haute, 5=basse)

@dataclass
class InvalidationEvent:
    """Événement d'invalidation"""
    event_id: str
    trigger: InvalidationTrigger
    source_keys: List[str]
    invalidation_type: InvalidationType
    strategy: InvalidationStrategy
    created_at: datetime
    executed_at: Optional[datetime] = None
    affected_keys: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InvalidationMetrics:
    """Métriques d'invalidation"""
    total_events: int = 0
    successful_invalidations: int = 0
    failed_invalidations: int = 0
    total_keys_invalidated: int = 0
    cascade_events: int = 0
    average_execution_time: float = 0.0
    average_cascade_depth: float = 0.0
    dependency_violations: int = 0

class InvalidationCascadeEngine:
    """
    ⚡ Moteur Invalidation Cascade Enterprise
    
    **Lead Dev IA**: Orchestration IA invalidation cascade intelligente
    **Backend Senior**: Architecture invalidation haute performance distribuée
    **DBA**: Gestion cohérence et dépendances données complexes
    **Microservices**: Coordination invalidation multi-services
    """
    
    def __init__(self, redis_pool, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.redis_pool = redis_pool
        self.config = config or self._get_default_config()
        
        # Graphe des dépendances
        self.dependency_graph = nx.DiGraph()
        self.dependency_rules: Dict[str, DependencyRule] = {}
        
        # Événements et métriques
        self.invalidation_events: Dict[str, InvalidationEvent] = {}
        self.metrics = InvalidationMetrics()
        self.event_history: deque = deque(maxlen=10000)
        
        # Tags et groupes
        self.tag_mappings: Dict[str, Set[str]] = defaultdict(set)  # tag -> keys
        self.key_tags: Dict[str, Set[str]] = defaultdict(set)  # key -> tags
        
        # Listeners et callbacks
        self.invalidation_listeners: Dict[str, List[Callable]] = defaultdict(list)
        
        # File d'attente invalidation
        self.invalidation_queue: asyncio.Queue = asyncio.Queue()
        self.batch_processor_task: Optional[asyncio.Task] = None
        
        # Cache local pour optimisation
        self.dependency_cache: Dict[str, List[str]] = {}
        self.last_dependency_refresh = 0
        
        logger.info("⚡ Invalidation Cascade Engine initialisé")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """**DBA**: Configuration par défaut optimisée"""
        return {
            'max_cascade_depth': 5,
            'batch_size': 100,
            'batch_timeout_ms': 1000,
            'enable_dependency_validation': True,
            'enable_circular_dependency_detection': True,
            'dependency_cache_ttl': 300,  # 5 minutes
            'max_concurrent_invalidations': 10,
            'enable_metrics': True,
            'enable_event_logging': True,
            'default_strategy': InvalidationStrategy.SMART.value,
            'patterns': {
                'user_data': r'user:\d+:.*',
                'media_content': r'media:\w+:.*',
                'cache_metadata': r'meta:.*',
                'session_data': r'session:\w+:.*'
            }
        }
    
    async def start_processor(self) -> None:
        """**Backend Senior**: Démarrage processeur invalidation"""
        if self.batch_processor_task and not self.batch_processor_task.done():
            logger.warning("⚠️ Processeur déjà en cours")
            return
        
        self.batch_processor_task = asyncio.create_task(self._batch_processor_loop())
        logger.info("🚀 Processeur invalidation démarré")
    
    async def stop_processor(self) -> None:
        """**Backend Senior**: Arrêt processeur invalidation"""
        if self.batch_processor_task:
            self.batch_processor_task.cancel()
            try:
                await self.batch_processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Processeur invalidation arrêté")
    
    async def _batch_processor_loop(self) -> None:
        """**Backend Senior**: Boucle traitement batch invalidations"""
        batch = []
        last_batch_time = time.time()
        
        while True:
            try:
                # Attente événement ou timeout
                timeout = self.config.get('batch_timeout_ms', 1000) / 1000.0
                
                try:
                    event = await asyncio.wait_for(self.invalidation_queue.get(), timeout=timeout)
                    batch.append(event)
                except asyncio.TimeoutError:
                    pass  # Timeout normal pour traitement batch
                
                current_time = time.time()
                batch_full = len(batch) >= self.config.get('batch_size', 100)
                batch_timeout = (current_time - last_batch_time) >= timeout
                
                # Traitement batch si conditions remplies
                if batch and (batch_full or batch_timeout):
                    await self._process_invalidation_batch(batch)
                    batch.clear()
                    last_batch_time = current_time
                
            except Exception as e:
                logger.error(f"❌ Erreur processeur batch: {e}")
                await asyncio.sleep(1)
    
    def add_dependency_rule(self, rule -> None: DependencyRule) -> None:
        """**DBA**: Ajout règle de dépendance"""
        rule_id = hashlib.md5(f"{rule.source_pattern}:{','.join(rule.dependent_patterns)}".encode()).hexdigest()
        self.dependency_rules[rule_id] = rule
        
        # Mise à jour graphe dépendances
        self._update_dependency_graph(rule)
        
        logger.info(f"📋 Règle dépendance ajoutée: {rule.source_pattern} -> {rule.dependent_patterns}")
    
    def _update_dependency_graph(self, rule -> None: DependencyRule) -> None:
        """**DBA**: Mise à jour graphe dépendances"""
        source = rule.source_pattern
        
        # Ajout noeud source
        if not self.dependency_graph.has_node(source):
            self.dependency_graph.add_node(source, rule=rule)
        
        # Ajout arêtes vers dépendants
        for dependent in rule.dependent_patterns:
            if not self.dependency_graph.has_node(dependent):
                self.dependency_graph.add_node(dependent)
            
            self.dependency_graph.add_edge(source, dependent, rule=rule)
        
        # Détection cycles si activée
        if self.config.get('enable_circular_dependency_detection', True):
            if not nx.is_directed_acyclic_graph(self.dependency_graph):
                cycles = list(nx.simple_cycles(self.dependency_graph))
                logger.warning(f"⚠️ Cycles détectés dans dépendances: {cycles}")
    
    def add_tag_mapping(self, tag -> None: str, keys -> None: List[str]) -> None:
        """**Backend Senior**: Ajout mapping tags-clés"""
        for key in keys:
            self.tag_mappings[tag].add(key)
            self.key_tags[key].add(tag)
        
        logger.debug(f"🏷️ Tag mapping ajouté: {tag} -> {len(keys)} clés")
    
    def remove_tag_mapping(self, tag -> None: str, keys -> None: Optional[List[str]] = None) -> None:
        """**Backend Senior**: Suppression mapping tags"""
        if keys:
            for key in keys:
                self.tag_mappings[tag].discard(key)
                self.key_tags[key].discard(tag)
        else:
            # Suppression complète du tag
            if tag in self.tag_mappings:
                for key in self.tag_mappings[tag]:
                    self.key_tags[key].discard(tag)
                del self.tag_mappings[tag]
        
        logger.debug(f"🗑️ Tag mapping supprimé: {tag}")
    
    async def invalidate_key(
        self,
        key: str,
        trigger: InvalidationTrigger = InvalidationTrigger.MANUAL,
        strategy: Optional[InvalidationStrategy] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """**Lead Dev IA**: Invalidation clé avec cascade intelligente"""
        
        event_id = f"inv_{int(time.time())}_{hashlib.md5(key.encode()).hexdigest()[:8]}"
        strategy = strategy or InvalidationStrategy(self.config.get('default_strategy', 'smart'))
        
        # Création événement
        event = InvalidationEvent(
            event_id=event_id,
            trigger=trigger,
            source_keys=[key],
            invalidation_type=InvalidationType.DIRECT,
            strategy=strategy,
            created_at=datetime.now(timezone.utc),
            context=context or {}
        )
        
        self.invalidation_events[event_id] = event
        
        # Ajout à la file d'attente
        await self.invalidation_queue.put(event)
        
        logger.info(f"📝 Invalidation programmée: {key} (ID: {event_id})")
        return event_id
    
    async def invalidate_by_pattern(
        self,
        pattern: str,
        trigger: InvalidationTrigger = InvalidationTrigger.MANUAL,
        strategy: Optional[InvalidationStrategy] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """**Backend Senior**: Invalidation par pattern"""
        
        event_id = f"inv_pattern_{int(time.time())}_{hashlib.md5(pattern.encode()).hexdigest()[:8]}"
        strategy = strategy or InvalidationStrategy(self.config.get('default_strategy', 'smart'))
        
        # Recherche clés correspondant au pattern
        matching_keys = await self._find_keys_by_pattern(pattern)
        
        event = InvalidationEvent(
            event_id=event_id,
            trigger=trigger,
            source_keys=matching_keys,
            invalidation_type=InvalidationType.PATTERN,
            strategy=strategy,
            created_at=datetime.now(timezone.utc),
            context={**(context or {}), 'pattern': pattern}
        )
        
        self.invalidation_events[event_id] = event
        await self.invalidation_queue.put(event)
        
        logger.info(f"📝 Invalidation pattern programmée: {pattern} ({len(matching_keys)} clés)")
        return event_id
    
    async def invalidate_by_tag(
        self,
        tag: str,
        trigger: InvalidationTrigger = InvalidationTrigger.MANUAL,
        strategy: Optional[InvalidationStrategy] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """**Backend Senior**: Invalidation par tag"""
        
        event_id = f"inv_tag_{int(time.time())}_{hashlib.md5(tag.encode()).hexdigest()[:8]}"
        strategy = strategy or InvalidationStrategy(self.config.get('default_strategy', 'smart'))
        
        # Récupération clés associées au tag
        tagged_keys = list(self.tag_mappings.get(tag, set()))
        
        event = InvalidationEvent(
            event_id=event_id,
            trigger=trigger,
            source_keys=tagged_keys,
            invalidation_type=InvalidationType.TAG_BASED,
            strategy=strategy,
            created_at=datetime.now(timezone.utc),
            context={**(context or {}), 'tag': tag}
        )
        
        self.invalidation_events[event_id] = event
        await self.invalidation_queue.put(event)
        
        logger.info(f"🏷️ Invalidation tag programmée: {tag} ({len(tagged_keys)} clés)")
        return event_id
    
    async def _process_invalidation_batch(self, events -> None: List[InvalidationEvent]) -> None:
        """**Backend Senior**: Traitement batch événements invalidation"""
        if not events:
            return
        
        logger.info(f"⚡ Traitement batch invalidation: {len(events)} événements")
        
        # Regroupement par stratégie
        strategy_groups = defaultdict(list)
        for event in events:
            strategy_groups[event.strategy].append(event)
        
        # Traitement par stratégie
        for strategy, strategy_events in strategy_groups.items():
            if strategy == InvalidationStrategy.IMMEDIATE:
                await self._process_immediate_invalidations(strategy_events)
            elif strategy == InvalidationStrategy.BATCH:
                await self._process_batch_invalidations(strategy_events)
            elif strategy == InvalidationStrategy.SMART:
                await self._process_smart_invalidations(strategy_events)
            else:
                await self._process_default_invalidations(strategy_events)
    
    async def _process_immediate_invalidations(self, events -> None: List[InvalidationEvent]) -> None:
        """**Backend Senior**: Traitement invalidations immédiates"""
        for event in events:
            await self._execute_single_invalidation(event)
    
    async def _process_batch_invalidations(self, events -> None: List[InvalidationEvent]) -> None:
        """**Backend Senior**: Traitement invalidations batch optimisé"""
        
        # Consolidation des clés à invalider
        all_keys = set()
        for event in events:
            all_keys.update(event.source_keys)
        
        # Calcul cascade consolidée
        cascade_keys = set()
        for key in all_keys:
            dependent_keys = await self._calculate_cascade_dependencies(key)
            cascade_keys.update(dependent_keys)
        
        # Invalidation consolidée
        final_keys = all_keys.union(cascade_keys)
        success = await self._execute_bulk_invalidation(list(final_keys))
        
        # Mise à jour événements
        for event in events:
            event.executed_at = datetime.now(timezone.utc)
            event.success = success
            event.affected_keys = list(final_keys)
            await self._update_event_metrics(event)
    
    async def _process_smart_invalidations(self, events -> None: List[InvalidationEvent]) -> None:
        """**Lead Dev IA**: Traitement invalidations intelligentes**"""
        
        # Analyse intelligent des événements
        for event in events:
            start_time = time.time()
            
            try:
                # Vérification nécessité invalidation
                needs_invalidation = await self._smart_invalidation_check(event)
                
                if not needs_invalidation:
                    event.executed_at = datetime.now(timezone.utc)
                    event.success = True
                    event.affected_keys = []
                    event.execution_time_ms = (time.time() - start_time) * 1000
                    logger.debug(f"🧠 Invalidation évitée (smart): {event.event_id}")
                    continue
                
                # Exécution invalidation optimisée
                await self._execute_single_invalidation(event)
                
            except Exception as e:
                logger.error(f"❌ Erreur invalidation smart {event.event_id}: {e}")
                event.executed_at = datetime.now(timezone.utc)
                event.success = False
                event.error_message = str(e)
                event.execution_time_ms = (time.time() - start_time) * 1000
    
    async def _smart_invalidation_check(self, event: InvalidationEvent) -> bool:
        """**Lead Dev IA**: Vérification intelligente nécessité invalidation"""
        
        # Vérification existence clés
        keys_exist = await self._check_keys_existence(event.source_keys)
        if not any(keys_exist.values()):
            return False  # Aucune clé n'existe
        
        # Vérification fraîcheur données (si contexte disponible)
        if 'last_modified' in event.context:
            is_fresh = await self._check_data_freshness(event.source_keys, event.context['last_modified'])
            if is_fresh:
                return False  # Données encore fraîches
        
        # Vérification impact cascade
        cascade_keys = []
        for key in event.source_keys:
            deps = await self._calculate_cascade_dependencies(key)
            cascade_keys.extend(deps)
        
        # Si pas de cascade, pas besoin d'invalidation sophistiquée
        if not cascade_keys:
            return len([k for k, exists in keys_exist.items() if exists]) > 0
        
        return True
    
    async def _process_default_invalidations(self, events -> None: List[InvalidationEvent]) -> None:
        """**Backend Senior**: Traitement invalidations par défaut"""
        for event in events:
            await self._execute_single_invalidation(event)
    
    async def _execute_single_invalidation(self, event -> None: InvalidationEvent) -> None:
        """**Backend Senior**: Exécution invalidation individuelle"""
        start_time = time.time()
        
        try:
            affected_keys = set(event.source_keys)
            
            # Calcul cascade dépendances
            if event.invalidation_type in [InvalidationType.CASCADE, InvalidationType.DEPENDENCY]:
                for source_key in event.source_keys:
                    cascade_keys = await self._calculate_cascade_dependencies(source_key)
                    affected_keys.update(cascade_keys)
            
            # Invalidation effective
            success = await self._execute_bulk_invalidation(list(affected_keys))
            
            # Mise à jour événement
            event.executed_at = datetime.now(timezone.utc)
            event.success = success
            event.affected_keys = list(affected_keys)
            event.execution_time_ms = (time.time() - start_time) * 1000
            
            # Notification listeners
            await self._notify_invalidation_listeners(event)
            
            # Mise à jour métriques
            await self._update_event_metrics(event)
            
            logger.debug(f"✅ Invalidation exécutée: {event.event_id} ({len(affected_keys)} clés)")
            
        except Exception as e:
            logger.error(f"❌ Erreur invalidation {event.event_id}: {e}")
            event.executed_at = datetime.now(timezone.utc)
            event.success = False
            event.error_message = str(e)
            event.execution_time_ms = (time.time() - start_time) * 1000
    
    async def _calculate_cascade_dependencies(self, key: str, depth: int = 0) -> List[str]:
        """**DBA**: Calcul dépendances cascade récursif"""
        
        if depth >= self.config.get('max_cascade_depth', 5):
            return []
        
        # Cache des dépendances pour optimisation
        cache_key = f"deps:{key}:{depth}"
        current_time = time.time()
        
        if (cache_key in self.dependency_cache and 
            current_time - self.last_dependency_refresh < self.config.get('dependency_cache_ttl', 300)):
            return self.dependency_cache[cache_key]
        
        dependent_keys = []
        
        # Recherche dans règles de dépendance
        for rule in self.dependency_rules.values():
            if self._matches_pattern(key, rule.source_pattern):
                
                # Vérification conditions
                if self._check_rule_conditions(key, rule):
                    
                    # Ajout dépendances directes
                    for dep_pattern in rule.dependent_patterns:
                        matching_deps = await self._find_keys_by_pattern(dep_pattern)
                        dependent_keys.extend(matching_deps)
                        
                        # Récursion pour cascade si autorisée
                        if rule.invalidation_type == InvalidationType.CASCADE and depth < rule.propagation_depth:
                            for dep_key in matching_deps:
                                cascade_deps = await self._calculate_cascade_dependencies(dep_key, depth + 1)
                                dependent_keys.extend(cascade_deps)
        
        # Recherche dans graphe de dépendances
        if self.dependency_graph.has_node(key):
            graph_deps = list(self.dependency_graph.successors(key))
            dependent_keys.extend(graph_deps)
        
        # Déduplication
        unique_deps = list(set(dependent_keys))
        
        # Mise en cache
        self.dependency_cache[cache_key] = unique_deps
        
        return unique_deps
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """**Backend Senior**: Vérification correspondance pattern"""
        import re
        try:
            return bool(re.match(pattern, key))
        except re.error:
            # Fallback simple matching
            return pattern in key or key.startswith(pattern.replace('*', ''))
    
    def _check_rule_conditions(self, key: str, rule: DependencyRule) -> bool:
        """**DBA**: Vérification conditions règle dépendance"""
        
        if not rule.conditions:
            return True
        
        # Conditions simples supportées
        for condition, value in rule.conditions.items():
            if condition == 'min_priority' and rule.priority > value:
                return False
            elif condition == 'exclude_patterns':
                for exclude_pattern in value:
                    if self._matches_pattern(key, exclude_pattern):
                        return False
        
        return True
    
    async def _find_keys_by_pattern(self, pattern: str) -> List[str]:
        """**Backend Senior**: Recherche clés par pattern"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                # Conversion pattern simple vers Redis pattern
                redis_pattern = pattern.replace('*', '*').replace('?', '?')
                
                keys = []
                async for key in redis_conn.scan_iter(match=redis_pattern, count=100):
                    keys.append(key)
                
                return keys
                
        except Exception as e:
            logger.error(f"❌ Erreur recherche pattern {pattern}: {e}")
            return []
    
    async def _execute_bulk_invalidation(self, keys: List[str]) -> bool:
        """**Backend Senior**: Invalidation bulk optimisée"""
        
        if not keys:
            return True
        
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                # Invalidation par batch pour performance
                batch_size = self.config.get('batch_size', 100)
                total_deleted = 0
                
                for i in range(0, len(keys), batch_size):
                    batch_keys = keys[i:i + batch_size]
                    deleted = await redis_conn.delete(*batch_keys)
                    total_deleted += deleted
                
                logger.debug(f"🗑️ Invalidation bulk: {total_deleted}/{len(keys)} clés supprimées")
                return total_deleted > 0
                
        except Exception as e:
            logger.error(f"❌ Erreur invalidation bulk: {e}")
            return False
    
    async def _check_keys_existence(self, keys: List[str]) -> Dict[str, bool]:
        """**Backend Senior**: Vérification existence clés"""
        existence_map = {}
        
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                for key in keys:
                    exists = await redis_conn.exists(key)
                    existence_map[key] = bool(exists)
            
            return existence_map
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification existence: {e}")
            return {key: False for key in keys}
    
    async def _check_data_freshness(self, keys: List[str], last_modified: float) -> bool:
        """**Lead Dev IA**: Vérification fraîcheur données intelligente"""
        
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                for key in keys:
                    # Vérification TTL restant
                    ttl = await redis_conn.ttl(key)
                    if ttl > 0:
                        # Récupération timestamp création si disponible
                        meta_key = f"meta:{key}"
                        meta_data = await redis_conn.get(meta_key)
                        
                        if meta_data:
                            try:
                                meta = json.loads(meta_data)
                                created_at = meta.get('created_at', 0)
                                
                                # Données fraîches si créées après dernière modification
                                if created_at > last_modified:
                                    return True
                            except (json.JSONDecodeError, KeyError):
                                pass
            
            return False  # Données pas fraîches par défaut
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification fraîcheur: {e}")
            return False
    
    async def _notify_invalidation_listeners(self, event -> None: InvalidationEvent) -> None:
        """**Microservices**: Notification listeners invalidation"""
        
        # Notification listeners génériques
        for listener in self.invalidation_listeners['*']:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event)
                else:
                    listener(event)
            except Exception as e:
                logger.error(f"❌ Erreur listener invalidation: {e}")
        
        # Notification listeners spécifiques
        for key in event.source_keys:
            for listener in self.invalidation_listeners.get(key, []):
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(event)
                    else:
                        listener(event)
                except Exception as e:
                    logger.error(f"❌ Erreur listener spécifique {key}: {e}")
    
    def register_invalidation_listener(self, key_pattern -> None: str, listener -> None: Callable) -> None:
        """**Microservices**: Enregistrement listener invalidation"""
        self.invalidation_listeners[key_pattern].append(listener)
        logger.info(f"👂 Listener invalidation enregistré: {key_pattern}")
    
    async def _update_event_metrics(self, event -> None: InvalidationEvent) -> None:
        """**DevOps**: Mise à jour métriques événement"""
        
        self.metrics.total_events += 1
        
        if event.success:
            self.metrics.successful_invalidations += 1
            self.metrics.total_keys_invalidated += len(event.affected_keys)
            
            # Cascade metrics
            if event.invalidation_type in [InvalidationType.CASCADE, InvalidationType.DEPENDENCY]:
                self.metrics.cascade_events += 1
                cascade_depth = len(event.affected_keys) - len(event.source_keys)
                if self.metrics.cascade_events > 0:
                    self.metrics.average_cascade_depth = (
                        self.metrics.average_cascade_depth * (self.metrics.cascade_events - 1) +
                        cascade_depth
                    ) / self.metrics.cascade_events
        else:
            self.metrics.failed_invalidations += 1
        
        # Temps d'exécution moyen
        if self.metrics.successful_invalidations > 0:
            self.metrics.average_execution_time = (
                self.metrics.average_execution_time * (self.metrics.successful_invalidations - 1) +
                event.execution_time_ms
            ) / self.metrics.successful_invalidations
        
        # Historique
        self.event_history.append({
            'event_id': event.event_id,
            'trigger': event.trigger.value,
            'type': event.invalidation_type.value,
            'success': event.success,
            'keys_count': len(event.affected_keys),
            'execution_time': event.execution_time_ms,
            'timestamp': event.executed_at.timestamp() if event.executed_at else None
        })
    
    async def get_invalidation_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics détaillées invalidation"""
        
        # Distribution par type d'invalidation
        type_distribution = defaultdict(int)
        trigger_distribution = defaultdict(int)
        success_by_type = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for record in self.event_history:
            inv_type = record['type']
            trigger = record['trigger']
            
            type_distribution[inv_type] += 1
            trigger_distribution[trigger] += 1
            
            success_by_type[inv_type]['total'] += 1
            if record['success']:
                success_by_type[inv_type]['success'] += 1
        
        # Calcul taux de succès
        success_rates = {}
        for inv_type, stats in success_by_type.items():
            success_rates[inv_type] = stats['success'] / max(1, stats['total'])
        
        return {
            'global_metrics': {
                'total_events': self.metrics.total_events,
                'successful_invalidations': self.metrics.successful_invalidations,
                'failed_invalidations': self.metrics.failed_invalidations,
                'success_rate': self.metrics.successful_invalidations / max(1, self.metrics.total_events),
                'total_keys_invalidated': self.metrics.total_keys_invalidated,
                'cascade_events': self.metrics.cascade_events,
                'average_execution_time': self.metrics.average_execution_time,
                'average_cascade_depth': self.metrics.average_cascade_depth
            },
            'distributions': {
                'by_type': dict(type_distribution),
                'by_trigger': dict(trigger_distribution),
                'success_rates': success_rates
            },
            'dependency_graph': {
                'nodes': self.dependency_graph.number_of_nodes(),
                'edges': self.dependency_graph.number_of_edges(),
                'rules': len(self.dependency_rules)
            },
            'tags': {
                'total_tags': len(self.tag_mappings),
                'total_tagged_keys': sum(len(keys) for keys in self.tag_mappings.values())
            },
            'recent_events': list(self.event_history)[-10:],  # 10 derniers
            'configuration': {
                'max_cascade_depth': self.config.get('max_cascade_depth'),
                'batch_size': self.config.get('batch_size'),
                'dependency_validation': self.config.get('enable_dependency_validation'),
                'circular_detection': self.config.get('enable_circular_dependency_detection')
            }
        }

# Factory function
async def create_invalidation_cascade_engine(redis_pool, config -> None: Optional[Dict[str, Any]] = None) -> None:
    """**Lead Dev IA**: Factory création moteur invalidation cascade"""
    engine = InvalidationCascadeEngine(redis_pool, config)
    await engine.start_processor()
    return engine

if __name__ == "__main__":
    async def demo() -> None:
        """Démonstration Invalidation Cascade Engine"""
        
        # Configuration Redis simulée
        class MockRedisPool:
    """MockRedisPool: class implementation"""
            def get_connection(self) -> None:
                from unittest.mock import AsyncMock
                mock = AsyncMock()
                mock.delete.return_value = 5
                mock.exists.return_value = 1
                mock.scan_iter.return_value = iter([f"key:{i}" for i in range(10)])
                return mock
        
        # Création engine
        engine = await create_invalidation_cascade_engine(MockRedisPool())
        
        # Ajout règles dépendance
        rule1 = DependencyRule(
            source_pattern="user:*",
            dependent_patterns=["session:*", "cache:user:*"],
            invalidation_type=InvalidationType.CASCADE,
            propagation_depth=2
        )
        engine.add_dependency_rule(rule1)
        
        # Test invalidation
        event_id = await engine.invalidate_key(
            "user:123",
            trigger=InvalidationTrigger.DATA_UPDATE,
            context={'last_modified': time.time()}
        )
        
        print(f"Invalidation programmée: {event_id}")
        
        # Attente traitement
        await asyncio.sleep(2)
        
        # Analytics
        analytics = await engine.get_invalidation_analytics()
        print(f"Analytics invalidation: {analytics}")
        
        # Arrêt
        await engine.stop_processor()
    
    asyncio.run(demo())