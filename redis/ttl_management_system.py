#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⏰ TTL Management System - Gestion Intelligente TTL Redis
========================================================

Système de gestion automatique des TTL avec optimisation IA,
prédiction de durée de vie et ajustement dynamique.

**Rôles Experts:**
- **DBA**: Optimisation TTL et lifecycle données enterprise
- **ML Engineer**: Prédiction intelligente TTL basée patterns
- **Backend Senior**: Performance TTL et optimisation requêtes
- **DevOps**: Monitoring expirations et alertes proactives

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import aioredis

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTLStrategy(Enum):
    """Stratégies de gestion TTL"""
    FIXED = "fixed"  # TTL fixe
    ADAPTIVE = "adaptive"  # TTL adaptatif basé usage
    PREDICTIVE = "predictive"  # TTL prédictif ML
    SLIDING = "sliding"  # TTL sliding window
    CONTEXTUAL = "contextual"  # TTL basé contexte

class ExpirationEvent(Enum):
    """Événements d'expiration"""
    NATURAL_EXPIRY = "natural_expiry"
    EARLY_EVICTION = "early_eviction"
    MANUAL_DELETE = "manual_delete"
    TTL_EXTENDED = "ttl_extended"
    TTL_REDUCED = "ttl_reduced"

@dataclass
class TTLProfile:
    """Profil TTL pour type de données"""
    key_pattern: str
    default_ttl: int
    min_ttl: int
    max_ttl: int
    strategy: TTLStrategy
    ml_enabled: bool = True
    context_factors: List[str] = field(default_factory=list)
    adjustment_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KeyLifecycle:
    """Cycle de vie d'une clé Redis"""
    key_name: str
    created_at: float
    original_ttl: int
    current_ttl: Optional[int]
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    last_ttl_update: float = field(default_factory=time.time)
    access_pattern: List[float] = field(default_factory=list)
    expiration_predicted: Optional[float] = None
    value_size: int = 0
    key_type: str = "string"

@dataclass
class TTLMetrics:
    """Métriques TTL système"""
    total_keys_monitored: int = 0
    natural_expirations: int = 0
    early_evictions: int = 0
    ttl_adjustments: int = 0
    average_key_lifetime: float = 0.0
    memory_saved_by_ttl: int = 0
    cache_efficiency_improvement: float = 0.0

