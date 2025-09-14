"""
Latency Monitor module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
⚡ Latency Monitor - Enterprise MLOps Platform
ML Engineer Expertise: Monitor de latence avec optimisation automatique des performances

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from collections import deque, defaultdict
import statistics
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LatencyLevel(Enum):
    """Niveaux de latence pour classification"""
    EXCELLENT = "excellent"      # < 20ms
    GOOD = "good"               # 20-50ms
    ACCEPTABLE = "acceptable"   # 50-100ms
    POOR = "poor"              # 100-500ms
    CRITICAL = "critical"       # > 500ms

class OptimizationStrategy(Enum):
    """Stratégies d'optimisation automatique"""
    CACHING = "caching"
    BATCH_PROCESSING = "batch_processing"
    MODEL_COMPRESSION = "model_compression"
    HARDWARE_SCALING = "hardware_scaling"
    LOAD_BALANCING = "load_balancing"
    PREPROCESSING_OPT = "preprocessing_optimization"

class CreatorWorkload(Enum):
    """Types de workloads créateurs"""
    MUSICIAN_REALTIME = "musician_realtime"          # Audio processing en temps réel
    BLOGGER_BATCH = "blogger_batch"                  # Traitement NLP par batch
    PHOTOGRAPHER_BULK = "photographer_bulk"          # Traitement d'images en lot
    INFLUENCER_INTERACTIVE = "influencer_interactive" # Recommandations interactives
    COMEDIAN_STREAMING = "comedian_streaming"        # Analyse sentiment en streaming

@dataclass
class LatencyMeasurement:
    """Mesure de latence complète"""
    timestamp: datetime
    model_id: str
    operation_type: str
    latency_ms: float
    request_size_kb: float
    response_size_kb: float
    cpu_usage: float
    memory_usage_mb: float
    gpu_usage: Optional[float]
    network_latency_ms: Optional[float]
    cache_hit: bool
    error_occurred: bool
    creator_workload: CreatorWorkload
    optimization_applied: List[OptimizationStrategy] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LatencyTarget:
    """Cibles de latence pour différents cas d'usage"""
    p50_target_ms: float
    p95_target_ms: float
    p99_target_ms: float
    max_acceptable_ms: float
    creator_workload: CreatorWorkload

@dataclass
class OptimizationRecommendation:
    """Recommandation d'optimisation"""
    strategy: OptimizationStrategy
    expected_improvement_ms: float
    implementation_cost: str  # "low", "medium", "high"
    priority: int  # 1-5, 1 being highest
    description: str

