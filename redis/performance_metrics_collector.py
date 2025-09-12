#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Performance Metrics Collector - Monitoring Redis Enterprise
==============================================================

Collecteur de métriques performance Redis avec analytics temps réel,
détection d'anomalies et optimisation automatique.

**Rôles Experts:**
- **DevOps**: Monitoring opérationnel et métriques infrastructure
- **Backend Senior**: Performance monitoring et optimisation système
- **ML Engineer**: Analytics prédictives et détection anomalies
- **DBA**: Métriques base de données et optimisation requêtes

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import psutil
import json
import statistics
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import aioredis

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques Redis"""
    COUNTER = "counter"  # Compteur croissant
    GAUGE = "gauge"  # Valeur instantanée
    HISTOGRAM = "histogram"  # Distribution valeurs
    TIMER = "timer"  # Durée opérations

class AlertSeverity(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class PerformanceCategory(Enum):
    """Catégories de performance"""
    MEMORY = "memory"
    CPU = "cpu"
    NETWORK = "network"
    DISK = "disk"
    REDIS_OPERATIONS = "redis_operations"
    CACHE_EFFICIENCY = "cache_efficiency"
    CLIENT_CONNECTIONS = "client_connections"

@dataclass
class MetricPoint:
    """Point de métrique temporel"""
    timestamp: float
    value: float
    metric_name: str
    labels: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class PerformanceAlert:
    """Alerte de performance"""
    alert_id: str
    severity: AlertSeverity
    metric_name: str
    current_value: float
    threshold: float
    message: str
    timestamp: float = field(default_factory=time.time)
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class PerformanceThreshold:
    """Seuil de performance"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    emergency_threshold: Optional[float] = None
    direction: str = "above"  # "above" ou "below"
    window_minutes: int = 5  # Fenêtre d'évaluation

