#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 Cache Warming Scheduler - Planificateur Préchauffage Cache Enterprise
========================================================================

Planificateur intelligent de préchauffage cache avec IA pour optimisation
proactive des performances et réduction des cold starts.

**Rôles Experts:**
- **Lead Dev IA**: Algorithmes IA pour prédiction patterns préchauffage
- **ML Engineer**: Machine Learning pour optimisation timing et priorités
- **Backend Senior**: Architecture préchauffage haute performance
- **DevOps**: Planification automatisée et monitoring préchauffage

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
import yaml
import aioredis
from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import crontab
import schedule

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WarmingStrategy(Enum):
    """Stratégies de préchauffage cache"""
    PREDICTIVE = "predictive"  # Prédictif basé ML
    SCHEDULED = "scheduled"  # Planifié fixe
    ADAPTIVE = "adaptive"  # Adaptatif temps réel
    EVENT_DRIVEN = "event_driven"  # Basé événements
    POPULARITY_BASED = "popularity_based"  # Basé popularité
    TIME_BASED = "time_based"  # Basé patterns temporels
    HYBRID = "hybrid"  # Combinaison stratégies

class WarmingPriority(Enum):
    """Priorités de préchauffage"""
    CRITICAL = "critical"  # Critique - exécution immédiate
    HIGH = "high"  # Haute - dans les 5 minutes
    MEDIUM = "medium"  # Moyenne - dans les 30 minutes
    LOW = "low"  # Basse - dans l'heure
    BACKGROUND = "background"  # Arrière-plan - quand possible

class WarmingTrigger(Enum):
    """Déclencheurs de préchauffage"""
    SCHEDULE = "schedule"  # Planifié
    TRAFFIC_SPIKE = "traffic_spike"  # Pic de trafic
    CACHE_MISS_RATE = "cache_miss_rate"  # Taux miss élevé
    TIME_PATTERN = "time_pattern"  # Pattern temporel
    USER_BEHAVIOR = "user_behavior"  # Comportement utilisateur
    SYSTEM_EVENT = "system_event"  # Événement système
    MANUAL = "manual"  # Manuel

@dataclass
class WarmingTask:
    """Tâche de préchauffage cache"""
    task_id: str
    key_pattern: str
    data_source: str  # Source des données à préchauffer
    strategy: WarmingStrategy
    priority: WarmingPriority
    trigger: WarmingTrigger
    scheduled_time: Optional[datetime] = None
    ttl_seconds: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None
    success: bool = False
    execution_time_ms: float = 0.0
    warmed_keys: List[str] = field(default_factory=list)

@dataclass
class WarmingMetrics:
    """Métriques de préchauffage"""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    total_keys_warmed: int = 0
    average_execution_time: float = 0.0
    cache_hit_improvement: float = 0.0
    last_warming_time: float = 0.0
    strategy_performance: Dict[str, float] = field(default_factory=dict)