class LatencyMonitor:
    """
    Monitor de latence avec optimisation automatique enterprise
    
    Fonctionnalités:
    - Monitoring temps réel de la latence
    - Analyse statistique des patterns
    - Détection d'anomalies de performance
    - Recommandations d'optimisation automatique
    - Alertes intelligentes par workload créateur
    """
    
    def __init__(self, 
                 db_path -> None: str = "/tmp/latency_monitor.db",
                 retention_days -> None: int = 30,
                 measurement_buffer_size -> None: int = 10000) -> None:
        self.db_path = db_path
        self.retention_days = retention_days
        self.measurement_buffer_size = measurement_buffer_size
        
        # Buffers en mémoire pour performance
        self.measurement_buffer: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=measurement_buffer_size)
        )
        self.real_time_stats: Dict[str, Dict] = defaultdict(dict)
        
        # Cibles de latence par workload créateur
        self.latency_targets = {
            CreatorWorkload.MUSICIAN_REALTIME: LatencyTarget(
                p50_target_ms=15.0, p95_target_ms=25.0, p99_target_ms=40.0, 
                max_acceptable_ms=50.0, creator_workload=CreatorWorkload.MUSICIAN_REALTIME
            ),
            CreatorWorkload.BLOGGER_BATCH: LatencyTarget(
                p50_target_ms=100.0, p95_target_ms=300.0, p99_target_ms=500.0,
                max_acceptable_ms=1000.0, creator_workload=CreatorWorkload.BLOGGER_BATCH
            ),
            CreatorWorkload.PHOTOGRAPHER_BULK: LatencyTarget(
                p50_target_ms=200.0, p95_target_ms=800.0, p99_target_ms=1500.0,
                max_acceptable_ms=3000.0, creator_workload=CreatorWorkload.PHOTOGRAPHER_BULK
            ),
            CreatorWorkload.INFLUENCER_INTERACTIVE: LatencyTarget(
                p50_target_ms=50.0, p95_target_ms=100.0, p99_target_ms=200.0,
                max_acceptable_ms=300.0, creator_workload=CreatorWorkload.INFLUENCER_INTERACTIVE
            ),
            CreatorWorkload.COMEDIAN_STREAMING: LatencyTarget(
                p50_target_ms=30.0, p95_target_ms=75.0, p99_target_ms=150.0,
                max_acceptable_ms=200.0, creator_workload=CreatorWorkload.COMEDIAN_STREAMING
            )
        }
        
        # Callbacks pour alertes
        self.alert_callbacks: List[Callable] = []
        self.optimization_callbacks: List[Callable] = []
        
        # Thread pool pour traitement asynchrone
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self._setup_database()
        logger.info("⚡ LatencyMonitor initialized for enterprise performance optimization")
    
    def _setup_database(self) -> None:
        """Initialisation de la base de données SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des mesures de latence
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS latency_measurements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        model_id TEXT NOT NULL,
                        operation_type TEXT NOT NULL,
                        latency_ms REAL NOT NULL,
                        request_size_kb REAL NOT NULL,
                        response_size_kb REAL NOT NULL,
                        cpu_usage REAL NOT NULL,
                        memory_usage_mb REAL NOT NULL,
                        gpu_usage REAL,
                        network_latency_ms REAL,
                        cache_hit BOOLEAN NOT NULL,
                        error_occurred BOOLEAN NOT NULL,
                        creator_workload TEXT NOT NULL,
                        optimization_applied TEXT,
                        metadata TEXT
                    )
                """)
                
                # Table des optimisations appliquées
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS optimizations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        model_id TEXT NOT NULL,
                        strategy TEXT NOT NULL,
                        expected_improvement_ms REAL NOT NULL,
                        actual_improvement_ms REAL,
                        implementation_cost TEXT NOT NULL,
                        success BOOLEAN
                    )
                """)
                
                # Index pour performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_latency_model_time ON latency_measurements(model_id, timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_latency_workload ON latency_measurements(creator_workload, timestamp)")
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Database setup error: {e}")
            raise
    
    async def measure_latency(self,
                            model_id: str,
                            operation_type: str,
                            start_time: float,
                            end_time: float,
                            request_size_kb: float = 0.0,
                            response_size_kb: float = 0.0,
                            cpu_usage: float = 0.0,
                            memory_usage_mb: float = 0.0,
                            gpu_usage: Optional[float] = None,
                            network_latency_ms: Optional[float] = None,
                            cache_hit: bool = False,
                            error_occurred: bool = False,
                            creator_workload: CreatorWorkload = CreatorWorkload.INFLUENCER_INTERACTIVE,
                            metadata: Optional[Dict[str, Any]] = None) -> LatencyMeasurement:
        """Mesurer et enregistrer une latence"""
        try:
            latency_ms = (end_time - start_time) * 1000  # Conversion en ms
            
            measurement = LatencyMeasurement(
                timestamp=datetime.now(),
                model_id=model_id,
                operation_type=operation_type,
                latency_ms=latency_ms,
                request_size_kb=request_size_kb,
                response_size_kb=response_size_kb,
                cpu_usage=cpu_usage,
                memory_usage_mb=memory_usage_mb,
                gpu_usage=gpu_usage,
                network_latency_ms=network_latency_ms,
                cache_hit=cache_hit,
                error_occurred=error_occurred,
                creator_workload=creator_workload,
                metadata=metadata or {}
            )
            
            # Stockage en buffer
            buffer_key = f"{model_id}_{operation_type}"
            self.measurement_buffer[buffer_key].append(measurement)
            
            # Mise à jour des stats temps réel
            await self._update_real_time_stats(buffer_key, measurement)
            
            # Persistance asynchrone en DB
            asyncio.create_task(self._save_measurement(measurement))
            
            # Vérification des seuils et alertes
            await self._check_latency_alerts(measurement)
            
            # Recommandations d'optimisation si nécessaire
            if latency_ms > self.latency_targets[creator_workload].p95_target_ms:
                await self._generate_optimization_recommendations(measurement)
            
            logger.debug(f"⏱️ Latency measured for {model_id}: {latency_ms:.2f}ms")
            return measurement
            
        except Exception as e:
            logger.error(f"❌ Error measuring latency for {model_id}: {e}")
            raise
    
    async def _update_real_time_stats(self, buffer_key -> None: str, measurement -> None: LatencyMeasurement) -> None:
        """Mise à jour des statistiques temps réel"""
        try:
            buffer = self.measurement_buffer[buffer_key]
            recent_measurements = list(buffer)[-100:]  # 100 dernières mesures
            
            if len(recent_measurements) >= 5:
                latencies = [m.latency_ms for m in recent_measurements if not m.error_occurred]
                
                if latencies:
                    self.real_time_stats[buffer_key] = {
                        "count": len(latencies),
                        "mean": statistics.mean(latencies),
                        "median": statistics.median(latencies),
                        "p95": np.percentile(latencies, 95),
                        "p99": np.percentile(latencies, 99),
                        "min": min(latencies),
                        "max": max(latencies),
                        "std": statistics.stdev(latencies) if len(latencies) > 1 else 0,
                        "error_rate": sum(1 for m in recent_measurements if m.error_occurred) / len(recent_measurements),
                        "cache_hit_rate": sum(1 for m in recent_measurements if m.cache_hit) / len(recent_measurements),
                        "last_updated": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error updating real-time stats: {e}")
    
    async def _save_measurement(self, measurement -> None: LatencyMeasurement) -> None:
        """Sauvegarde asynchrone d'une mesure"""
        try:
            def save_to_db() -> None:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO latency_measurements 
                        (timestamp, model_id, operation_type, latency_ms, request_size_kb,
                         response_size_kb, cpu_usage, memory_usage_mb, gpu_usage,
                         network_latency_ms, cache_hit, error_occurred, creator_workload,
                         optimization_applied, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        measurement.timestamp.isoformat(),
                        measurement.model_id,
                        measurement.operation_type,
                        measurement.latency_ms,
                        measurement.request_size_kb,
                        measurement.response_size_kb,
                        measurement.cpu_usage,
                        measurement.memory_usage_mb,
                        measurement.gpu_usage,
                        measurement.network_latency_ms,
                        measurement.cache_hit,
                        measurement.error_occurred,
                        measurement.creator_workload.value,
                        json.dumps([s.value for s in measurement.optimization_applied]),
                        json.dumps(measurement.metadata)
                    ))
                    conn.commit()
            
            # Exécution en thread pool pour éviter de bloquer
            await asyncio.get_event_loop().run_in_executor(self.executor, save_to_db)
            
        except Exception as e:
            logger.error(f"❌ Error saving measurement: {e}")
    
    async def _check_latency_alerts(self, measurement -> None: LatencyMeasurement) -> None:
        """Vérification et déclenchement d'alertes de latence"""
        try:
            target = self.latency_targets.get(measurement.creator_workload)
            if not target:
                return
            
            alerts = []
            
            # Classification du niveau de latence
            if measurement.latency_ms > target.max_acceptable_ms:
                level = LatencyLevel.CRITICAL
                alerts.append({
                    "type": "critical_latency",
                    "severity": "critical",
                    "message": f"Critical latency: {measurement.latency_ms:.2f}ms > {target.max_acceptable_ms}ms"
                })
            elif measurement.latency_ms > target.p99_target_ms:
                level = LatencyLevel.POOR
                alerts.append({
                    "type": "poor_latency",
                    "severity": "high",
                    "message": f"Poor latency: {measurement.latency_ms:.2f}ms > P99 target {target.p99_target_ms}ms"
                })
            elif measurement.latency_ms > target.p95_target_ms:
                level = LatencyLevel.ACCEPTABLE
                alerts.append({
                    "type": "acceptable_latency",
                    "severity": "medium",
                    "message": f"Latency above P95 target: {measurement.latency_ms:.2f}ms > {target.p95_target_ms}ms"
                })
            elif measurement.latency_ms > target.p50_target_ms:
                level = LatencyLevel.GOOD
            else:
                level = LatencyLevel.EXCELLENT
            
            # Vérification des tendances dégradantes
            buffer_key = f"{measurement.model_id}_{measurement.operation_type}"
            if buffer_key in self.real_time_stats:
                stats = self.real_time_stats[buffer_key]
                if stats["p95"] > target.p95_target_ms * 1.2:  # 20% au-dessus de la cible
                    alerts.append({
                        "type": "degrading_trend",
                        "severity": "medium",
                        "message": f"P95 latency trending above target: {stats['p95']:.2f}ms"
                    })
            
            # Déclenchement des callbacks d'alerte
            for alert in alerts:
                alert_data = {
                    "model_id": measurement.model_id,
                    "timestamp": measurement.timestamp,
                    "latency_level": level,
                    "measurement": measurement,
                    "alert": alert
                }
                
                for callback in self.alert_callbacks:
                    try:
                        await callback(alert_data)
                    except Exception as e:
                        logger.error(f"❌ Alert callback error: {e}")
            
            if alerts:
                logger.warning(f"🚨 {len(alerts)} latency alerts for {measurement.model_id}")
                
        except Exception as e:
            logger.error(f"❌ Error checking latency alerts: {e}")
    
    async def _generate_optimization_recommendations(self, measurement -> None: LatencyMeasurement) -> None:
        """Génération de recommandations d'optimisation"""
        try:
            recommendations = []
            
            # Analyse des patterns pour recommandations
            if measurement.cache_hit is False and measurement.latency_ms > 100:
                recommendations.append(OptimizationRecommendation(
                    strategy=OptimizationStrategy.CACHING,
                    expected_improvement_ms=measurement.latency_ms * 0.3,
                    implementation_cost="medium",
                    priority=1,
                    description="Implement intelligent caching for repeated requests"
                ))
            
            if measurement.cpu_usage > 0.8:
                recommendations.append(OptimizationRecommendation(
                    strategy=OptimizationStrategy.HARDWARE_SCALING,
                    expected_improvement_ms=measurement.latency_ms * 0.4,
                    implementation_cost="high",
                    priority=2,
                    description="Scale CPU resources for better performance"
                ))
            
            if measurement.request_size_kb > 1000:  # Grosses requêtes
                recommendations.append(OptimizationRecommendation(
                    strategy=OptimizationStrategy.MODEL_COMPRESSION,
                    expected_improvement_ms=measurement.latency_ms * 0.2,
                    implementation_cost="medium",
                    priority=3,
                    description="Apply model compression techniques"
                ))
            
            if measurement.creator_workload in [CreatorWorkload.BLOGGER_BATCH, CreatorWorkload.PHOTOGRAPHER_BULK]:
                recommendations.append(OptimizationRecommendation(
                    strategy=OptimizationStrategy.BATCH_PROCESSING,
                    expected_improvement_ms=measurement.latency_ms * 0.5,
                    implementation_cost="low",
                    priority=1,
                    description="Optimize for batch processing workloads"
                ))
            
            # Déclenchement des callbacks d'optimisation
            if recommendations:
                optimization_data = {
                    "model_id": measurement.model_id,
                    "timestamp": measurement.timestamp,
                    "measurement": measurement,
                    "recommendations": recommendations
                }
                
                for callback in self.optimization_callbacks:
                    try:
                        await callback(optimization_data)
                    except Exception as e:
                        logger.error(f"❌ Optimization callback error: {e}")
                
                logger.info(f"💡 Generated {len(recommendations)} optimization recommendations for {measurement.model_id}")
                
        except Exception as e:
            logger.error(f"❌ Error generating optimization recommendations: {e}")
    
    async def get_latency_report(self, 
                               model_id: str,
                               days_back: int = 7,
                               operation_type: Optional[str] = None) -> Dict[str, Any]:
        """Générer un rapport de latence pour un modèle"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            query = """
                SELECT * FROM latency_measurements 
                WHERE model_id = ? AND timestamp >= ?
            """
            params = [model_id, start_date.isoformat()]
            
            if operation_type:
                query += " AND operation_type = ?"
                params.append(operation_type)
            
            query += " ORDER BY timestamp DESC"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                if not rows:
                    return {"error": "No data found for the specified period"}
                
                # Conversion en DataFrame
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Filtrage des erreurs pour les stats principales
                clean_df = df[df['error_occurred'] == 0]
                
                if len(clean_df) == 0:
                    return {"error": "No successful measurements found"}
                
                latencies = clean_df['latency_ms'].values
                
                # Rapport détaillé
                report = {
                    "model_id": model_id,
                    "operation_type": operation_type,
                    "period": f"{days_back} days",
                    "total_measurements": len(df),
                    "successful_measurements": len(clean_df),
                    "error_rate": (len(df) - len(clean_df)) / len(df) if len(df) > 0 else 0,
                    "latency_stats": {
                        "mean_ms": float(np.mean(latencies)),
                        "median_ms": float(np.median(latencies)),
                        "p50_ms": float(np.percentile(latencies, 50)),
                        "p95_ms": float(np.percentile(latencies, 95)),
                        "p99_ms": float(np.percentile(latencies, 99)),
                        "min_ms": float(np.min(latencies)),
                        "max_ms": float(np.max(latencies)),
                        "std_ms": float(np.std(latencies))
                    },
                    "cache_hit_rate": float(clean_df['cache_hit'].mean()),
                    "avg_cpu_usage": float(clean_df['cpu_usage'].mean()),
                    "avg_memory_usage_mb": float(clean_df['memory_usage_mb'].mean()),
                    "creator_workloads": clean_df['creator_workload'].value_counts().to_dict(),
                    "optimization_strategies_used": self._parse_optimization_stats(clean_df)
                }
                
                # Comparaison avec les cibles
                if 'creator_workload' in clean_df.columns and len(clean_df) > 0:
                    primary_workload = clean_df['creator_workload'].mode()[0]
                    if primary_workload in [w.value for w in CreatorWorkload]:
                        workload_enum = CreatorWorkload(primary_workload)
                        if workload_enum in self.latency_targets:
                            target = self.latency_targets[workload_enum]
                            report["target_compliance"] = {
                                "p50_compliance": report["latency_stats"]["p50_ms"] <= target.p50_target_ms,
                                "p95_compliance": report["latency_stats"]["p95_ms"] <= target.p95_target_ms,
                                "p99_compliance": report["latency_stats"]["p99_ms"] <= target.p99_target_ms,
                                "max_compliance": report["latency_stats"]["max_ms"] <= target.max_acceptable_ms
                            }
                
                return report
                
        except Exception as e:
            logger.error(f"❌ Error generating latency report for {model_id}: {e}")
            return {"error": str(e)}
    
    def _parse_optimization_stats(self, df: pd.DataFrame) -> Dict[str, int]:
        """Parser les statistiques d'optimisations appliquées"""
        try:
            optimization_counts = defaultdict(int)
            
            for opt_json in df['optimization_applied'].dropna():
                try:
                    optimizations = json.loads(opt_json)
                    for opt in optimizations:
                        optimization_counts[opt] += 1
                except json.JSONDecodeError:
                    continue
            
            return dict(optimization_counts)
            
        except Exception as e:
            logger.error(f"❌ Error parsing optimization stats: {e}")
            return {}
    
    async def get_real_time_stats(self, model_id: str, operation_type: str) -> Dict[str, Any]:
        """Obtenir les statistiques temps réel"""
        buffer_key = f"{model_id}_{operation_type}"
        
        if buffer_key in self.real_time_stats:
            return self.real_time_stats[buffer_key]
        else:
            return {"error": "No real-time data available"}
    
    def add_alert_callback(self, callback -> None: Callable) -> None:
        """Ajouter un callback pour les alertes de latence"""
        self.alert_callbacks.append(callback)
        logger.info(f"📢 Latency alert callback added. Total callbacks: {len(self.alert_callbacks)}")
    
    def add_optimization_callback(self, callback -> None: Callable) -> None:
        """Ajouter un callback pour les recommandations d'optimisation"""
        self.optimization_callbacks.append(callback)
        logger.info(f"🚀 Optimization callback added. Total callbacks: {len(self.optimization_callbacks)}")
    
    async def cleanup_old_data(self) -> None:
        """Nettoyage des données anciennes"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM latency_measurements 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
            
            logger.info(f"🧹 Cleaned up {deleted_count} old latency records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0


# Context manager pour mesure automatique de latence
class LatencyMeasureContext:
    """Context manager pour mesure automatique de latence"""
    
    def __init__(self, 
                 monitor -> None: LatencyMonitor,
                 model_id -> None: str,
                 operation_type -> None: str,
                 creator_workload -> None: CreatorWorkload = CreatorWorkload.INFLUENCER_INTERACTIVE,
                 **kwargs) -> None:
        self.monitor = monitor
        self.model_id = model_id
        self.operation_type = operation_type
        self.creator_workload = creator_workload
        self.kwargs = kwargs
        self.start_time = None
        self.end_time = None
    
    def __enter__(self) -> None:
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.end_time = time.time()
        
        # Mesure asynchrone de la latence
        asyncio.create_task(self.monitor.measure_latency(
            model_id=self.model_id,
            operation_type=self.operation_type,
            start_time=self.start_time,
            end_time=self.end_time,
            creator_workload=self.creator_workload,
            error_occurred=exc_type is not None,
            **self.kwargs
        ))


# Exemple d'utilisation pour démonstration
async def main() -> None:
    """Démonstration des capacités du LatencyMonitor"""
    monitor = LatencyMonitor()
    
    # Callback d'exemple pour les alertes
    async def latency_alert_handler(alert_data) -> None:
        print(f"🚨 LATENCY ALERT: {alert_data['alert']['message']}")
    
    # Callback d'exemple pour les optimisations
    async def optimization_handler(opt_data) -> None:
        print(f"💡 OPTIMIZATION: {len(opt_data['recommendations'])} recommendations generated")
        for rec in opt_data['recommendations']:
            print(f"   - {rec.strategy.value}: {rec.description}")
    
    monitor.add_alert_callback(latency_alert_handler)
    monitor.add_optimization_callback(optimization_handler)
    
    # Simulation de mesures pour différents workloads créateurs
    workloads = [
        (CreatorWorkload.MUSICIAN_REALTIME, "audio_classification", 0.025),
        (CreatorWorkload.BLOGGER_BATCH, "text_processing", 0.150),
        (CreatorWorkload.PHOTOGRAPHER_BULK, "image_enhancement", 0.300),
        (CreatorWorkload.INFLUENCER_INTERACTIVE, "recommendation", 0.080),
        (CreatorWorkload.COMEDIAN_STREAMING, "sentiment_analysis", 0.045)
    ]
    
    for workload, operation, base_latency in workloads:
        model_id = f"{workload.value}_model"
        
        # Simulation de plusieurs mesures avec variation
        for i in range(10):
            # Simulation d'une latence variable
            variation = np.random.normal(0, base_latency * 0.2)
            simulated_latency = base_latency + variation
            
            start_time = time.time()
            end_time = start_time + simulated_latency
            
            await monitor.measure_latency(
                model_id=model_id,
                operation_type=operation,
                start_time=start_time,
                end_time=end_time,
                request_size_kb=np.random.uniform(1, 100),
                response_size_kb=np.random.uniform(0.5, 50),
                cpu_usage=np.random.uniform(0.2, 0.9),
                memory_usage_mb=np.random.uniform(100, 1000),
                cache_hit=np.random.choice([True, False], p=[0.7, 0.3]),
                creator_workload=workload,
                metadata={"test_run": i}
            )
    
    # Génération de rapports
    for workload, operation, _ in workloads[:2]:  # Test sur 2 workloads
        model_id = f"{workload.value}_model"
        report = await monitor.get_latency_report(model_id, operation_type=operation)
        print(f"\n📊 Latency Report for {model_id}:")
        print(f"   Mean latency: {report.get('latency_stats', {}).get('mean_ms', 0):.2f}ms")
        print(f"   P95 latency: {report.get('latency_stats', {}).get('p95_ms', 0):.2f}ms")
        print(f"   Error rate: {report.get('error_rate', 0):.2%}")
    
    # Démonstration du context manager
    print(f"\n🔄 Context Manager Demo:")
    with LatencyMeasureContext(
        monitor, 
        "demo_model", 
        "context_test",
        CreatorWorkload.MUSICIAN_REALTIME,
        request_size_kb=50.0
    ):
        # Simulation d'une opération
        await asyncio.sleep(0.03)
    
    print(f"✅ LatencyMonitor demonstration completed")


if __name__ == "__main__":
    asyncio.run(main())