class PerformanceMetricsCollector:
    """
    📊 Collecteur de Métriques Performance Redis Enterprise
    
    **DevOps Expert:**
    - Monitoring temps réel infrastructure Redis complete
    - Alertes proactives et escalation automatique
    - Dashboard opérationnel avec métriques business
    - SLA tracking et reporting automatisé
    
    **Backend Senior:**
    - Monitoring performance micro-optimisations
    - Analyse goulots d'étranglement temps réel
    - Profiling opérations Redis avancé
    - Optimisation automatique based on metrics
    
    **ML Engineer:**
    - Détection d'anomalies avec machine learning
    - Prédiction tendances et capacity planning
    - Clustering patterns d'utilisation anormaux
    - Analytics prédictives pour maintenance
    
    **DBA:**
    - Métriques base de données spécialisées
    - Analyse performance requêtes détaillée
    - Monitoring intégrité et consistency
    - Optimisation index et structures données
    """
    
    def __init__(self, redis_pool, config: Optional[Dict[str, Any]] = None):
        self.redis_pool = redis_pool
        self.config = config or {}
        
        # Configuration collecte
        self.collection_interval = self.config.get('collection_interval', 30)  # secondes
        self.retention_hours = self.config.get('retention_hours', 24)
        self.enable_ml_analytics = self.config.get('enable_ml_analytics', True)
        
        # Stockage métriques en mémoire
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.current_metrics: Dict[str, float] = {}
        
        # Alertes et seuils
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        self.alert_history: deque = deque(maxlen=1000)
        
        # ML pour détection d'anomalies
        self.anomaly_detector: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        
        # Statistiques de performance
        self.performance_stats = {
            "total_metrics_collected": 0,
            "alerts_generated": 0,
            "anomalies_detected": 0,
            "collection_errors": 0
        }
        
        # Baseline performance
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}
        
        # Initialisation
        self._setup_default_thresholds()
        asyncio.create_task(self._initialize_ml_models())
        asyncio.create_task(self._start_collection_loop())
        asyncio.create_task(self._start_analysis_loop())
        
        logger.info(f"📊 Performance Metrics Collector initialisé (intervalle: {self.collection_interval}s)")
    
    def _setup_default_thresholds(self):
        """**DevOps**: Configuration seuils par défaut"""
        
        default_thresholds = [
            # Métriques mémoire
            PerformanceThreshold("memory_usage_percent", 80.0, 90.0, 95.0),
            PerformanceThreshold("memory_fragmentation_ratio", 1.5, 2.0, 3.0),
            
            # Métriques CPU
            PerformanceThreshold("cpu_usage_percent", 70.0, 85.0, 95.0),
            
            # Métriques réseau
            PerformanceThreshold("network_latency_ms", 10.0, 50.0, 100.0),
            PerformanceThreshold("network_errors_per_sec", 1.0, 5.0, 10.0),
            
            # Métriques Redis
            PerformanceThreshold("redis_commands_per_sec", 1000.0, 5000.0, 10000.0),
            PerformanceThreshold("redis_slow_queries_per_min", 1.0, 5.0, 10.0),
            PerformanceThreshold("cache_hit_ratio", 90.0, 80.0, 70.0, "below"),
            
            # Métriques clients
            PerformanceThreshold("connected_clients", 100.0, 500.0, 1000.0),
            PerformanceThreshold("blocked_clients", 1.0, 5.0, 10.0),
            
            # Métriques disque
            PerformanceThreshold("disk_usage_percent", 80.0, 90.0, 95.0),
            PerformanceThreshold("disk_io_wait_percent", 10.0, 20.0, 30.0)
        ]
        
        for threshold in default_thresholds:
            self.thresholds[threshold.metric_name] = threshold
    
    async def _initialize_ml_models(self):
        """**ML Engineer**: Initialisation modèles ML pour analytics"""
        try:
            if not self.enable_ml_analytics:
                return
            
            # Détecteur d'anomalies
            self.anomaly_detector = IsolationForest(
                contamination=0.1,  # 10% des données sont des anomalies
                random_state=42,
                n_jobs=-1
            )
            
            # Scaler pour normalisation
            self.scaler = StandardScaler()
            
            # Features pour détection d'anomalies
            self.feature_names = [
                "memory_usage_percent",
                "cpu_usage_percent", 
                "redis_commands_per_sec",
                "cache_hit_ratio",
                "connected_clients",
                "network_latency_ms",
                "memory_fragmentation_ratio"
            ]
            
            logger.info("✅ Modèles ML métriques initialisés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation ML: {e}")
    
    async def _start_collection_loop(self):
        """**DevOps**: Démarrage boucle collecte métriques"""
        asyncio.create_task(self._metrics_collection_loop())
        asyncio.create_task(self._system_metrics_loop())
        logger.info("📈 Collecte métriques démarrée")
    
    async def _start_analysis_loop(self):
        """**ML Engineer**: Démarrage boucle analyse ML"""
        asyncio.create_task(self._anomaly_detection_loop())
        asyncio.create_task(self._trend_analysis_loop())
        asyncio.create_task(self._alert_management_loop())
        logger.info("🔍 Analyse ML démarrée")
    
    async def _metrics_collection_loop(self):
        """**Backend Senior**: Boucle collecte métriques Redis"""
        while True:
            try:
                await asyncio.sleep(self.collection_interval)
                
                # Collecte métriques Redis
                redis_metrics = await self._collect_redis_metrics()
                if redis_metrics:
                    await self._process_metrics(redis_metrics)
                
                self.performance_stats["total_metrics_collected"] += len(redis_metrics) if redis_metrics else 0
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur collecte métriques Redis: {e}")
                self.performance_stats["collection_errors"] += 1
    
    async def _system_metrics_loop(self):
        """**DevOps**: Boucle collecte métriques système"""
        while True:
            try:
                await asyncio.sleep(self.collection_interval)
                
                # Collecte métriques système
                system_metrics = await self._collect_system_metrics()
                if system_metrics:
                    await self._process_metrics(system_metrics)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur collecte métriques système: {e}")
    
    async def _collect_redis_metrics(self) -> Optional[Dict[str, float]]:
        """**DBA**: Collecte métriques Redis détaillées"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                # Info Redis complet
                info_memory = await redis_conn.info('memory')
                info_stats = await redis_conn.info('stats')
                info_clients = await redis_conn.info('clients')
                info_server = await redis_conn.info('server')
                info_cpu = await redis_conn.info('cpu')
                
                # Métriques calculées
                used_memory = info_memory.get('used_memory', 0)
                maxmemory = info_memory.get('maxmemory', 0)
                memory_usage_percent = (used_memory / maxmemory * 100) if maxmemory > 0 else 0
                
                keyspace_hits = info_stats.get('keyspace_hits', 0)
                keyspace_misses = info_stats.get('keyspace_misses', 0)
                total_commands = keyspace_hits + keyspace_misses
                cache_hit_ratio = (keyspace_hits / total_commands * 100) if total_commands > 0 else 0
                
                # Latence Redis (mesurée)
                latency_start = time.time()
                await redis_conn.ping()
                redis_latency_ms = (time.time() - latency_start) * 1000
                
                metrics = {
                    # Métriques mémoire
                    "memory_usage_bytes": used_memory,
                    "memory_usage_percent": memory_usage_percent,
                    "memory_rss_bytes": info_memory.get('used_memory_rss', 0),
                    "memory_peak_bytes": info_memory.get('used_memory_peak', 0),
                    "memory_fragmentation_ratio": info_memory.get('mem_fragmentation_ratio', 1.0),
                    "memory_lua_bytes": info_memory.get('used_memory_lua', 0),
                    
                    # Métriques opérations
                    "total_commands_processed": info_stats.get('total_commands_processed', 0),
                    "instantaneous_ops_per_sec": info_stats.get('instantaneous_ops_per_sec', 0),
                    "redis_commands_per_sec": info_stats.get('instantaneous_ops_per_sec', 0),
                    
                    # Métriques cache
                    "keyspace_hits": keyspace_hits,
                    "keyspace_misses": keyspace_misses,
                    "cache_hit_ratio": cache_hit_ratio,
                    "evicted_keys": info_stats.get('evicted_keys', 0),
                    "expired_keys": info_stats.get('expired_keys', 0),
                    
                    # Métriques clients
                    "connected_clients": info_clients.get('connected_clients', 0),
                    "blocked_clients": info_clients.get('blocked_clients', 0),
                    "client_recent_max_input_buffer": info_clients.get('client_recent_max_input_buffer', 0),
                    "client_recent_max_output_buffer": info_clients.get('client_recent_max_output_buffer', 0),
                    
                    # Métriques réseau
                    "total_net_input_bytes": info_stats.get('total_net_input_bytes', 0),
                    "total_net_output_bytes": info_stats.get('total_net_output_bytes', 0),
                    "instantaneous_input_kbps": info_stats.get('instantaneous_input_kbps', 0),
                    "instantaneous_output_kbps": info_stats.get('instantaneous_output_kbps', 0),
                    "network_latency_ms": redis_latency_ms,
                    
                    # Métriques CPU
                    "used_cpu_sys": info_cpu.get('used_cpu_sys', 0),
                    "used_cpu_user": info_cpu.get('used_cpu_user', 0),
                    "used_cpu_sys_children": info_cpu.get('used_cpu_sys_children', 0),
                    "used_cpu_user_children": info_cpu.get('used_cpu_user_children', 0),
                    
                    # Métriques persistance
                    "rdb_changes_since_last_save": info_stats.get('rdb_changes_since_last_save', 0),
                    "rdb_last_save_time": info_stats.get('rdb_last_save_time', 0),
                    
                    # Métriques uptime
                    "uptime_in_seconds": info_server.get('uptime_in_seconds', 0),
                    "uptime_in_days": info_server.get('uptime_in_days', 0)
                }
                
                return metrics
                
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques Redis: {e}")
            return None
    
    async def _collect_system_metrics(self) -> Optional[Dict[str, float]]:
        """**DevOps**: Collecte métriques système détaillées"""
        try:
            # Métriques CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            # Métriques mémoire système
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Métriques disque
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Métriques réseau
            network_io = psutil.net_io_counters()
            
            # Métriques processus
            process_count = len(psutil.pids())
            
            metrics = {
                # CPU
                "system_cpu_usage_percent": cpu_percent,
                "system_cpu_count": cpu_count,
                "system_load_avg_1m": load_avg[0],
                "system_load_avg_5m": load_avg[1],
                "system_load_avg_15m": load_avg[2],
                
                # Mémoire
                "system_memory_total_bytes": memory.total,
                "system_memory_used_bytes": memory.used,
                "system_memory_usage_percent": memory.percent,
                "system_memory_available_bytes": memory.available,
                "system_swap_usage_percent": swap.percent,
                
                # Disque
                "system_disk_total_bytes": disk_usage.total,
                "system_disk_used_bytes": disk_usage.used,
                "system_disk_usage_percent": disk_usage.percent,
                "system_disk_free_bytes": disk_usage.free,
                
                # I/O Disque
                "system_disk_read_bytes": disk_io.read_bytes if disk_io else 0,
                "system_disk_write_bytes": disk_io.write_bytes if disk_io else 0,
                "system_disk_read_count": disk_io.read_count if disk_io else 0,
                "system_disk_write_count": disk_io.write_count if disk_io else 0,
                
                # Réseau
                "system_network_bytes_sent": network_io.bytes_sent,
                "system_network_bytes_recv": network_io.bytes_recv,
                "system_network_packets_sent": network_io.packets_sent,
                "system_network_packets_recv": network_io.packets_recv,
                "system_network_errors_in": network_io.errin,
                "system_network_errors_out": network_io.errout,
                
                # Processus
                "system_process_count": process_count
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques système: {e}")
            return None
    
    async def _process_metrics(self, metrics: Dict[str, float]):
        """**Backend Senior**: Traitement et stockage métriques"""
        current_time = time.time()
        
        for metric_name, value in metrics.items():
            # Création point métrique
            metric_point = MetricPoint(
                timestamp=current_time,
                value=value,
                metric_name=metric_name
            )
            
            # Stockage buffer mémoire
            self.metrics_buffer[metric_name].append(metric_point)
            self.current_metrics[metric_name] = value
            
            # Vérification seuils d'alerte
            await self._check_metric_threshold(metric_name, value, current_time)
        
        # Persistance Redis pour historique
        await self._persist_metrics_redis(metrics, current_time)
    
    async def _check_metric_threshold(self, metric_name: str, value: float, timestamp: float):
        """**DevOps**: Vérification seuils avec génération alertes"""
        threshold = self.thresholds.get(metric_name)
        if not threshold:
            return
        
        severity = None
        exceeded_threshold = None
        
        # Détermination seuil dépassé
        if threshold.direction == "above":
            if threshold.emergency_threshold and value >= threshold.emergency_threshold:
                severity = AlertSeverity.EMERGENCY
                exceeded_threshold = threshold.emergency_threshold
            elif value >= threshold.critical_threshold:
                severity = AlertSeverity.CRITICAL
                exceeded_threshold = threshold.critical_threshold
            elif value >= threshold.warning_threshold:
                severity = AlertSeverity.WARNING
                exceeded_threshold = threshold.warning_threshold
        else:  # "below"
            if threshold.emergency_threshold and value <= threshold.emergency_threshold:
                severity = AlertSeverity.EMERGENCY
                exceeded_threshold = threshold.emergency_threshold
            elif value <= threshold.critical_threshold:
                severity = AlertSeverity.CRITICAL
                exceeded_threshold = threshold.critical_threshold
            elif value <= threshold.warning_threshold:
                severity = AlertSeverity.WARNING
                exceeded_threshold = threshold.warning_threshold
        
        # Génération alerte si seuil dépassé
        if severity:
            alert_id = f"{metric_name}_{severity.value}_{int(timestamp)}"
            
            # Éviter doublons d'alertes
            existing_alert = None
            for alert in self.active_alerts.values():
                if (alert.metric_name == metric_name and 
                    alert.severity == severity and 
                    not alert.resolved and
                    timestamp - alert.timestamp < 300):  # 5 minutes
                    existing_alert = alert
                    break
            
            if not existing_alert:
                alert = PerformanceAlert(
                    alert_id=alert_id,
                    severity=severity,
                    metric_name=metric_name,
                    current_value=value,
                    threshold=exceeded_threshold,
                    message=f"{metric_name} {threshold.direction} threshold: {value:.2f} > {exceeded_threshold}",
                    timestamp=timestamp
                )
                
                self.active_alerts[alert_id] = alert
                self.alert_history.append(alert)
                self.performance_stats["alerts_generated"] += 1
                
                # Log selon sévérité
                if severity == AlertSeverity.EMERGENCY:
                    logger.critical(f"🚨 {alert.message}")
                elif severity == AlertSeverity.CRITICAL:
                    logger.error(f"❌ {alert.message}")
                elif severity == AlertSeverity.WARNING:
                    logger.warning(f"⚠️ {alert.message}")
                
                # Notification externe (webhook, email, etc.)
                await self._send_alert_notification(alert)
    
    async def _send_alert_notification(self, alert: PerformanceAlert):
        """**DevOps**: Envoi notifications alertes externes"""
        try:
            # Persistance alerte Redis pour traitement externe
            async with self.redis_pool.get_connection() as redis_conn:
                alert_data = {
                    "alert_id": alert.alert_id,
                    "severity": alert.severity.value,
                    "metric_name": alert.metric_name,
                    "current_value": alert.current_value,
                    "threshold": alert.threshold,
                    "message": alert.message,
                    "timestamp": alert.timestamp
                }
                
                # Queue alertes pour traitement externe
                await redis_conn.lpush("performance_alerts", json.dumps(alert_data))
                await redis_conn.expire("performance_alerts", 86400)  # 24h
                
                # Index alertes par sévérité
                await redis_conn.sadd(f"alerts_{alert.severity.value}", alert.alert_id)
                
        except Exception as e:
            logger.error(f"❌ Erreur envoi notification alerte: {e}")
    
    async def _persist_metrics_redis(self, metrics: Dict[str, float], timestamp: float):
        """**DBA**: Persistance métriques Redis avec compression temporelle"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                # Timestamp formaté pour indexation
                time_key = int(timestamp // 60) * 60  # Arrondi à la minute
                
                # Stockage batch efficient
                pipeline = redis_conn.pipeline()
                
                for metric_name, value in metrics.items():
                    # Clé time-series
                    ts_key = f"metrics:{metric_name}:{time_key}"
                    
                    # Stockage avec TTL basé sur rétention
                    ttl = self.retention_hours * 3600
                    pipeline.setex(ts_key, ttl, value)
                    
                    # Index métrique pour requêtes
                    pipeline.sadd("metric_names", metric_name)
                    pipeline.zadd(f"metric_timeline:{metric_name}", {time_key: value})
                    pipeline.expire(f"metric_timeline:{metric_name}", ttl)
                
                await pipeline.execute()
                
        except Exception as e:
            logger.error(f"❌ Erreur persistance métriques: {e}")
    
    async def _anomaly_detection_loop(self):
        """**ML Engineer**: Boucle détection d'anomalies ML"""
        while True:
            try:
                await asyncio.sleep(300)  # Analyse toutes les 5 minutes
                
                if self.enable_ml_analytics and len(self.metrics_buffer) > 100:
                    await self._detect_anomalies()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur détection d'anomalies: {e}")
    
    async def _detect_anomalies(self):
        """**ML Engineer**: Détection d'anomalies avec Machine Learning"""
        try:
            # Préparation données pour ML
            features_matrix = []
            timestamps = []
            
            # Collecte features sur fenêtre récente
            min_samples = min(len(self.metrics_buffer[name]) for name in self.feature_names 
                             if name in self.metrics_buffer)
            
            if min_samples < 50:  # Besoin minimum 50 échantillons
                return
            
            for i in range(min_samples):
                feature_vector = []
                valid_sample = True
                
                for feature_name in self.feature_names:
                    if feature_name in self.metrics_buffer:
                        buffer = list(self.metrics_buffer[feature_name])
                        if i < len(buffer):
                            metric_point = buffer[-(i+1)]  # Depuis le plus récent
                            feature_vector.append(metric_point.value)
                            if i == 0:  # Premier échantillon = plus récent
                                timestamps.append(metric_point.timestamp)
                        else:
                            valid_sample = False
                            break
                    else:
                        valid_sample = False
                        break
                
                if valid_sample and len(feature_vector) == len(self.feature_names):
                    features_matrix.append(feature_vector)
            
            if len(features_matrix) < 50:
                return
            
            # Préparation et normalisation
            features_array = np.array(features_matrix)
            
            # Entraînement/mise à jour modèle si nécessaire
            if self.anomaly_detector is None:
                await self._initialize_ml_models()
            
            # Normalisation
            features_scaled = self.scaler.fit_transform(features_array)
            
            # Entraînement sur données récentes
            self.anomaly_detector.fit(features_scaled)
            
            # Prédiction anomalies
            anomaly_scores = self.anomaly_detector.decision_function(features_scaled)
            anomalies = self.anomaly_detector.predict(features_scaled)
            
            # Traitement anomalies détectées
            for i, (is_anomaly, score) in enumerate(zip(anomalies, anomaly_scores)):
                if is_anomaly == -1:  # Anomalie détectée
                    timestamp = timestamps[i] if i < len(timestamps) else time.time()
                    
                    # Génération alerte anomalie
                    await self._generate_anomaly_alert(
                        timestamp, score, features_matrix[i]
                    )
            
            anomaly_count = sum(1 for a in anomalies if a == -1)
            if anomaly_count > 0:
                self.performance_stats["anomalies_detected"] += anomaly_count
                logger.info(f"🔍 {anomaly_count} anomalies détectées")
            
        except Exception as e:
            logger.error(f"❌ Erreur détection anomalies ML: {e}")
    
    async def _generate_anomaly_alert(self, timestamp: float, anomaly_score: float, features: List[float]):
        """**ML Engineer**: Génération alerte anomalie ML"""
        try:
            # Analyse features pour identifier cause
            feature_analysis = {}
            for i, feature_name in enumerate(self.feature_names):
                if i < len(features):
                    feature_analysis[feature_name] = features[i]
            
            # Sévérité basée sur score anomalie
            if anomaly_score < -0.5:
                severity = AlertSeverity.CRITICAL
            elif anomaly_score < -0.3:
                severity = AlertSeverity.WARNING
            else:
                severity = AlertSeverity.INFO
            
            alert_id = f"anomaly_{int(timestamp)}_{abs(hash(str(features)))}"
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                severity=severity,
                metric_name="ml_anomaly_detection",
                current_value=anomaly_score,
                threshold=-0.3,
                message=f"Anomalie ML détectée (score: {anomaly_score:.3f})",
                timestamp=timestamp
            )
            
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Log détaillé
            logger.warning(f"🤖 Anomalie ML: score={anomaly_score:.3f}, features={feature_analysis}")
            
            # Notification avec contexte
            await self._send_alert_notification(alert)
            
        except Exception as e:
            logger.error(f"❌ Erreur génération alerte anomalie: {e}")
    
    async def _trend_analysis_loop(self):
        """**ML Engineer**: Boucle analyse tendances prédictives"""
        while True:
            try:
                await asyncio.sleep(900)  # Analyse toutes les 15 minutes
                
                await self._analyze_performance_trends()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur analyse tendances: {e}")
    
    async def _analyze_performance_trends(self):
        """**ML Engineer**: Analyse tendances avec prédictions"""
        try:
            # Analyse pour métriques clés
            key_metrics = [
                "memory_usage_percent",
                "cpu_usage_percent",
                "redis_commands_per_sec",
                "cache_hit_ratio"
            ]
            
            trend_results = {}
            
            for metric_name in key_metrics:
                if metric_name not in self.metrics_buffer:
                    continue
                
                buffer = list(self.metrics_buffer[metric_name])
                if len(buffer) < 20:  # Minimum pour analyse tendance
                    continue
                
                # Extraction série temporelle
                values = [point.value for point in buffer[-100:]]  # 100 derniers points
                timestamps = [point.timestamp for point in buffer[-100:]]
                
                if len(values) < 10:
                    continue
                
                # Calcul tendance (régression linéaire simple)
                x = np.arange(len(values))
                slope, intercept = np.polyfit(x, values, 1)
                
                # Prédiction prochaine heure (basée sur intervalle collecte)
                future_points = 3600 // self.collection_interval  # Points pour 1 heure
                predicted_value = slope * (len(values) + future_points) + intercept
                
                # Détection tendances critiques
                current_value = values[-1]
                trend_severity = None
                
                if metric_name in ["memory_usage_percent", "cpu_usage_percent"]:
                    # Tendance croissante critique pour usage ressources
                    if slope > 0.1 and predicted_value > 90:
                        trend_severity = "critical_increase"
                elif metric_name == "cache_hit_ratio":
                    # Tendance décroissante critique pour hit ratio
                    if slope < -0.1 and predicted_value < 80:
                        trend_severity = "critical_decrease"
                elif metric_name == "redis_commands_per_sec":
                    # Augmentation charge excessive
                    if slope > 10 and predicted_value > 5000:
                        trend_severity = "high_load_trend"
                
                trend_results[metric_name] = {
                    "current_value": current_value,
                    "slope": slope,
                    "predicted_1h": predicted_value,
                    "trend_severity": trend_severity,
                    "confidence": min(0.8, len(values) / 100)  # Confiance basée sur échantillons
                }
                
                # Génération alerte si tendance critique
                if trend_severity:
                    await self._generate_trend_alert(metric_name, trend_results[metric_name])
            
            # Stockage résultats analyse
            self.performance_stats["last_trend_analysis"] = {
                "timestamp": time.time(),
                "results": trend_results
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse tendances: {e}")
    
    async def _generate_trend_alert(self, metric_name: str, trend_data: Dict[str, Any]):
        """**ML Engineer**: Génération alerte tendance prédictive"""
        try:
            severity = AlertSeverity.WARNING
            if "critical" in trend_data["trend_severity"]:
                severity = AlertSeverity.CRITICAL
            
            alert_id = f"trend_{metric_name}_{int(time.time())}"
            
            message = (
                f"Tendance critique {metric_name}: "
                f"actuel={trend_data['current_value']:.2f}, "
                f"prédit 1h={trend_data['predicted_1h']:.2f} "
                f"(confiance: {trend_data['confidence']:.1%})"
            )
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                severity=severity,
                metric_name=f"trend_{metric_name}",
                current_value=trend_data["current_value"],
                threshold=trend_data["predicted_1h"],
                message=message
            )
            
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            logger.warning(f"📈 {message}")
            await self._send_alert_notification(alert)
            
        except Exception as e:
            logger.error(f"❌ Erreur alerte tendance: {e}")
    
    async def _alert_management_loop(self):
        """**DevOps**: Boucle gestion alertes et résolution automatique"""
        while True:
            try:
                await asyncio.sleep(60)  # Vérification chaque minute
                
                await self._auto_resolve_alerts()
                await self._cleanup_old_alerts()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur gestion alertes: {e}")
    
    async def _auto_resolve_alerts(self):
        """**DevOps**: Résolution automatique alertes"""
        current_time = time.time()
        
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.resolved:
                continue
            
            # Vérification si métrique revenue normale
            current_value = self.current_metrics.get(alert.metric_name)
            if current_value is None:
                continue
            
            threshold_config = self.thresholds.get(alert.metric_name)
            if not threshold_config:
                continue
            
            # Logique résolution basée sur seuil
            should_resolve = False
            
            if threshold_config.direction == "above":
                if current_value < threshold_config.warning_threshold:
                    should_resolve = True
            else:  # "below"
                if current_value > threshold_config.warning_threshold:
                    should_resolve = True
            
            # Résolution si stable depuis 5 minutes
            if (should_resolve and 
                current_time - alert.timestamp > 300 and
                alert.severity != AlertSeverity.EMERGENCY):
                
                alert.resolved = True
                logger.info(f"✅ Alerte auto-résolue: {alert.alert_id}")
                
                # Notification résolution
                await self._send_resolution_notification(alert)
    
    async def _send_resolution_notification(self, alert: PerformanceAlert):
        """**DevOps**: Notification résolution alerte"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                resolution_data = {
                    "alert_id": alert.alert_id,
                    "metric_name": alert.metric_name,
                    "resolved_at": time.time(),
                    "duration": time.time() - alert.timestamp,
                    "message": f"Alerte résolue: {alert.metric_name}"
                }
                
                await redis_conn.lpush("performance_resolutions", json.dumps(resolution_data))
                
        except Exception as e:
            logger.error(f"❌ Erreur notification résolution: {e}")
    
    async def _cleanup_old_alerts(self):
        """**DevOps**: Nettoyage alertes anciennes"""
        current_time = time.time()
        
        # Nettoyage alertes résolues anciennes (> 24h)
        alerts_to_remove = []
        for alert_id, alert in self.active_alerts.items():
            if (alert.resolved and 
                current_time - alert.timestamp > 86400):  # 24 heures
                alerts_to_remove.append(alert_id)
        
        for alert_id in alerts_to_remove:
            del self.active_alerts[alert_id]
        
        if alerts_to_remove:
            logger.info(f"🧹 {len(alerts_to_remove)} alertes anciennes nettoyées")
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """**DevOps**: Dashboard performance complet temps réel"""
        
        current_time = time.time()
        
        # Métriques actuelles
        current_metrics_summary = {}
        for category in PerformanceCategory:
            category_metrics = {
                name: value for name, value in self.current_metrics.items()
                if category.value in name.lower()
            }
            if category_metrics:
                current_metrics_summary[category.value] = category_metrics
        
        # Alertes actives par sévérité
        active_alerts_by_severity = defaultdict(list)
        for alert in self.active_alerts.values():
            if not alert.resolved:
                active_alerts_by_severity[alert.severity.value].append({
                    "alert_id": alert.alert_id,
                    "metric_name": alert.metric_name,
                    "current_value": alert.current_value,
                    "threshold": alert.threshold,
                    "message": alert.message,
                    "age_minutes": (current_time - alert.timestamp) / 60
                })
        
        # Métriques santé globale
        health_score = await self._calculate_health_score()
        
        # Top métriques problématiques
        problematic_metrics = await self._get_problematic_metrics()
        
        # Tendances récentes
        recent_trends = {}
        if hasattr(self.performance_stats, "last_trend_analysis"):
            trend_data = self.performance_stats.get("last_trend_analysis", {})
            recent_trends = trend_data.get("results", {})
        
        return {
            "overview": {
                "health_score": health_score,
                "total_metrics": len(self.current_metrics),
                "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
                "collection_errors": self.performance_stats["collection_errors"],
                "uptime_hours": (current_time - 
                               (self.current_metrics.get("uptime_in_seconds", 0) or current_time)) / 3600
            },
            "current_metrics": current_metrics_summary,
            "alerts": {
                "by_severity": dict(active_alerts_by_severity),
                "total_generated": self.performance_stats["alerts_generated"],
                "recent_count": len([a for a in self.alert_history 
                                   if current_time - a.timestamp < 3600])  # Dernière heure
            },
            "performance_summary": {
                "memory_usage_percent": self.current_metrics.get("memory_usage_percent", 0),
                "cpu_usage_percent": self.current_metrics.get("system_cpu_usage_percent", 0),
                "cache_hit_ratio": self.current_metrics.get("cache_hit_ratio", 0),
                "connected_clients": self.current_metrics.get("connected_clients", 0),
                "redis_commands_per_sec": self.current_metrics.get("redis_commands_per_sec", 0),
                "network_latency_ms": self.current_metrics.get("network_latency_ms", 0)
            },
            "ml_analytics": {
                "anomalies_detected": self.performance_stats["anomalies_detected"],
                "trend_analysis_enabled": self.enable_ml_analytics,
                "recent_trends": recent_trends
            },
            "problematic_metrics": problematic_metrics,
            "collection_stats": {
                "interval_seconds": self.collection_interval,
                "retention_hours": self.retention_hours,
                "total_collected": self.performance_stats["total_metrics_collected"],
                "last_collection": max([point.timestamp for buffer in self.metrics_buffer.values() 
                                      for point in buffer], default=0)
            }
        }
    
    async def _calculate_health_score(self) -> float:
        """**DevOps**: Calcul score santé global système"""
        try:
            scores = []
            weights = []
            
            # Score mémoire
            memory_usage = self.current_metrics.get("memory_usage_percent", 0)
            memory_score = max(0, 100 - memory_usage)
            scores.append(memory_score)
            weights.append(0.25)
            
            # Score CPU
            cpu_usage = self.current_metrics.get("system_cpu_usage_percent", 0)
            cpu_score = max(0, 100 - cpu_usage)
            scores.append(cpu_score)
            weights.append(0.20)
            
            # Score cache
            cache_hit_ratio = self.current_metrics.get("cache_hit_ratio", 90)
            cache_score = cache_hit_ratio
            scores.append(cache_score)
            weights.append(0.25)
            
            # Score latence
            latency = self.current_metrics.get("network_latency_ms", 5)
            latency_score = max(0, 100 - latency * 2)  # Pénalité latence
            scores.append(latency_score)
            weights.append(0.15)
            
            # Score alertes actives
            active_alerts = len([a for a in self.active_alerts.values() if not a.resolved])
            alert_score = max(0, 100 - active_alerts * 10)
            scores.append(alert_score)
            weights.append(0.15)
            
            # Calcul score pondéré
            health_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
            return min(100, max(0, health_score))
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul health score: {e}")
            return 50.0  # Score neutre par défaut
    
    async def _get_problematic_metrics(self) -> List[Dict[str, Any]]:
        """**DevOps**: Identification métriques problématiques"""
        problematic = []
        
        for metric_name, value in self.current_metrics.items():
            threshold = self.thresholds.get(metric_name)
            if not threshold:
                continue
            
            # Vérification si problématique
            is_problematic = False
            severity = "normal"
            
            if threshold.direction == "above":
                if value >= threshold.critical_threshold:
                    is_problematic = True
                    severity = "critical"
                elif value >= threshold.warning_threshold:
                    is_problematic = True
                    severity = "warning"
            else:  # "below"
                if value <= threshold.critical_threshold:
                    is_problematic = True
                    severity = "critical"
                elif value <= threshold.warning_threshold:
                    is_problematic = True
                    severity = "warning"
            
            if is_problematic:
                problematic.append({
                    "metric_name": metric_name,
                    "current_value": value,
                    "warning_threshold": threshold.warning_threshold,
                    "critical_threshold": threshold.critical_threshold,
                    "severity": severity,
                    "direction": threshold.direction
                })
        
        # Tri par sévérité
        severity_order = {"critical": 0, "warning": 1}
        problematic.sort(key=lambda x: severity_order.get(x["severity"], 2))
        
        return problematic[:10]  # Top 10 problématiques

# Factory function
async def create_performance_metrics_collector(redis_pool, config: Optional[Dict[str, Any]] = None):
    """**DevOps**: Factory création collecteur métriques"""
    return PerformanceMetricsCollector(redis_pool, config)

if __name__ == "__main__":
    async def demo():
        """Démonstration Performance Metrics Collector"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                mock = AsyncMock()
                mock.info.return_value = {
                    'used_memory': 100*1024*1024,  # 100MB
                    'maxmemory': 200*1024*1024,    # 200MB
                    'keyspace_hits': 1000,
                    'keyspace_misses': 100,
                    'connected_clients': 50
                }
                mock.ping = AsyncMock()
                return mock
        
        # Configuration collecteur
        config = {
            'collection_interval': 10,  # 10 secondes pour demo
            'enable_ml_analytics': True,
            'retention_hours': 1
        }
        
        # Création collecteur
        collector = await create_performance_metrics_collector(MockRedisPool(), config)
        
        # Attente collecte initiale
        await asyncio.sleep(15)
        
        # Dashboard
        dashboard = await collector.get_performance_dashboard()
        print(f"Health Score: {dashboard['overview']['health_score']:.1f}")
        print(f"Métriques collectées: {dashboard['overview']['total_metrics']}")
        print(f"Alertes actives: {dashboard['overview']['active_alerts']}")
    
    asyncio.run(demo())