class CacheWarmingScheduler:
    """
    🔥 Planificateur Préchauffage Cache Enterprise
    
    **Lead Dev IA**: Orchestration IA préchauffage prédictif intelligent
    **ML Engineer**: Algorithmes ML prédiction patterns et optimisation timing
    **Backend Senior**: Architecture préchauffage haute performance
    **DevOps**: Automation planification et monitoring opérationnel
    """
    
    def __init__(self, redis_pool, cache_policy_engine=None, config: Optional[Dict[str, Any]] = None):
        self.redis_pool = redis_pool
        self.cache_policy_engine = cache_policy_engine
        self.config = config or self._get_default_config()
        
        # Gestion des tâches
        self.warming_tasks: Dict[str, WarmingTask] = {}
        self.scheduled_tasks: Dict[str, WarmingTask] = {}
        self.active_warmings: Set[str] = set()
        
        # ML pour prédictions
        self.ml_model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        
        # Métriques et analytics
        self.metrics = WarmingMetrics()
        self.warming_history: deque = deque(maxlen=10000)
        self.traffic_patterns: deque = deque(maxlen=1000)
        
        # Sources de données configurables
        self.data_sources: Dict[str, Callable] = {}
        
        # Planificateur interne
        self.scheduler_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        logger.info("🔥 Cache Warming Scheduler initialisé")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """**DevOps**: Configuration par défaut optimisée"""
        return {
            'warming_enabled': True,
            'ml_enabled': True,
            'max_concurrent_warmings': 5,
            'warming_batch_size': 100,
            'default_ttl': 3600,
            'strategies': {
                'predictive': {'weight': 0.3, 'enabled': True},
                'scheduled': {'weight': 0.2, 'enabled': True},
                'adaptive': {'weight': 0.2, 'enabled': True},
                'popularity_based': {'weight': 0.2, 'enabled': True},
                'time_based': {'weight': 0.1, 'enabled': True}
            },
            'triggers': {
                'cache_miss_threshold': 0.3,  # 30% miss rate
                'traffic_spike_threshold': 2.0,  # 2x traffic normal
                'warming_window_hours': 24
            },
            'schedules': {
                'morning_peak': '0 8 * * *',  # 8h du matin
                'evening_peak': '0 18 * * *',  # 18h
                'weekend_prep': '0 6 * * 6',  # Samedi 6h
                'weekly_cleanup': '0 2 * * 1'  # Lundi 2h
            }
        }
    
    async def initialize_ml_model(self):
        """**ML Engineer**: Initialisation modèle ML prédiction"""
        try:
            self.ml_model = RandomForestRegressor(
                n_estimators=150,
                max_depth=12,
                random_state=42,
                min_samples_split=5,
                min_samples_leaf=2
            )
            self.scaler = StandardScaler()
            
            # Entraînement avec données historiques
            await self._train_prediction_model()
            
            logger.info("✅ Modèle ML préchauffage initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation ML préchauffage: {e}")
    
    async def _train_prediction_model(self):
        """**ML Engineer**: Entraînement modèle prédiction patterns"""
        try:
            # Génération données d'entraînement simulées
            n_samples = 3000
            features = []
            targets = []
            
            for _ in range(n_samples):
                # Features: heure, jour_semaine, traffic_load, cache_miss_rate, recent_activity
                hour = np.random.randint(0, 24)
                day_week = np.random.randint(0, 7)
                traffic_load = np.random.lognormal(1.0, 0.5)
                cache_miss_rate = np.random.beta(2, 8)  # Biaisé vers low miss
                recent_activity = np.random.exponential(1.0)
                user_count = np.random.poisson(100)
                
                features.append([hour, day_week, traffic_load, cache_miss_rate, recent_activity, user_count])
                
                # Target: probabilité de nécessiter préchauffage (0-1)
                warming_need = (
                    0.3 * self._hour_pattern(hour) +  # Peak hours
                    0.2 * self._day_pattern(day_week) +  # Weekend patterns
                    0.2 * min(1.0, traffic_load / 2.0) +  # High traffic
                    0.3 * cache_miss_rate  # High miss rate
                )
                
                targets.append(min(1.0, warming_need))
            
            # Entraînement
            features_scaled = self.scaler.fit_transform(features)
            self.ml_model.fit(features_scaled, targets)
            
            score = self.ml_model.score(features_scaled, targets)
            logger.info(f"🎯 Modèle ML préchauffage entraîné - Score: {score:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement ML préchauffage: {e}")
    
    def _hour_pattern(self, hour: int) -> float:
        """**ML Engineer**: Pattern horaire d'activité"""
        # Pics à 9h, 14h, 20h
        peaks = [9, 14, 20]
        pattern = 0.0
        for peak in peaks:
            distance = min(abs(hour - peak), 24 - abs(hour - peak))
            pattern += max(0, 1.0 - distance / 3.0)
        return min(1.0, pattern)
    
    def _day_pattern(self, day: int) -> float:
        """**ML Engineer**: Pattern jour de semaine"""
        # Weekend plus actif pour contenu créatif
        weekend_boost = 0.3 if day in [5, 6] else 0.0  # Samedi, Dimanche
        weekday_pattern = 0.7 if day in [1, 2, 3, 4] else 0.5  # Lun-Jeu
        return weekday_pattern + weekend_boost
    
    async def start_scheduler(self):
        """**DevOps**: Démarrage planificateur automatique"""
        if self.scheduler_running:
            logger.warning("⚠️ Planificateur déjà en cours")
            return
        
        self.scheduler_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Chargement tâches planifiées
        await self._load_scheduled_tasks()
        
        logger.info("🚀 Planificateur préchauffage démarré")
    
    async def stop_scheduler(self):
        """**DevOps**: Arrêt planificateur"""
        self.scheduler_running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Planificateur préchauffage arrêté")
    
    async def _scheduler_loop(self):
        """**DevOps**: Boucle principale planificateur"""
        while self.scheduler_running:
            try:
                # Vérification tâches planifiées
                await self._check_scheduled_tasks()
                
                # Détection besoins préchauffage adaptatif
                if self.config.get('ml_enabled', True):
                    await self._detect_warming_needs()
                
                # Exécution tâches en attente
                await self._execute_pending_tasks()
                
                # Nettoyage tâches terminées
                await self._cleanup_completed_tasks()
                
                # Pause avant prochaine itération
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle planificateur: {e}")
                await asyncio.sleep(30)
    
    async def _load_scheduled_tasks(self):
        """**Backend Senior**: Chargement tâches planifiées depuis config"""
        schedules = self.config.get('schedules', {})
        
        for schedule_name, cron_expr in schedules.items():
            task_id = f"scheduled_{schedule_name}"
            
            # Parsing expression cron pour prochaine exécution
            next_run = self._parse_cron_next_run(cron_expr)
            
            if next_run:
                warming_task = WarmingTask(
                    task_id=task_id,
                    key_pattern=f"*",  # Pattern par défaut
                    data_source=schedule_name,
                    strategy=WarmingStrategy.SCHEDULED,
                    priority=WarmingPriority.MEDIUM,
                    trigger=WarmingTrigger.SCHEDULE,
                    scheduled_time=next_run,
                    context={'cron_expression': cron_expr, 'schedule_name': schedule_name}
                )
                
                self.scheduled_tasks[task_id] = warming_task
                logger.info(f"📅 Tâche planifiée: {schedule_name} - {next_run}")
    
    def _parse_cron_next_run(self, cron_expr: str) -> Optional[datetime]:
        """**DevOps**: Parsing expression cron pour prochaine exécution"""
        try:
            cron = crontab.CronTab(cron_expr)
            next_run_seconds = cron.next()
            return datetime.now(timezone.utc) + timedelta(seconds=next_run_seconds)
        except Exception as e:
            logger.error(f"❌ Erreur parsing cron '{cron_expr}': {e}")
            return None
    
    async def _check_scheduled_tasks(self):
        """**DevOps**: Vérification et déclenchement tâches planifiées"""
        current_time = datetime.now(timezone.utc)
        
        for task_id, task in list(self.scheduled_tasks.items()):
            if task.scheduled_time and current_time >= task.scheduled_time:
                # Déclenchement tâche
                await self._queue_warming_task(task)
                
                # Re-planification pour prochaine occurrence
                if 'cron_expression' in task.context:
                    next_run = self._parse_cron_next_run(task.context['cron_expression'])
                    if next_run:
                        task.scheduled_time = next_run
                    else:
                        del self.scheduled_tasks[task_id]
    
    async def _detect_warming_needs(self):
        """**Lead Dev IA**: Détection intelligente besoins préchauffage"""
        try:
            # Collecte métriques actuelles
            current_metrics = await self._collect_current_metrics()
            
            # Prédiction ML si modèle disponible
            if self.ml_model:
                warming_probability = await self._predict_warming_need(current_metrics)
                
                if warming_probability > 0.7:  # Seuil élevé pour déclenchement
                    await self._create_predictive_warming_task(current_metrics, warming_probability)
            
            # Détection seuils
            await self._check_threshold_triggers(current_metrics)
            
        except Exception as e:
            logger.error(f"❌ Erreur détection besoins préchauffage: {e}")
    
    async def _collect_current_metrics(self) -> Dict[str, Any]:
        """**Backend Senior**: Collecte métriques actuelles système"""
        current_time = datetime.now(timezone.utc)
        
        # Métriques temporelles
        hour = current_time.hour
        day_week = current_time.weekday()
        
        # Métriques cache (simulées pour démo)
        cache_metrics = {
            'hit_rate': 0.85,  # À récupérer du cache_policy_engine
            'miss_rate': 0.15,
            'total_requests': 1000,
            'average_latency': 5.2
        }
        
        # Métriques trafic (simulées)
        traffic_metrics = {
            'current_load': 1.2,
            'concurrent_users': 150,
            'requests_per_second': 50
        }
        
        return {
            'time': {
                'hour': hour,
                'day_week': day_week,
                'timestamp': current_time.timestamp()
            },
            'cache': cache_metrics,
            'traffic': traffic_metrics
        }
    
    async def _predict_warming_need(self, metrics: Dict[str, Any]) -> float:
        """**ML Engineer**: Prédiction besoin préchauffage via ML"""
        try:
            features = [
                metrics['time']['hour'],
                metrics['time']['day_week'],
                metrics['traffic']['current_load'],
                metrics['cache']['miss_rate'],
                metrics['traffic']['requests_per_second'] / 100.0,  # Normalized
                metrics['traffic']['concurrent_users']
            ]
            
            features_scaled = self.scaler.transform([features])
            probability = self.ml_model.predict(features_scaled)[0]
            
            return min(1.0, max(0.0, probability))
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction ML warming: {e}")
            return 0.0
    
    async def _check_threshold_triggers(self, metrics: Dict[str, Any]):
        """**Backend Senior**: Vérification seuils déclenchement"""
        triggers = self.config.get('triggers', {})
        
        # Seuil miss rate
        if metrics['cache']['miss_rate'] > triggers.get('cache_miss_threshold', 0.3):
            await self._create_threshold_warming_task(
                WarmingTrigger.CACHE_MISS_RATE,
                WarmingPriority.HIGH,
                f"Miss rate élevé: {metrics['cache']['miss_rate']:.2%}"
            )
        
        # Seuil traffic spike
        if metrics['traffic']['current_load'] > triggers.get('traffic_spike_threshold', 2.0):
            await self._create_threshold_warming_task(
                WarmingTrigger.TRAFFIC_SPIKE,
                WarmingPriority.CRITICAL,
                f"Pic de trafic: {metrics['traffic']['current_load']:.1f}x"
            )
    
    async def _create_predictive_warming_task(self, metrics: Dict[str, Any], probability: float):
        """**Lead Dev IA**: Création tâche préchauffage prédictive"""
        task_id = f"predictive_{int(time.time())}"
        
        # Sélection pattern et priorité basé sur métriques
        key_pattern = await self._select_optimal_warming_pattern(metrics)
        priority = WarmingPriority.HIGH if probability > 0.8 else WarmingPriority.MEDIUM
        
        warming_task = WarmingTask(
            task_id=task_id,
            key_pattern=key_pattern,
            data_source="predictive_analysis",
            strategy=WarmingStrategy.PREDICTIVE,
            priority=priority,
            trigger=WarmingTrigger.USER_BEHAVIOR,
            context={
                'probability': probability,
                'metrics': metrics,
                'prediction_time': time.time()
            }
        )
        
        await self._queue_warming_task(warming_task)
        logger.info(f"🤖 Tâche prédictive créée: {task_id} (prob: {probability:.2f})")
    
    async def _create_threshold_warming_task(self, trigger: WarmingTrigger, priority: WarmingPriority, reason: str):
        """**Backend Senior**: Création tâche warming seuil**"""
        task_id = f"threshold_{trigger.value}_{int(time.time())}"
        
        warming_task = WarmingTask(
            task_id=task_id,
            key_pattern="*:popular:*",  # Pattern populaire par défaut
            data_source="threshold_trigger",
            strategy=WarmingStrategy.ADAPTIVE,
            priority=priority,
            trigger=trigger,
            context={'reason': reason, 'trigger_time': time.time()}
        )
        
        await self._queue_warming_task(warming_task)
        logger.info(f"⚡ Tâche seuil créée: {task_id} - {reason}")
    
    async def _select_optimal_warming_pattern(self, metrics: Dict[str, Any]) -> str:
        """**Lead Dev IA**: Sélection pattern préchauffage optimal"""
        
        hour = metrics['time']['hour']
        day_week = metrics['time']['day_week']
        
        # Patterns spécialisés selon contexte temporel
        if 6 <= hour <= 10:  # Matin
            return "user:session:*"
        elif 11 <= hour <= 14:  # Midi
            return "content:trending:*"
        elif 17 <= hour <= 22:  # Soirée
            return "media:popular:*"
        elif day_week in [5, 6]:  # Weekend
            return "creator:content:*"
        else:
            return "*:cache:*"  # Pattern général
    
    async def _queue_warming_task(self, task: WarmingTask):
        """**Backend Senior**: Mise en file d'attente tâche warming"""
        self.warming_tasks[task.task_id] = task
        self.metrics.total_tasks += 1
        
        logger.debug(f"📝 Tâche warming ajoutée: {task.task_id}")
    
    async def _execute_pending_tasks(self):
        """**DevOps**: Exécution tâches en attente"""
        if len(self.active_warmings) >= self.config.get('max_concurrent_warmings', 5):
            return  # Limite concurrence
        
        # Tri par priorité
        pending_tasks = [
            task for task in self.warming_tasks.values()
            if task.task_id not in self.active_warmings and not task.executed_at
        ]
        
        # Tri par priorité et temps de création
        priority_order = {
            WarmingPriority.CRITICAL: 0,
            WarmingPriority.HIGH: 1,
            WarmingPriority.MEDIUM: 2,
            WarmingPriority.LOW: 3,
            WarmingPriority.BACKGROUND: 4
        }
        
        pending_tasks.sort(key=lambda t: (
            priority_order[t.priority],
            t.created_at
        ))
        
        # Exécution des tâches disponibles
        for task in pending_tasks[:self.config.get('max_concurrent_warmings', 5) - len(self.active_warmings)]:
            asyncio.create_task(self._execute_warming_task(task))
    
    async def _execute_warming_task(self, task: WarmingTask):
        """**Backend Senior**: Exécution tâche préchauffage"""
        task_id = task.task_id
        self.active_warmings.add(task_id)
        
        start_time = time.time()
        
        try:
            logger.info(f"🔥 Exécution warming: {task_id} ({task.strategy.value})")
            
            # Récupération données à préchauffer
            data_to_warm = await self._get_warming_data(task)
            
            if not data_to_warm:
                logger.warning(f"⚠️ Aucune donnée à préchauffer: {task_id}")
                task.success = False
                return
            
            # Préchauffage effectif
            warmed_keys = []
            
            for key, value in data_to_warm.items():
                try:
                    # Utilisation cache policy engine si disponible
                    if self.cache_policy_engine:
                        success = await self.cache_policy_engine.set_cache(
                            key, value, 
                            policy_name="media_content",  # Politique optimisée
                            context={'warming_task': task_id, 'strategy': task.strategy.value}
                        )
                    else:
                        # Fallback Redis direct
                        async with self.redis_pool.get_connection() as redis_conn:
                            ttl = task.ttl_seconds or self.config.get('default_ttl', 3600)
                            success = await redis_conn.setex(key, ttl, json.dumps(value))
                    
                    if success:
                        warmed_keys.append(key)
                        
                except Exception as e:
                    logger.error(f"❌ Erreur warming clé {key}: {e}")
            
            # Mise à jour résultat
            task.executed_at = datetime.now(timezone.utc)
            task.success = len(warmed_keys) > 0
            task.execution_time_ms = (time.time() - start_time) * 1000
            task.warmed_keys = warmed_keys
            
            # Mise à jour métriques
            if task.success:
                self.metrics.successful_tasks += 1
                self.metrics.total_keys_warmed += len(warmed_keys)
            else:
                self.metrics.failed_tasks += 1
            
            # Mise à jour temps exécution moyen
            if self.metrics.successful_tasks > 0:
                self.metrics.average_execution_time = (
                    self.metrics.average_execution_time * (self.metrics.successful_tasks - 1) +
                    task.execution_time_ms
                ) / self.metrics.successful_tasks
            
            self.metrics.last_warming_time = time.time()
            
            # Historique
            self.warming_history.append({
                'task_id': task_id,
                'strategy': task.strategy.value,
                'success': task.success,
                'keys_warmed': len(warmed_keys),
                'execution_time': task.execution_time_ms,
                'timestamp': task.executed_at.timestamp()
            })
            
            logger.info(f"✅ Warming terminé: {task_id} - {len(warmed_keys)} clés")
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution warming {task_id}: {e}")
            task.success = False
            task.executed_at = datetime.now(timezone.utc)
            self.metrics.failed_tasks += 1
            
        finally:
            self.active_warmings.discard(task_id)
    
    async def _get_warming_data(self, task: WarmingTask) -> Dict[str, Any]:
        """**Backend Senior**: Récupération données à préchauffer"""
        
        # Utilisation source configurée si disponible
        if task.data_source in self.data_sources:
            try:
                return await self.data_sources[task.data_source](task)
            except Exception as e:
                logger.error(f"❌ Erreur source données {task.data_source}: {e}")
        
        # Sources par défaut selon stratégie
        if task.strategy == WarmingStrategy.PREDICTIVE:
            return await self._get_predictive_data(task)
        elif task.strategy == WarmingStrategy.POPULARITY_BASED:
            return await self._get_popular_data(task)
        elif task.strategy == WarmingStrategy.TIME_BASED:
            return await self._get_time_based_data(task)
        else:
            return await self._get_default_warming_data(task)
    
    async def _get_predictive_data(self, task: WarmingTask) -> Dict[str, Any]:
        """**ML Engineer**: Génération données prédictives"""
        # Simulation données prédictives basées contexte
        warming_data = {}
        
        batch_size = self.config.get('warming_batch_size', 100)
        
        for i in range(batch_size):
            key = f"predictive:{task.task_id}:{i}"
            value = {
                'type': 'predictive_content',
                'probability': task.context.get('probability', 0.5),
                'generated_at': time.time(),
                'context': task.context.get('metrics', {})
            }
            warming_data[key] = value
        
        return warming_data
    
    async def _get_popular_data(self, task: WarmingTask) -> Dict[str, Any]:
        """**Backend Senior**: Génération données populaires"""
        # Simulation contenu populaire
        warming_data = {}
        
        popular_items = [
            f"media:video:{i}" for i in range(1, 51)  # 50 vidéos populaires
        ]
        
        for item_key in popular_items:
            value = {
                'type': 'popular_content',
                'popularity_score': np.random.uniform(0.7, 1.0),
                'views': np.random.randint(1000, 100000),
                'cached_at': time.time()
            }
            warming_data[item_key] = value
        
        return warming_data
    
    async def _get_time_based_data(self, task: WarmingTask) -> Dict[str, Any]:
        """**DevOps**: Génération données basées temporelles"""
        current_hour = datetime.now().hour
        warming_data = {}
        
        # Contenu spécialisé selon l'heure
        if 6 <= current_hour <= 10:  # Matin - sessions utilisateur
            for i in range(50):
                key = f"user:session:{1000 + i}"
                value = {
                    'type': 'user_session',
                    'hour_context': 'morning',
                    'expected_activity': 'high',
                    'cached_at': time.time()
                }
                warming_data[key] = value
        
        elif 17 <= current_hour <= 22:  # Soirée - contenu média
            for i in range(100):
                key = f"media:evening:{i}"
                value = {
                    'type': 'evening_content',
                    'hour_context': 'evening',
                    'content_type': 'entertainment',
                    'cached_at': time.time()
                }
                warming_data[key] = value
        
        return warming_data
    
    async def _get_default_warming_data(self, task: WarmingTask) -> Dict[str, Any]:
        """**Backend Senior**: Génération données par défaut"""
        warming_data = {}
        
        # Pattern basé sur key_pattern de la tâche
        base_keys = [
            f"default:{task.task_id}:{i}" 
            for i in range(self.config.get('warming_batch_size', 50))
        ]
        
        for key in base_keys:
            value = {
                'type': 'default_warming',
                'pattern': task.key_pattern,
                'strategy': task.strategy.value,
                'cached_at': time.time()
            }
            warming_data[key] = value
        
        return warming_data
    
    def register_data_source(self, source_name: str, source_function: Callable):
        """**Lead Dev IA**: Enregistrement source données personnalisée"""
        self.data_sources[source_name] = source_function
        logger.info(f"📊 Source données enregistrée: {source_name}")
    
    async def create_manual_warming_task(
        self,
        key_pattern: str,
        data_source: str,
        priority: WarmingPriority = WarmingPriority.MEDIUM,
        strategy: WarmingStrategy = WarmingStrategy.ADAPTIVE,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """**DevOps**: Création tâche warming manuelle"""
        
        task_id = f"manual_{int(time.time())}"
        
        warming_task = WarmingTask(
            task_id=task_id,
            key_pattern=key_pattern,
            data_source=data_source,
            strategy=strategy,
            priority=priority,
            trigger=WarmingTrigger.MANUAL,
            context=context or {}
        )
        
        await self._queue_warming_task(warming_task)
        
        logger.info(f"📝 Tâche warming manuelle créée: {task_id}")
        return task_id
    
    async def _cleanup_completed_tasks(self):
        """**DevOps**: Nettoyage tâches terminées"""
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(hours=24)  # Garder 24h
        
        completed_tasks = [
            task_id for task_id, task in self.warming_tasks.items()
            if task.executed_at and task.executed_at < cutoff_time
        ]
        
        for task_id in completed_tasks:
            del self.warming_tasks[task_id]
        
        if completed_tasks:
            logger.debug(f"🧹 {len(completed_tasks)} tâches nettoyées")
    
    async def get_warming_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics détaillées préchauffage"""
        
        active_tasks = len([t for t in self.warming_tasks.values() if not t.executed_at])
        completed_tasks = len([t for t in self.warming_tasks.values() if t.executed_at])
        
        # Performance par stratégie
        strategy_stats = defaultdict(lambda: {'count': 0, 'success': 0, 'avg_time': 0})
        
        for record in self.warming_history:
            strategy = record['strategy']
            strategy_stats[strategy]['count'] += 1
            if record['success']:
                strategy_stats[strategy]['success'] += 1
            strategy_stats[strategy]['avg_time'] += record['execution_time']
        
        # Finalisation stats
        for strategy, stats in strategy_stats.items():
            if stats['count'] > 0:
                stats['success_rate'] = stats['success'] / stats['count']
                stats['avg_time'] /= stats['count']
            else:
                stats['success_rate'] = 0
        
        return {
            'global_metrics': {
                'total_tasks': self.metrics.total_tasks,
                'successful_tasks': self.metrics.successful_tasks,
                'failed_tasks': self.metrics.failed_tasks,
                'success_rate': self.metrics.successful_tasks / max(1, self.metrics.total_tasks),
                'total_keys_warmed': self.metrics.total_keys_warmed,
                'average_execution_time': self.metrics.average_execution_time,
                'last_warming_time': self.metrics.last_warming_time
            },
            'current_state': {
                'scheduler_running': self.scheduler_running,
                'active_warmings': len(self.active_warmings),
                'pending_tasks': active_tasks,
                'completed_tasks': completed_tasks,
                'scheduled_tasks': len(self.scheduled_tasks)
            },
            'strategy_performance': dict(strategy_stats),
            'recent_history': list(self.warming_history)[-10:],  # 10 derniers
            'configuration': {
                'warming_enabled': self.config.get('warming_enabled'),
                'ml_enabled': self.config.get('ml_enabled'),
                'max_concurrent': self.config.get('max_concurrent_warmings'),
                'batch_size': self.config.get('warming_batch_size')
            }
        }

# Factory function
async def create_cache_warming_scheduler(
    redis_pool, 
    cache_policy_engine=None, 
    config: Optional[Dict[str, Any]] = None
):
    """**Lead Dev IA**: Factory création planificateur warming"""
    scheduler = CacheWarmingScheduler(redis_pool, cache_policy_engine, config)
    
    if config and config.get('ml_enabled', True):
        await scheduler.initialize_ml_model()
    
    return scheduler

if __name__ == "__main__":
    async def demo():
        """Démonstration Cache Warming Scheduler"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                mock = AsyncMock()
                mock.setex.return_value = True
                return mock
        
        # Création scheduler
        scheduler = await create_cache_warming_scheduler(MockRedisPool())
        
        # Démarrage planificateur
        await scheduler.start_scheduler()
        
        # Création tâche manuelle
        task_id = await scheduler.create_manual_warming_task(
            key_pattern="demo:*",
            data_source="demo_source",
            priority=WarmingPriority.HIGH
        )
        
        print(f"Tâche créée: {task_id}")
        
        # Attente exécution
        await asyncio.sleep(5)
        
        # Analytics
        analytics = await scheduler.get_warming_analytics()
        print(f"Analytics warming: {analytics}")
        
        # Arrêt
        await scheduler.stop_scheduler()
    
    asyncio.run(demo())