class TTLManagementSystem:
    """
    ⏰ Système de Gestion TTL Intelligent Redis
    
    **DBA Expert:**
    - Gestion lifecycle données enterprise avec policies avancées
    - Optimisation TTL pour performance et conformité GDPR
    - Monitoring expirations et cleanup automatisé
    - Stratégies TTL hiérarchiques par type données
    
    **ML Engineer:**
    - Prédiction TTL optimal avec algorithmes ML
    - Pattern recognition pour ajustement automatique
    - Clustering données par comportement TTL
    - Anomaly detection pour TTL anormaux
    
    **Backend Senior:**
    - Performance TTL avec batch operations
    - Optimisation requêtes expiration massive
    - Indexation intelligente clés TTL
    - Cache warming et éviction prédictive
    
    **DevOps:**
    - Monitoring temps réel expirations
    - Alertes proactives TTL critiques
    - Dashboard lifecycle et trending
    - Automation maintenance TTL
    """
    
    def __init__(self, redis_pool, config: Optional[Dict[str, Any]] = None):
        self.redis_pool = redis_pool
        self.config = config or {}
        
        # Configuration système
        self.monitoring_interval = self.config.get('monitoring_interval', 60)  # secondes
        self.batch_size = self.config.get('batch_size', 1000)
        self.ml_prediction_enabled = self.config.get('ml_prediction_enabled', True)
        self.max_tracked_keys = self.config.get('max_tracked_keys', 100000)
        
        # Profils TTL par type de données
        self.ttl_profiles: Dict[str, TTLProfile] = {}
        
        # Tracking lifecycle clés
        self.key_lifecycles: Dict[str, KeyLifecycle] = {}
        self.expiration_queue: Dict[float, Set[str]] = defaultdict(set)
        
        # Métriques et statistiques
        self.ttl_metrics = TTLMetrics()
        self.metrics_history: deque = deque(maxlen=10000)
        
        # ML pour prédiction TTL
        self.ttl_predictor: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_extractors: Dict[str, Callable] = {}
        
        # Cache optimisations
        self.ttl_cache: Dict[str, int] = {}  # Cache TTL calculés
        self.batch_operations: List[Tuple[str, str, Any]] = []  # Opérations en attente
        
        # Initialisation
        self._setup_default_profiles()
        asyncio.create_task(self._initialize_ml_predictor())
        asyncio.create_task(self._start_monitoring_loop())
        asyncio.create_task(self._start_optimization_loop())
        
        logger.info(f"⏰ TTL Management System initialisé (intervalle: {self.monitoring_interval}s)")
    
    def _setup_default_profiles(self):
        """**DBA**: Configuration profils TTL par défaut"""
        
        default_profiles = [
            # Sessions utilisateur
            TTLProfile(
                key_pattern="session:*",
                default_ttl=1800,  # 30 minutes
                min_ttl=300,       # 5 minutes
                max_ttl=7200,      # 2 heures
                strategy=TTLStrategy.ADAPTIVE,
                context_factors=["user_activity", "session_type"]
            ),
            
            # Cache API responses
            TTLProfile(
                key_pattern="api:*",
                default_ttl=300,   # 5 minutes
                min_ttl=60,        # 1 minute
                max_ttl=3600,      # 1 heure
                strategy=TTLStrategy.CONTEXTUAL,
                context_factors=["api_endpoint", "response_size", "update_frequency"]
            ),
            
            # Contenu multimédia
            TTLProfile(
                key_pattern="media:*",
                default_ttl=86400, # 24 heures
                min_ttl=3600,      # 1 heure
                max_ttl=604800,    # 7 jours
                strategy=TTLStrategy.PREDICTIVE,
                context_factors=["content_popularity", "file_size", "access_frequency"]
            ),
            
            # Cache ML models
            TTLProfile(
                key_pattern="ml_model:*",
                default_ttl=3600,  # 1 heure
                min_ttl=300,       # 5 minutes
                max_ttl=86400,     # 24 heures
                strategy=TTLStrategy.ADAPTIVE,
                context_factors=["model_accuracy", "inference_frequency", "model_size"]
            ),
            
            # Données temporaires
            TTLProfile(
                key_pattern="temp:*",
                default_ttl=300,   # 5 minutes
                min_ttl=60,        # 1 minute
                max_ttl=1800,      # 30 minutes
                strategy=TTLStrategy.FIXED
            ),
            
            # Cache analytics
            TTLProfile(
                key_pattern="analytics:*",
                default_ttl=3600,  # 1 heure
                min_ttl=300,       # 5 minutes
                max_ttl=86400,     # 24 heures
                strategy=TTLStrategy.SLIDING,
                context_factors=["data_freshness", "query_complexity"]
            )
        ]
        
        for profile in default_profiles:
            self.ttl_profiles[profile.key_pattern] = profile
    
    async def _initialize_ml_predictor(self):
        """**ML Engineer**: Initialisation prédicteur TTL ML"""
        try:
            if not self.ml_prediction_enabled:
                return
            
            # Modèle prédiction TTL optimal
            self.ttl_predictor = RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                random_state=42,
                n_jobs=-1
            )
            
            # Scaler pour normalisation
            self.scaler = StandardScaler()
            
            # Feature extractors pour différents types de données
            self.feature_extractors = {
                "temporal": self._extract_temporal_features,
                "usage": self._extract_usage_features,
                "content": self._extract_content_features,
                "context": self._extract_context_features
            }
            
            # Entraînement initial avec données simulées
            await self._train_initial_predictor()
            
            logger.info("✅ Prédicteur TTL ML initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation ML TTL: {e}")
    
    async def _train_initial_predictor(self):
        """**ML Engineer**: Entraînement initial avec données simulées"""
        try:
            # Génération données d'entraînement simulées
            n_samples = 2000
            features = []
            targets = []
            
            for _ in range(n_samples):
                # Features simulées
                hour_of_day = np.random.randint(0, 24)
                day_of_week = np.random.randint(0, 7)
                access_frequency = np.random.exponential(2.0)  # Accès par heure
                last_access_hours = np.random.exponential(1.0)  # Heures depuis dernier accès
                content_size_kb = np.random.lognormal(5, 2)  # Taille contenu
                content_popularity = np.random.beta(2, 5)  # Score popularité 0-1
                user_activity = np.random.beta(3, 2)  # Activité utilisateur 0-1
                
                feature_vector = [
                    hour_of_day, day_of_week, access_frequency, 
                    last_access_hours, content_size_kb, content_popularity, user_activity
                ]
                features.append(feature_vector)
                
                # TTL optimal calculé heuristiquement
                base_ttl = 3600  # 1 heure baseline
                
                # Ajustements basés sur features
                frequency_factor = min(3.0, 1.0 + access_frequency / 5.0)
                recency_factor = max(0.3, 1.0 - last_access_hours / 24.0)
                popularity_factor = 1.0 + content_popularity
                activity_factor = 1.0 + user_activity * 0.5
                
                optimal_ttl = base_ttl * frequency_factor * recency_factor * popularity_factor * activity_factor
                optimal_ttl = max(300, min(86400, optimal_ttl))  # Clamp 5min-24h
                
                targets.append(optimal_ttl)
            
            # Entraînement
            features_scaled = self.scaler.fit_transform(features)
            self.ttl_predictor.fit(features_scaled, targets)
            
            logger.info("✅ Prédicteur TTL entraîné avec données simulées")
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement prédicteur TTL: {e}")
    
    async def _start_monitoring_loop(self):
        """**DevOps**: Démarrage monitoring TTL continu"""
        asyncio.create_task(self._monitor_key_lifecycles())
        asyncio.create_task(self._process_expirations())
        asyncio.create_task(self._cleanup_tracking_data())
        logger.info("📊 Monitoring TTL démarré")
    
    async def _start_optimization_loop(self):
        """**Backend Senior**: Démarrage optimisation TTL"""
        asyncio.create_task(self._optimize_ttl_loop())
        asyncio.create_task(self._batch_operations_processor())
        logger.info("⚡ Optimisation TTL démarrée")
    
    async def set_ttl_smart(
        self, 
        key: str, 
        value: Any = None,
        context: Optional[Dict[str, Any]] = None,
        force_strategy: Optional[TTLStrategy] = None
    ) -> int:
        """**ML Engineer**: Définition TTL intelligent avec ML"""
        
        try:
            # Recherche profil TTL applicable
            profile = self._find_matching_profile(key)
            if not profile:
                # Profil par défaut
                profile = TTLProfile(
                    key_pattern="*",
                    default_ttl=3600,
                    min_ttl=300,
                    max_ttl=86400,
                    strategy=TTLStrategy.ADAPTIVE
                )
            
            # Calcul TTL selon stratégie
            strategy = force_strategy or profile.strategy
            calculated_ttl = await self._calculate_optimal_ttl(key, profile, strategy, context, value)
            
            # Application TTL
            async with self.redis_pool.get_connection() as redis_conn:
                await redis_conn.expire(key, calculated_ttl)
            
            # Tracking lifecycle
            await self._track_key_lifecycle(key, calculated_ttl, context)
            
            logger.debug(f"⏰ TTL défini: {key} = {calculated_ttl}s (stratégie: {strategy.value})")
            return calculated_ttl
            
        except Exception as e:
            logger.error(f"❌ Erreur définition TTL smart {key}: {e}")
            return profile.default_ttl if profile else 3600
    
    def _find_matching_profile(self, key: str) -> Optional[TTLProfile]:
        """**DBA**: Recherche profil TTL correspondant"""
        for pattern, profile in self.ttl_profiles.items():
            if self._match_pattern(key, pattern):
                return profile
        return None
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """**DBA**: Matching pattern clés"""
        if pattern == "*":
            return True
        
        if "*" in pattern:
            # Pattern avec wildcard
            import re
            regex_pattern = pattern.replace("*", ".*")
            return bool(re.match(f"^{regex_pattern}$", key))
        
        return key.startswith(pattern.rstrip("*"))
    
    async def _calculate_optimal_ttl(
        self,
        key: str,
        profile: TTLProfile,
        strategy: TTLStrategy,
        context: Optional[Dict[str, Any]] = None,
        value: Any = None
    ) -> int:
        """**ML Engineer**: Calcul TTL optimal selon stratégie"""
        
        base_ttl = profile.default_ttl
        
        if strategy == TTLStrategy.FIXED:
            return base_ttl
        
        elif strategy == TTLStrategy.ADAPTIVE:
            # TTL adaptatif basé sur historique d'accès
            lifecycle = self.key_lifecycles.get(key)
            if lifecycle:
                # Facteurs d'ajustement
                access_factor = min(2.0, lifecycle.access_count / 10.0)
                recency_factor = max(0.5, 1.0 - (time.time() - lifecycle.last_access) / 3600)
                
                adjusted_ttl = int(base_ttl * access_factor * recency_factor)
                return max(profile.min_ttl, min(profile.max_ttl, adjusted_ttl))
            
            return base_ttl
        
        elif strategy == TTLStrategy.PREDICTIVE:
            # TTL prédictif avec ML
            if self.ttl_predictor and self.ml_prediction_enabled:
                try:
                    features = await self._extract_all_features(key, context, value)
                    if features and len(features) > 0:
                        features_scaled = self.scaler.transform([features])
                        predicted_ttl = self.ttl_predictor.predict(features_scaled)[0]
                        
                        # Validation et contraintes
                        predicted_ttl = max(profile.min_ttl, min(profile.max_ttl, int(predicted_ttl)))
                        
                        logger.debug(f"🤖 TTL ML prédit: {key} = {predicted_ttl}s")
                        return predicted_ttl
                except Exception as e:
                    logger.warning(f"⚠️ Erreur prédiction ML TTL: {e}")
            
            # Fallback adaptatif
            return await self._calculate_optimal_ttl(key, profile, TTLStrategy.ADAPTIVE, context, value)
        
        elif strategy == TTLStrategy.SLIDING:
            # TTL sliding window - extension à chaque accès
            lifecycle = self.key_lifecycles.get(key)
            if lifecycle and time.time() - lifecycle.last_access < 300:  # Accès récent (5min)
                # Extension TTL
                extended_ttl = int(base_ttl * 1.5)
                return max(profile.min_ttl, min(profile.max_ttl, extended_ttl))
            
            return base_ttl
        
        elif strategy == TTLStrategy.CONTEXTUAL:
            # TTL basé sur contexte métier
            if context:
                context_multiplier = 1.0
                
                # Analyse facteurs contextuels
                for factor in profile.context_factors:
                    if factor in context:
                        value = context[factor]
                        
                        if factor == "user_activity" and isinstance(value, (int, float)):
                            context_multiplier *= (1.0 + value * 0.5)
                        elif factor == "content_popularity" and isinstance(value, (int, float)):
                            context_multiplier *= (1.0 + value)
                        elif factor == "update_frequency" and isinstance(value, (int, float)):
                            context_multiplier *= max(0.5, 1.0 - value * 0.3)
                
                contextual_ttl = int(base_ttl * context_multiplier)
                return max(profile.min_ttl, min(profile.max_ttl, contextual_ttl))
            
            return base_ttl
        
        return base_ttl
    
    async def _extract_all_features(
        self, 
        key: str, 
        context: Optional[Dict[str, Any]] = None,
        value: Any = None
    ) -> Optional[List[float]]:
        """**ML Engineer**: Extraction features complète pour ML"""
        try:
            features = []
            
            # Features temporelles
            temporal_features = await self.feature_extractors["temporal"](key, context)
            features.extend(temporal_features)
            
            # Features d'usage
            usage_features = await self.feature_extractors["usage"](key, context)
            features.extend(usage_features)
            
            # Features de contenu
            content_features = await self.feature_extractors["content"](key, context, value)
            features.extend(content_features)
            
            # Features contextuelles
            context_features = await self.feature_extractors["context"](key, context)
            features.extend(context_features)
            
            return features if len(features) == 7 else None  # Expected feature count
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction features {key}: {e}")
            return None
    
    async def _extract_temporal_features(self, key: str, context: Optional[Dict[str, Any]] = None) -> List[float]:
        """**ML Engineer**: Extraction features temporelles"""
        now = datetime.now()
        return [
            float(now.hour),
            float(now.weekday())
        ]
    
    async def _extract_usage_features(self, key: str, context: Optional[Dict[str, Any]] = None) -> List[float]:
        """**ML Engineer**: Extraction features d'usage"""
        lifecycle = self.key_lifecycles.get(key)
        if lifecycle:
            access_frequency = len(lifecycle.access_pattern) / max(1, (time.time() - lifecycle.created_at) / 3600)
            last_access_hours = (time.time() - lifecycle.last_access) / 3600
        else:
            access_frequency = 0.0
            last_access_hours = 0.0
        
        return [access_frequency, last_access_hours]
    
    async def _extract_content_features(self, key: str, context: Optional[Dict[str, Any]] = None, value: Any = None) -> List[float]:
        """**ML Engineer**: Extraction features de contenu"""
        # Taille estimée du contenu
        content_size = 0
        if value:
            try:
                if isinstance(value, str):
                    content_size = len(value.encode('utf-8'))
                elif isinstance(value, bytes):
                    content_size = len(value)
                else:
                    content_size = len(str(value).encode('utf-8'))
            except:
                content_size = 100  # Estimation par défaut
        
        content_size_kb = content_size / 1024.0
        
        # Popularité basée sur pattern de clé
        popularity = 0.5  # Par défaut
        if "popular" in key or "trending" in key:
            popularity = 0.8
        elif "temp" in key or "cache" in key:
            popularity = 0.2
        
        return [content_size_kb, popularity]
    
    async def _extract_context_features(self, key: str, context: Optional[Dict[str, Any]] = None) -> List[float]:
        """**ML Engineer**: Extraction features contextuelles"""
        user_activity = 0.5  # Par défaut
        
        if context:
            user_activity = context.get("user_activity", 0.5)
            if isinstance(user_activity, (int, float)):
                user_activity = max(0.0, min(1.0, float(user_activity)))
        
        return [user_activity]
    
    async def _track_key_lifecycle(self, key: str, ttl: int, context: Optional[Dict[str, Any]] = None):
        """**DBA**: Tracking lifecycle clé pour analytics"""
        current_time = time.time()
        
        if key in self.key_lifecycles:
            # Mise à jour lifecycle existant
            lifecycle = self.key_lifecycles[key]
            lifecycle.current_ttl = ttl
            lifecycle.last_ttl_update = current_time
            lifecycle.access_count += 1
            lifecycle.last_access = current_time
            lifecycle.access_pattern.append(current_time)
            
            # Limite taille pattern pour mémoire
            if len(lifecycle.access_pattern) > 100:
                lifecycle.access_pattern = lifecycle.access_pattern[-50:]
        else:
            # Nouveau lifecycle
            if len(self.key_lifecycles) >= self.max_tracked_keys:
                # Éviction LRU des lifecycles
                oldest_key = min(
                    self.key_lifecycles.keys(),
                    key=lambda k: self.key_lifecycles[k].last_access
                )
                del self.key_lifecycles[oldest_key]
            
            lifecycle = KeyLifecycle(
                key_name=key,
                created_at=current_time,
                original_ttl=ttl,
                current_ttl=ttl
            )
            
            self.key_lifecycles[key] = lifecycle
        
        # Ajout à queue d'expiration
        expiration_time = current_time + ttl
        self.expiration_queue[expiration_time].add(key)
    
    async def _monitor_key_lifecycles(self):
        """**DevOps**: Monitoring lifecycle clés continu"""
        while True:
            try:
                await asyncio.sleep(self.monitoring_interval)
                
                current_time = time.time()
                monitored_count = 0
                
                # Vérification état clés trackées
                for key, lifecycle in list(self.key_lifecycles.items()):
                    try:
                        async with self.redis_pool.get_connection() as redis_conn:
                            ttl = await redis_conn.ttl(key)
                            
                            if ttl == -2:  # Clé expirée
                                await self._handle_key_expiration(key, ExpirationEvent.NATURAL_EXPIRY)
                            elif ttl == -1:  # Clé sans TTL
                                # Clé modifiée sans TTL - nettoyage tracking
                                del self.key_lifecycles[key]
                            else:
                                # Mise à jour TTL actuel
                                lifecycle.current_ttl = ttl
                                monitored_count += 1
                    
                    except Exception as e:
                        logger.error(f"❌ Erreur monitoring clé {key}: {e}")
                
                # Mise à jour métriques
                self.ttl_metrics.total_keys_monitored = monitored_count
                
                logger.debug(f"📊 Monitoring TTL: {monitored_count} clés trackées")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur monitoring lifecycles: {e}")
    
    async def _handle_key_expiration(self, key: str, event_type: ExpirationEvent):
        """**DevOps**: Gestion expiration clé avec métriques"""
        try:
            lifecycle = self.key_lifecycles.get(key)
            if lifecycle:
                # Calcul statistiques lifetime
                lifetime = time.time() - lifecycle.created_at
                
                # Mise à jour métriques
                if event_type == ExpirationEvent.NATURAL_EXPIRY:
                    self.ttl_metrics.natural_expirations += 1
                elif event_type == ExpirationEvent.EARLY_EVICTION:
                    self.ttl_metrics.early_evictions += 1
                
                # Calcul moyenne lifetime
                if self.ttl_metrics.average_key_lifetime == 0:
                    self.ttl_metrics.average_key_lifetime = lifetime
                else:
                    self.ttl_metrics.average_key_lifetime = (
                        self.ttl_metrics.average_key_lifetime * 0.95 + lifetime * 0.05
                    )
                
                # Estimation mémoire économisée
                estimated_size = lifecycle.value_size or 1024  # 1KB par défaut
                self.ttl_metrics.memory_saved_by_ttl += estimated_size
                
                # Nettoyage tracking
                del self.key_lifecycles[key]
                
                logger.debug(f"⏰ Expiration trackée: {key} (lifetime: {lifetime:.1f}s)")
        
        except Exception as e:
            logger.error(f"❌ Erreur handling expiration {key}: {e}")
    
    async def _process_expirations(self):
        """**Backend Senior**: Traitement batch expirations programmées"""
        while True:
            try:
                await asyncio.sleep(60)  # Vérification chaque minute
                
                current_time = time.time()
                expired_times = []
                
                # Recherche expirations dues
                for expiration_time, keys in self.expiration_queue.items():
                    if expiration_time <= current_time:
                        expired_times.append(expiration_time)
                        
                        # Traitement batch expirations
                        for key in keys:
                            await self._handle_key_expiration(key, ExpirationEvent.NATURAL_EXPIRY)
                
                # Nettoyage queue expirations
                for expired_time in expired_times:
                    del self.expiration_queue[expired_time]
                
                if expired_times:
                    logger.info(f"⏰ {len(expired_times)} lots d'expirations traités")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur traitement expirations: {e}")
    
    async def _optimize_ttl_loop(self):
        """**ML Engineer**: Boucle optimisation TTL continue"""
        while True:
            try:
                await asyncio.sleep(300)  # Optimisation toutes les 5 minutes
                
                if self.ml_prediction_enabled and len(self.key_lifecycles) > 50:
                    await self._retrain_ttl_predictor()
                    await self._optimize_existing_ttls()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur optimisation TTL: {e}")
    
    async def _retrain_ttl_predictor(self):
        """**ML Engineer**: Re-entraînement prédicteur avec données réelles"""
        try:
            # Collecte données réelles pour re-entraînement
            features = []
            targets = []
            
            for key, lifecycle in self.key_lifecycles.items():
                if (len(lifecycle.access_pattern) > 5 and 
                    lifecycle.original_ttl > 0):
                    
                    # Features basées sur données réelles
                    feature_vector = await self._extract_all_features(key)
                    if feature_vector:
                        features.append(feature_vector)
                        
                        # Target = TTL optimal observé
                        actual_lifetime = time.time() - lifecycle.created_at
                        optimal_ttl = min(lifecycle.original_ttl * 2, actual_lifetime * 1.2)
                        targets.append(optimal_ttl)
            
            if len(features) > 20:  # Minimum pour re-entraînement
                # Re-entraînement incrémental
                features_scaled = self.scaler.fit_transform(features)
                self.ttl_predictor.fit(features_scaled, targets)
                
                logger.info(f"🔄 Prédicteur TTL re-entraîné avec {len(features)} échantillons")
        
        except Exception as e:
            logger.error(f"❌ Erreur re-entraînement TTL: {e}")
    
    async def _optimize_existing_ttls(self):
        """**Backend Senior**: Optimisation TTL clés existantes"""
        try:
            optimization_count = 0
            
            for key, lifecycle in list(self.key_lifecycles.items()):
                # Clés candidates à optimisation
                if (lifecycle.current_ttl and lifecycle.current_ttl > 300 and
                    time.time() - lifecycle.last_ttl_update > 1800):  # 30 min depuis dernière MAJ
                    
                    # Recalcul TTL optimal
                    profile = self._find_matching_profile(key)
                    if profile and profile.strategy in [TTLStrategy.ADAPTIVE, TTLStrategy.PREDICTIVE]:
                        new_ttl = await self._calculate_optimal_ttl(key, profile, profile.strategy)
                        
                        # Application si différence significative
                        if abs(new_ttl - lifecycle.current_ttl) > lifecycle.current_ttl * 0.2:
                            await self.set_ttl_smart(key)
                            optimization_count += 1
                            self.ttl_metrics.ttl_adjustments += 1
                            
                            if optimization_count >= 10:  # Limite batch
                                break
            
            if optimization_count > 0:
                logger.info(f"⚡ {optimization_count} TTL optimisés")
        
        except Exception as e:
            logger.error(f"❌ Erreur optimisation TTL existants: {e}")
    
    async def _batch_operations_processor(self):
        """**Backend Senior**: Processeur opérations batch TTL"""
        while True:
            try:
                await asyncio.sleep(5)  # Traitement toutes les 5 secondes
                
                if self.batch_operations:
                    operations = self.batch_operations[:self.batch_size]
                    self.batch_operations = self.batch_operations[self.batch_size:]
                    
                    # Traitement batch
                    async with self.redis_pool.get_connection() as redis_conn:
                        pipeline = redis_conn.pipeline()
                        
                        for operation, key, value in operations:
                            if operation == "expire":
                                pipeline.expire(key, value)
                            elif operation == "persist":
                                pipeline.persist(key)
                        
                        await pipeline.execute()
                    
                    logger.debug(f"⚡ Batch TTL: {len(operations)} opérations traitées")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur batch operations: {e}")
    
    async def _cleanup_tracking_data(self):
        """**DevOps**: Nettoyage données tracking périodique"""
        while True:
            try:
                await asyncio.sleep(3600)  # Nettoyage chaque heure
                
                current_time = time.time()
                cleaned_count = 0
                
                # Nettoyage lifecycles anciens
                keys_to_remove = []
                for key, lifecycle in self.key_lifecycles.items():
                    if current_time - lifecycle.last_access > 86400:  # 24h inactif
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self.key_lifecycles[key]
                    cleaned_count += 1
                
                # Nettoyage queue expirations anciennes
                expired_queue_times = []
                for expiration_time in self.expiration_queue.keys():
                    if expiration_time < current_time - 3600:  # 1h passé
                        expired_queue_times.append(expiration_time)
                
                for expired_time in expired_queue_times:
                    del self.expiration_queue[expired_time]
                    cleaned_count += 1
                
                if cleaned_count > 0:
                    logger.info(f"🧹 TTL cleanup: {cleaned_count} entrées nettoyées")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur cleanup TTL: {e}")
    
    async def get_ttl_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics TTL complet"""
        
        current_time = time.time()
        
        # Statistiques globales
        total_tracked = len(self.key_lifecycles)
        active_keys = len([k for k, l in self.key_lifecycles.items() 
                          if current_time - l.last_access < 3600])
        
        # Distribution TTL par profil
        ttl_by_profile = defaultdict(list)
        for key, lifecycle in self.key_lifecycles.items():
            profile = self._find_matching_profile(key)
            profile_name = profile.key_pattern if profile else "unknown"
            if lifecycle.current_ttl:
                ttl_by_profile[profile_name].append(lifecycle.current_ttl)
        
        # Métriques performance
        avg_lifetime = self.ttl_metrics.average_key_lifetime
        memory_saved_mb = self.ttl_metrics.memory_saved_by_ttl / 1024 / 1024
        
        # Top clés par lifetime
        top_keys_by_lifetime = sorted(
            [(k, time.time() - l.created_at, l.access_count) 
             for k, l in self.key_lifecycles.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "overview": {
                "total_tracked_keys": total_tracked,
                "active_keys_1h": active_keys,
                "total_expirations": self.ttl_metrics.natural_expirations + self.ttl_metrics.early_evictions,
                "ttl_adjustments": self.ttl_metrics.ttl_adjustments,
                "average_key_lifetime_hours": avg_lifetime / 3600,
                "memory_saved_mb": round(memory_saved_mb, 2)
            },
            "expiration_stats": {
                "natural_expirations": self.ttl_metrics.natural_expirations,
                "early_evictions": self.ttl_metrics.early_evictions,
                "expiration_ratio": (
                    self.ttl_metrics.natural_expirations / 
                    max(1, self.ttl_metrics.natural_expirations + self.ttl_metrics.early_evictions)
                )
            },
            "ttl_distribution": {
                profile: {
                    "count": len(ttls),
                    "avg_ttl": round(np.mean(ttls), 2) if ttls else 0,
                    "median_ttl": round(np.median(ttls), 2) if ttls else 0
                }
                for profile, ttls in ttl_by_profile.items()
            },
            "profiles": [
                {
                    "pattern": profile.key_pattern,
                    "strategy": profile.strategy.value,
                    "default_ttl": profile.default_ttl,
                    "ml_enabled": profile.ml_enabled
                }
                for profile in self.ttl_profiles.values()
            ],
            "top_keys_by_lifetime": [
                {
                    "key": key,
                    "lifetime_hours": round(lifetime / 3600, 2),
                    "access_count": access_count
                }
                for key, lifetime, access_count in top_keys_by_lifetime
            ],
            "ml_analytics": {
                "predictor_enabled": self.ml_prediction_enabled,
                "model_trained": self.ttl_predictor is not None,
                "predictions_made": len([l for l in self.key_lifecycles.values() 
                                       if l.expiration_predicted is not None])
            }
        }

# Factory function
async def create_ttl_management_system(redis_pool, config: Optional[Dict[str, Any]] = None):
    """**DBA**: Factory création système gestion TTL"""
    return TTLManagementSystem(redis_pool, config)

if __name__ == "__main__":
    async def demo():
        """Démonstration TTL Management System"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                mock = AsyncMock()
                mock.expire = AsyncMock(return_value=True)
                mock.ttl = AsyncMock(return_value=3600)
                return mock
        
        # Configuration système
        config = {
            'monitoring_interval': 10,
            'ml_prediction_enabled': True,
            'batch_size': 100
        }
        
        # Création système
        ttl_system = await create_ttl_management_system(MockRedisPool(), config)
        
        # Test définition TTL smart
        ttl_session = await ttl_system.set_ttl_smart(
            "session:user123",
            context={"user_activity": 0.8, "session_type": "premium"}
        )
        print(f"TTL session défini: {ttl_session}s")
        
        # Test TTL ML
        ttl_ml = await ttl_system.set_ttl_smart(
            "ml_model:recommendation",
            force_strategy=TTLStrategy.PREDICTIVE,
            context={"model_accuracy": 0.95, "inference_frequency": 100}
        )
        print(f"TTL ML prédit: {ttl_ml}s")
        
        # Attente tracking
        await asyncio.sleep(2)
        
        # Analytics
        analytics = await ttl_system.get_ttl_analytics()
        print(f"Clés trackées: {analytics['overview']['total_tracked_keys']}")
        print(f"Profiles TTL: {len(analytics['profiles'])}")
    
    asyncio.run(demo())