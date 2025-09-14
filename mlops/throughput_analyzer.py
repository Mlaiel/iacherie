"""
Throughput Analyzer module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
📊 Throughput Analyzer - Enterprise MLOps Platform
ML Engineer Expertise: Analyseur de throughput avec bottleneck identification

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
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
import time
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BottleneckType(Enum):
    """Types de bottlenecks identifiés"""
    CPU_BOUND = "cpu_bound"
    MEMORY_BOUND = "memory_bound"
    IO_BOUND = "io_bound"
    NETWORK_BOUND = "network_bound"
    GPU_BOUND = "gpu_bound"
    DATABASE_BOUND = "database_bound"
    MODEL_COMPLEXITY = "model_complexity"
    UNKNOWN = "unknown"

class ThroughputLevel(Enum):
    """Niveaux de performance throughput"""
    EXCELLENT = "excellent"    # > 90% du maximum théorique
    GOOD = "good"             # 70-90% du maximum
    ACCEPTABLE = "acceptable"  # 50-70% du maximum
    POOR = "poor"             # 30-50% du maximum
    CRITICAL = "critical"      # < 30% du maximum

class CreatorProcessingType(Enum):
    """Types de traitement par créateur"""
    MUSICIAN_AUDIO_STREAM = "musician_audio_stream"
    MUSICIAN_AUDIO_BATCH = "musician_audio_batch"
    BLOGGER_TEXT_BATCH = "blogger_text_batch"
    BLOGGER_SEO_ANALYSIS = "blogger_seo_analysis"
    PHOTOGRAPHER_IMAGE_BULK = "photographer_image_bulk"
    PHOTOGRAPHER_IMAGE_ENHANCE = "photographer_image_enhance"
    INFLUENCER_MULTI_MODAL = "influencer_multi_modal"
    INFLUENCER_ANALYTICS = "influencer_analytics"
    COMEDIAN_SENTIMENT_STREAM = "comedian_sentiment_stream"
    COMEDIAN_CONTENT_GEN = "comedian_content_generation"

@dataclass
class ThroughputMeasurement:
    """Mesure de throughput complète"""
    timestamp: datetime
    model_id: str
    processing_type: CreatorProcessingType
    requests_per_second: float
    processed_items_count: int
    processing_duration_sec: float
    queue_length: int
    concurrent_workers: int
    cpu_utilization: float
    memory_utilization: float
    gpu_utilization: Optional[float]
    disk_io_rate_mbps: float
    network_io_rate_mbps: float
    cache_hit_ratio: float
    error_rate: float
    bottleneck_detected: BottleneckType
    optimization_score: float  # 0-100
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ThroughputTarget:
    """Cibles de throughput par type de traitement"""
    target_rps: float
    min_acceptable_rps: float
    max_queue_length: int
    max_processing_time_sec: float
    processing_type: CreatorProcessingType

@dataclass
class BottleneckAnalysis:
    """Analyse de bottleneck détaillée"""
    bottleneck_type: BottleneckType
    severity: float  # 0-1
    impact_on_throughput: float  # % de réduction
    recommended_actions: List[str]
    estimated_improvement: float  # % d'amélioration attendue
    implementation_cost: str  # "low", "medium", "high"

class ThroughputAnalyzer:
    """
    Analyseur de throughput avec identification de bottlenecks enterprise
    
    Fonctionnalités:
    - Monitoring temps réel du throughput
    - Identification intelligente des bottlenecks
    - Analyse des patterns de performance
    - Recommandations d'optimisation automatique
    - Alertes proactives par type de créateur
    """
    
    def __init__(self, 
                 db_path -> None: str = "/tmp/throughput_analyzer.db",
                 retention_days -> None: int = 30,
                 analysis_window_size -> None: int = 100) -> None:
        self.db_path = db_path
        self.retention_days = retention_days
        self.analysis_window_size = analysis_window_size
        
        # Buffers pour analyse en temps réel
        self.measurement_buffer: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=analysis_window_size)
        )
        self.throughput_history: Dict[str, List[float]] = defaultdict(list)
        self.bottleneck_history: Dict[str, List[BottleneckAnalysis]] = defaultdict(list)
        
        # Cibles de throughput par type de créateur
        self.throughput_targets = {
            CreatorProcessingType.MUSICIAN_AUDIO_STREAM: ThroughputTarget(
                target_rps=50.0, min_acceptable_rps=30.0, max_queue_length=10,
                max_processing_time_sec=0.1, processing_type=CreatorProcessingType.MUSICIAN_AUDIO_STREAM
            ),
            CreatorProcessingType.MUSICIAN_AUDIO_BATCH: ThroughputTarget(
                target_rps=10.0, min_acceptable_rps=5.0, max_queue_length=100,
                max_processing_time_sec=2.0, processing_type=CreatorProcessingType.MUSICIAN_AUDIO_BATCH
            ),
            CreatorProcessingType.BLOGGER_TEXT_BATCH: ThroughputTarget(
                target_rps=100.0, min_acceptable_rps=50.0, max_queue_length=200,
                max_processing_time_sec=0.5, processing_type=CreatorProcessingType.BLOGGER_TEXT_BATCH
            ),
            CreatorProcessingType.BLOGGER_SEO_ANALYSIS: ThroughputTarget(
                target_rps=20.0, min_acceptable_rps=10.0, max_queue_length=50,
                max_processing_time_sec=1.0, processing_type=CreatorProcessingType.BLOGGER_SEO_ANALYSIS
            ),
            CreatorProcessingType.PHOTOGRAPHER_IMAGE_BULK: ThroughputTarget(
                target_rps=5.0, min_acceptable_rps=2.0, max_queue_length=50,
                max_processing_time_sec=5.0, processing_type=CreatorProcessingType.PHOTOGRAPHER_IMAGE_BULK
            ),
            CreatorProcessingType.PHOTOGRAPHER_IMAGE_ENHANCE: ThroughputTarget(
                target_rps=2.0, min_acceptable_rps=1.0, max_queue_length=20,
                max_processing_time_sec=10.0, processing_type=CreatorProcessingType.PHOTOGRAPHER_IMAGE_ENHANCE
            ),
            CreatorProcessingType.INFLUENCER_MULTI_MODAL: ThroughputTarget(
                target_rps=25.0, min_acceptable_rps=15.0, max_queue_length=75,
                max_processing_time_sec=1.5, processing_type=CreatorProcessingType.INFLUENCER_MULTI_MODAL
            ),
            CreatorProcessingType.INFLUENCER_ANALYTICS: ThroughputTarget(
                target_rps=200.0, min_acceptable_rps=100.0, max_queue_length=500,
                max_processing_time_sec=0.2, processing_type=CreatorProcessingType.INFLUENCER_ANALYTICS
            ),
            CreatorProcessingType.COMEDIAN_SENTIMENT_STREAM: ThroughputTarget(
                target_rps=80.0, min_acceptable_rps=50.0, max_queue_length=30,
                max_processing_time_sec=0.3, processing_type=CreatorProcessingType.COMEDIAN_SENTIMENT_STREAM
            ),
            CreatorProcessingType.COMEDIAN_CONTENT_GEN: ThroughputTarget(
                target_rps=1.0, min_acceptable_rps=0.5, max_queue_length=10,
                max_processing_time_sec=30.0, processing_type=CreatorProcessingType.COMEDIAN_CONTENT_GEN
            )
        }
        
        # Callbacks pour alertes et optimisations
        self.alert_callbacks: List[Callable] = []
        self.bottleneck_callbacks: List[Callable] = []
        
        # Thread pool pour analyses
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self._setup_database()
        logger.info("📊 ThroughputAnalyzer initialized for enterprise performance analysis")
    
    def _setup_database(self) -> None:
        """Initialisation de la base de données SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des mesures de throughput
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS throughput_measurements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        model_id TEXT NOT NULL,
                        processing_type TEXT NOT NULL,
                        requests_per_second REAL NOT NULL,
                        processed_items_count INTEGER NOT NULL,
                        processing_duration_sec REAL NOT NULL,
                        queue_length INTEGER NOT NULL,
                        concurrent_workers INTEGER NOT NULL,
                        cpu_utilization REAL NOT NULL,
                        memory_utilization REAL NOT NULL,
                        gpu_utilization REAL,
                        disk_io_rate_mbps REAL NOT NULL,
                        network_io_rate_mbps REAL NOT NULL,
                        cache_hit_ratio REAL NOT NULL,
                        error_rate REAL NOT NULL,
                        bottleneck_detected TEXT NOT NULL,
                        optimization_score REAL NOT NULL,
                        metadata TEXT
                    )
                """)
                
                # Table des analyses de bottlenecks
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bottleneck_analyses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        model_id TEXT NOT NULL,
                        bottleneck_type TEXT NOT NULL,
                        severity REAL NOT NULL,
                        impact_on_throughput REAL NOT NULL,
                        recommended_actions TEXT NOT NULL,
                        estimated_improvement REAL NOT NULL,
                        implementation_cost TEXT NOT NULL
                    )
                """)
                
                # Index pour performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_throughput_model_time ON throughput_measurements(model_id, timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_throughput_type ON throughput_measurements(processing_type, timestamp)")
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Database setup error: {e}")
            raise
    
    async def measure_throughput(self,
                               model_id: str,
                               processing_type: CreatorProcessingType,
                               processed_items_count: int,
                               processing_duration_sec: float,
                               queue_length: int = 0,
                               concurrent_workers: int = 1,
                               cpu_utilization: float = 0.0,
                               memory_utilization: float = 0.0,
                               gpu_utilization: Optional[float] = None,
                               disk_io_rate_mbps: float = 0.0,
                               network_io_rate_mbps: float = 0.0,
                               cache_hit_ratio: float = 0.0,
                               error_count: int = 0,
                               metadata: Optional[Dict[str, Any]] = None) -> ThroughputMeasurement:
        """Mesurer et analyser le throughput"""
        try:
            # Calcul du throughput
            if processing_duration_sec > 0:
                requests_per_second = processed_items_count / processing_duration_sec
            else:
                requests_per_second = 0.0
            
            # Calcul du taux d'erreur
            error_rate = error_count / max(processed_items_count, 1)
            
            # Détection du bottleneck principal
            bottleneck_detected = await self._detect_bottleneck(
                cpu_utilization, memory_utilization, gpu_utilization,
                disk_io_rate_mbps, network_io_rate_mbps, queue_length,
                processing_duration_sec, processing_type
            )
            
            # Calcul du score d'optimisation
            optimization_score = await self._calculate_optimization_score(
                requests_per_second, processing_type, bottleneck_detected,
                cpu_utilization, memory_utilization, error_rate
            )
            
            measurement = ThroughputMeasurement(
                timestamp=datetime.now(),
                model_id=model_id,
                processing_type=processing_type,
                requests_per_second=requests_per_second,
                processed_items_count=processed_items_count,
                processing_duration_sec=processing_duration_sec,
                queue_length=queue_length,
                concurrent_workers=concurrent_workers,
                cpu_utilization=cpu_utilization,
                memory_utilization=memory_utilization,
                gpu_utilization=gpu_utilization,
                disk_io_rate_mbps=disk_io_rate_mbps,
                network_io_rate_mbps=network_io_rate_mbps,
                cache_hit_ratio=cache_hit_ratio,
                error_rate=error_rate,
                bottleneck_detected=bottleneck_detected,
                optimization_score=optimization_score,
                metadata=metadata or {}
            )
            
            # Stockage en buffer
            buffer_key = f"{model_id}_{processing_type.value}"
            self.measurement_buffer[buffer_key].append(measurement)
            self.throughput_history[buffer_key].append(requests_per_second)
            
            # Persistance en DB
            asyncio.create_task(self._save_measurement(measurement))
            
            # Analyse de bottleneck détaillée
            if bottleneck_detected != BottleneckType.UNKNOWN:
                bottleneck_analysis = await self._analyze_bottleneck(measurement)
                if bottleneck_analysis:
                    self.bottleneck_history[buffer_key].append(bottleneck_analysis)
                    asyncio.create_task(self._save_bottleneck_analysis(model_id, bottleneck_analysis))
            
            # Vérification des alertes
            await self._check_throughput_alerts(measurement)
            
            logger.debug(f"📈 Throughput measured for {model_id}: {requests_per_second:.2f} RPS")
            return measurement
            
        except Exception as e:
            logger.error(f"❌ Error measuring throughput for {model_id}: {e}")
            raise
    
    async def _detect_bottleneck(self,
                               cpu_util: float,
                               memory_util: float,
                               gpu_util: Optional[float],
                               disk_io: float,
                               network_io: float,
                               queue_length: int,
                               processing_time: float,
                               processing_type: CreatorProcessingType) -> BottleneckType:
        """Détection intelligente du type de bottleneck"""
        try:
            # Seuils par type de traitement
            bottleneck_thresholds = {
                # Traitement audio temps réel - sensible au CPU et GPU
                CreatorProcessingType.MUSICIAN_AUDIO_STREAM: {
                    "cpu_threshold": 0.8, "memory_threshold": 0.85,
                    "gpu_threshold": 0.9, "io_threshold": 50.0
                },
                # Traitement batch - sensible à la mémoire et I/O
                CreatorProcessingType.BLOGGER_TEXT_BATCH: {
                    "cpu_threshold": 0.85, "memory_threshold": 0.9,
                    "gpu_threshold": 0.8, "io_threshold": 100.0
                },
                # Traitement d'images - très sensible au GPU et mémoire
                CreatorProcessingType.PHOTOGRAPHER_IMAGE_BULK: {
                    "cpu_threshold": 0.75, "memory_threshold": 0.95,
                    "gpu_threshold": 0.85, "io_threshold": 200.0
                },
                # Par défaut
                "default": {
                    "cpu_threshold": 0.8, "memory_threshold": 0.85,
                    "gpu_threshold": 0.85, "io_threshold": 100.0
                }
            }
            
            thresholds = bottleneck_thresholds.get(processing_type, bottleneck_thresholds["default"])
            
            # Logique de détection hiérarchique
            bottleneck_scores = {}
            
            # Score CPU
            if cpu_util > thresholds["cpu_threshold"]:
                bottleneck_scores[BottleneckType.CPU_BOUND] = cpu_util
            
            # Score Memory
            if memory_util > thresholds["memory_threshold"]:
                bottleneck_scores[BottleneckType.MEMORY_BOUND] = memory_util
            
            # Score GPU (si disponible)
            if gpu_util is not None and gpu_util > thresholds["gpu_threshold"]:
                bottleneck_scores[BottleneckType.GPU_BOUND] = gpu_util
            
            # Score I/O
            total_io = disk_io + network_io
            if total_io > thresholds["io_threshold"]:
                if disk_io > network_io:
                    bottleneck_scores[BottleneckType.IO_BOUND] = disk_io / thresholds["io_threshold"]
                else:
                    bottleneck_scores[BottleneckType.NETWORK_BOUND] = network_io / thresholds["io_threshold"]
            
            # Détection de complexité de modèle
            target = self.throughput_targets.get(processing_type)
            if target and processing_time > target.max_processing_time_sec * 1.5:
                bottleneck_scores[BottleneckType.MODEL_COMPLEXITY] = processing_time / target.max_processing_time_sec
            
            # Retourner le bottleneck avec le score le plus élevé
            if bottleneck_scores:
                return max(bottleneck_scores.items(), key=lambda x: x[1])[0]
            else:
                return BottleneckType.UNKNOWN
                
        except Exception as e:
            logger.error(f"❌ Error detecting bottleneck: {e}")
            return BottleneckType.UNKNOWN
    
    async def _calculate_optimization_score(self,
                                          current_rps: float,
                                          processing_type: CreatorProcessingType,
                                          bottleneck: BottleneckType,
                                          cpu_util: float,
                                          memory_util: float,
                                          error_rate: float) -> float:
        """Calcul du score d'optimisation (0-100)"""
        try:
            target = self.throughput_targets.get(processing_type)
            if not target:
                return 50.0  # Score neutre si pas de cible
            
            # Score de base basé sur la performance vs cible
            performance_ratio = min(current_rps / target.target_rps, 1.0)
            base_score = performance_ratio * 40  # Max 40 points pour la performance
            
            # Score d'utilisation des ressources (équilibré = mieux)
            resource_score = 0
            optimal_cpu = 0.7  # Utilisation CPU optimale
            optimal_memory = 0.75  # Utilisation mémoire optimale
            
            cpu_score = 20 * (1 - abs(cpu_util - optimal_cpu) / optimal_cpu)
            memory_score = 20 * (1 - abs(memory_util - optimal_memory) / optimal_memory)
            resource_score = max(0, cpu_score + memory_score)  # Max 40 points
            
            # Pénalité pour les erreurs
            error_penalty = error_rate * 30  # Max 30 points de pénalité
            
            # Bonus/malus pour le type de bottleneck
            bottleneck_adjustment = 0
            if bottleneck == BottleneckType.UNKNOWN:
                bottleneck_adjustment = 10  # Bonus pour pas de bottleneck
            elif bottleneck in [BottleneckType.CPU_BOUND, BottleneckType.MEMORY_BOUND]:
                bottleneck_adjustment = -5  # Pénalité légère pour bottlenecks communs
            elif bottleneck in [BottleneckType.MODEL_COMPLEXITY, BottleneckType.IO_BOUND]:
                bottleneck_adjustment = -10  # Pénalité plus forte
            
            final_score = base_score + resource_score - error_penalty + bottleneck_adjustment
            return max(0, min(100, final_score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating optimization score: {e}")
            return 50.0
    
    async def _analyze_bottleneck(self, measurement: ThroughputMeasurement) -> Optional[BottleneckAnalysis]:
        """Analyse détaillée d'un bottleneck"""
        try:
            bottleneck = measurement.bottleneck_detected
            if bottleneck == BottleneckType.UNKNOWN:
                return None
            
            # Calcul de la sévérité
            target = self.throughput_targets.get(measurement.processing_type)
            if target:
                severity = max(0, min(1, 1 - (measurement.requests_per_second / target.target_rps)))
            else:
                severity = 0.5
            
            # Impact estimé sur le throughput
            impact_on_throughput = severity * 100
            
            # Recommandations selon le type de bottleneck
            recommendations = []
            estimated_improvement = 0.0
            implementation_cost = "medium"
            
            if bottleneck == BottleneckType.CPU_BOUND:
                recommendations = [
                    "Scale CPU resources vertically (more cores)",
                    "Implement CPU-efficient algorithms",
                    "Enable multi-threading optimization",
                    "Consider CPU caching strategies"
                ]
                estimated_improvement = 30.0
                implementation_cost = "medium"
                
            elif bottleneck == BottleneckType.MEMORY_BOUND:
                recommendations = [
                    "Increase available RAM",
                    "Implement memory-efficient data structures",
                    "Add memory pooling and caching",
                    "Optimize garbage collection settings"
                ]
                estimated_improvement = 40.0
                implementation_cost = "low"
                
            elif bottleneck == BottleneckType.GPU_BOUND:
                recommendations = [
                    "Scale GPU resources (more/better GPUs)",
                    "Optimize GPU memory usage",
                    "Implement GPU batch processing",
                    "Use mixed precision training"
                ]
                estimated_improvement = 50.0
                implementation_cost = "high"
                
            elif bottleneck == BottleneckType.IO_BOUND:
                recommendations = [
                    "Implement async I/O operations",
                    "Add SSD storage for faster disk access",
                    "Use connection pooling",
                    "Implement data compression"
                ]
                estimated_improvement = 35.0
                implementation_cost = "medium"
                
            elif bottleneck == BottleneckType.NETWORK_BOUND:
                recommendations = [
                    "Optimize network bandwidth",
                    "Implement request batching",
                    "Add CDN for content delivery",
                    "Use compression for network traffic"
                ]
                estimated_improvement = 25.0
                implementation_cost = "medium"
                
            elif bottleneck == BottleneckType.MODEL_COMPLEXITY:
                recommendations = [
                    "Apply model compression techniques",
                    "Use model quantization",
                    "Implement model pruning",
                    "Consider simpler model architectures"
                ]
                estimated_improvement = 45.0
                implementation_cost = "high"
                
            elif bottleneck == BottleneckType.DATABASE_BOUND:
                recommendations = [
                    "Optimize database queries",
                    "Add database indexing",
                    "Implement database connection pooling",
                    "Consider database sharding"
                ]
                estimated_improvement = 30.0
                implementation_cost = "medium"
            
            return BottleneckAnalysis(
                bottleneck_type=bottleneck,
                severity=severity,
                impact_on_throughput=impact_on_throughput,
                recommended_actions=recommendations,
                estimated_improvement=estimated_improvement,
                implementation_cost=implementation_cost
            )
            
        except Exception as e:
            logger.error(f"❌ Error analyzing bottleneck: {e}")
            return None
    
    async def _save_measurement(self, measurement -> None: ThroughputMeasurement) -> None:
        """Sauvegarde d'une mesure en base"""
        try:
            def save_to_db() -> None:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO throughput_measurements 
                        (timestamp, model_id, processing_type, requests_per_second,
                         processed_items_count, processing_duration_sec, queue_length,
                         concurrent_workers, cpu_utilization, memory_utilization,
                         gpu_utilization, disk_io_rate_mbps, network_io_rate_mbps,
                         cache_hit_ratio, error_rate, bottleneck_detected,
                         optimization_score, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        measurement.timestamp.isoformat(),
                        measurement.model_id,
                        measurement.processing_type.value,
                        measurement.requests_per_second,
                        measurement.processed_items_count,
                        measurement.processing_duration_sec,
                        measurement.queue_length,
                        measurement.concurrent_workers,
                        measurement.cpu_utilization,
                        measurement.memory_utilization,
                        measurement.gpu_utilization,
                        measurement.disk_io_rate_mbps,
                        measurement.network_io_rate_mbps,
                        measurement.cache_hit_ratio,
                        measurement.error_rate,
                        measurement.bottleneck_detected.value,
                        measurement.optimization_score,
                        json.dumps(measurement.metadata)
                    ))
                    conn.commit()
            
            await asyncio.get_event_loop().run_in_executor(self.executor, save_to_db)
            
        except Exception as e:
            logger.error(f"❌ Error saving measurement: {e}")
    
    async def _save_bottleneck_analysis(self, model_id -> None: str, analysis -> None: BottleneckAnalysis) -> None:
        """Sauvegarde d'une analyse de bottleneck"""
        try:
            def save_to_db() -> None:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO bottleneck_analyses 
                        (timestamp, model_id, bottleneck_type, severity,
                         impact_on_throughput, recommended_actions,
                         estimated_improvement, implementation_cost)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        model_id,
                        analysis.bottleneck_type.value,
                        analysis.severity,
                        analysis.impact_on_throughput,
                        json.dumps(analysis.recommended_actions),
                        analysis.estimated_improvement,
                        analysis.implementation_cost
                    ))
                    conn.commit()
            
            await asyncio.get_event_loop().run_in_executor(self.executor, save_to_db)
            
        except Exception as e:
            logger.error(f"❌ Error saving bottleneck analysis: {e}")
    
    async def _check_throughput_alerts(self, measurement -> None: ThroughputMeasurement) -> None:
        """Vérification et déclenchement d'alertes de throughput"""
        try:
            target = self.throughput_targets.get(measurement.processing_type)
            if not target:
                return
            
            alerts = []
            
            # Alerte throughput critique
            if measurement.requests_per_second < target.min_acceptable_rps:
                alerts.append({
                    "type": "critical_throughput",
                    "severity": "critical",
                    "message": f"Throughput critically low: {measurement.requests_per_second:.2f} < {target.min_acceptable_rps} RPS"
                })
            
            # Alerte queue length
            if measurement.queue_length > target.max_queue_length:
                alerts.append({
                    "type": "high_queue_length",
                    "severity": "high",
                    "message": f"Queue length too high: {measurement.queue_length} > {target.max_queue_length}"
                })
            
            # Alerte score d'optimisation bas
            if measurement.optimization_score < 30:
                alerts.append({
                    "type": "low_optimization_score",
                    "severity": "medium",
                    "message": f"Low optimization score: {measurement.optimization_score:.1f}%"
                })
            
            # Alerte taux d'erreur élevé
            if measurement.error_rate > 0.05:  # Plus de 5% d'erreurs
                alerts.append({
                    "type": "high_error_rate",
                    "severity": "high",
                    "message": f"High error rate: {measurement.error_rate:.2%}"
                })
            
            # Déclenchement des callbacks
            for alert in alerts:
                alert_data = {
                    "model_id": measurement.model_id,
                    "timestamp": measurement.timestamp,
                    "measurement": measurement,
                    "alert": alert
                }
                
                for callback in self.alert_callbacks:
                    try:
                        await callback(alert_data)
                    except Exception as e:
                        logger.error(f"❌ Alert callback error: {e}")
            
            if alerts:
                logger.warning(f"🚨 {len(alerts)} throughput alerts for {measurement.model_id}")
                
        except Exception as e:
            logger.error(f"❌ Error checking throughput alerts: {e}")
    
    async def get_throughput_report(self, 
                                  model_id: str,
                                  days_back: int = 7,
                                  processing_type: Optional[CreatorProcessingType] = None) -> Dict[str, Any]:
        """Générer un rapport de throughput détaillé"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            query = """
                SELECT * FROM throughput_measurements 
                WHERE model_id = ? AND timestamp >= ?
            """
            params = [model_id, start_date.isoformat()]
            
            if processing_type:
                query += " AND processing_type = ?"
                params.append(processing_type.value)
            
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
                
                # Statistiques de base
                report = {
                    "model_id": model_id,
                    "processing_type": processing_type.value if processing_type else "all",
                    "period": f"{days_back} days",
                    "total_measurements": len(df),
                    "throughput_stats": {
                        "avg_rps": float(df['requests_per_second'].mean()),
                        "max_rps": float(df['requests_per_second'].max()),
                        "min_rps": float(df['requests_per_second'].min()),
                        "p50_rps": float(df['requests_per_second'].quantile(0.5)),
                        "p95_rps": float(df['requests_per_second'].quantile(0.95)),
                        "p99_rps": float(df['requests_per_second'].quantile(0.99)),
                        "std_rps": float(df['requests_per_second'].std())
                    },
                    "performance_metrics": {
                        "avg_optimization_score": float(df['optimization_score'].mean()),
                        "avg_error_rate": float(df['error_rate'].mean()),
                        "avg_queue_length": float(df['queue_length'].mean()),
                        "avg_processing_duration": float(df['processing_duration_sec'].mean()),
                        "cache_hit_ratio": float(df['cache_hit_ratio'].mean())
                    },
                    "resource_utilization": {
                        "avg_cpu_utilization": float(df['cpu_utilization'].mean()),
                        "avg_memory_utilization": float(df['memory_utilization'].mean()),
                        "avg_disk_io_mbps": float(df['disk_io_rate_mbps'].mean()),
                        "avg_network_io_mbps": float(df['network_io_rate_mbps'].mean())
                    },
                    "bottleneck_analysis": df['bottleneck_detected'].value_counts().to_dict(),
                    "total_items_processed": int(df['processed_items_count'].sum())
                }
                
                # Ajout de stats GPU si disponible
                if df['gpu_utilization'].notna().any():
                    report["resource_utilization"]["avg_gpu_utilization"] = float(
                        df['gpu_utilization'].dropna().mean()
                    )
                
                # Comparaison avec les cibles si disponible
                if processing_type and processing_type in self.throughput_targets:
                    target = self.throughput_targets[processing_type]
                    report["target_compliance"] = {
                        "avg_rps_vs_target": report["throughput_stats"]["avg_rps"] / target.target_rps,
                        "min_rps_compliance": report["throughput_stats"]["min_rps"] >= target.min_acceptable_rps,
                        "queue_length_compliance": report["performance_metrics"]["avg_queue_length"] <= target.max_queue_length,
                        "processing_time_compliance": report["performance_metrics"]["avg_processing_duration"] <= target.max_processing_time_sec
                    }
                
                # Tendance récente
                recent_df = df.head(20)  # 20 dernières mesures
                if len(recent_df) >= 5:
                    recent_trend = np.polyfit(range(len(recent_df)), recent_df['requests_per_second'], 1)[0]
                    report["recent_trend"] = {
                        "slope_rps_per_measurement": float(recent_trend),
                        "trending": "up" if recent_trend > 0 else "down" if recent_trend < 0 else "stable"
                    }
                
                return report
                
        except Exception as e:
            logger.error(f"❌ Error generating throughput report for {model_id}: {e}")
            return {"error": str(e)}
    
    async def get_bottleneck_recommendations(self, 
                                           model_id: str,
                                           days_back: int = 7) -> List[BottleneckAnalysis]:
        """Obtenir les recommandations de bottlenecks récentes"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM bottleneck_analyses 
                    WHERE model_id = ? AND timestamp >= ?
                    ORDER BY severity DESC, timestamp DESC
                    LIMIT 10
                """, (model_id, start_date.isoformat()))
                
                rows = cursor.fetchall()
                
                recommendations = []
                for row in rows:
                    try:
                        analysis = BottleneckAnalysis(
                            bottleneck_type=BottleneckType(row[3]),
                            severity=row[4],
                            impact_on_throughput=row[5],
                            recommended_actions=json.loads(row[6]),
                            estimated_improvement=row[7],
                            implementation_cost=row[8]
                        )
                        recommendations.append(analysis)
                    except Exception as e:
                        logger.error(f"❌ Error parsing bottleneck analysis: {e}")
                        continue
                
                return recommendations
                
        except Exception as e:
            logger.error(f"❌ Error getting bottleneck recommendations: {e}")
            return []
    
    def add_alert_callback(self, callback -> None: Callable) -> None:
        """Ajouter un callback pour les alertes de throughput"""
        self.alert_callbacks.append(callback)
        logger.info(f"📢 Throughput alert callback added. Total: {len(self.alert_callbacks)}")
    
    def add_bottleneck_callback(self, callback -> None: Callable) -> None:
        """Ajouter un callback pour les analyses de bottlenecks"""
        self.bottleneck_callbacks.append(callback)
        logger.info(f"🔍 Bottleneck callback added. Total: {len(self.bottleneck_callbacks)}")
    
    async def cleanup_old_data(self) -> None:
        """Nettoyage des données anciennes"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM throughput_measurements 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                measurements_deleted = cursor.rowcount
                
                cursor.execute("""
                    DELETE FROM bottleneck_analyses 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                analyses_deleted = cursor.rowcount
                conn.commit()
            
            logger.info(f"🧹 Cleaned up {measurements_deleted} measurements and {analyses_deleted} analyses")
            return measurements_deleted + analyses_deleted
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0


# Exemple d'utilisation pour démonstration
async def main() -> None:
    """Démonstration des capacités du ThroughputAnalyzer"""
    analyzer = ThroughputAnalyzer()
    
    # Callbacks pour démonstration
    async def throughput_alert_handler(alert_data) -> None:
        print(f"🚨 THROUGHPUT ALERT: {alert_data['alert']['message']}")
    
    async def bottleneck_handler(bottleneck_data) -> None:
        print(f"🔍 BOTTLENECK DETECTED: {bottleneck_data['analysis'].bottleneck_type.value}")
        print(f"   Severity: {bottleneck_data['analysis'].severity:.2f}")
        print(f"   Expected improvement: {bottleneck_data['analysis'].estimated_improvement:.1f}%")
    
    analyzer.add_alert_callback(throughput_alert_handler)
    analyzer.add_bottleneck_callback(bottleneck_handler)
    
    # Simulation de mesures pour différents types de créateurs
    processing_scenarios = [
        (CreatorProcessingType.MUSICIAN_AUDIO_STREAM, "music_model", 100, 2.5, 0.7, 0.6),
        (CreatorProcessingType.BLOGGER_TEXT_BATCH, "blog_model", 500, 6.0, 0.85, 0.9),
        (CreatorProcessingType.PHOTOGRAPHER_IMAGE_BULK, "photo_model", 20, 15.0, 0.6, 0.95),
        (CreatorProcessingType.INFLUENCER_ANALYTICS, "analytics_model", 1000, 4.2, 0.9, 0.7),
        (CreatorProcessingType.COMEDIAN_SENTIMENT_STREAM, "comedy_model", 200, 3.1, 0.75, 0.8)
    ]
    
    for processing_type, model_id, items_count, duration, cpu_util, mem_util in processing_scenarios:
        # Simulation avec variation pour créer des bottlenecks
        variation_factor = np.random.uniform(0.8, 1.3)
        
        measurement = await analyzer.measure_throughput(
            model_id=model_id,
            processing_type=processing_type,
            processed_items_count=int(items_count * variation_factor),
            processing_duration_sec=duration * variation_factor,
            queue_length=int(np.random.uniform(0, 50)),
            concurrent_workers=np.random.randint(1, 8),
            cpu_utilization=min(1.0, cpu_util * variation_factor),
            memory_utilization=min(1.0, mem_util * variation_factor),
            gpu_utilization=np.random.uniform(0.3, 0.95) if processing_type in [
                CreatorProcessingType.PHOTOGRAPHER_IMAGE_BULK,
                CreatorProcessingType.MUSICIAN_AUDIO_STREAM
            ] else None,
            disk_io_rate_mbps=np.random.uniform(10, 200),
            network_io_rate_mbps=np.random.uniform(5, 100),
            cache_hit_ratio=np.random.uniform(0.6, 0.95),
            error_count=int(np.random.uniform(0, items_count * 0.1)),
            metadata={"test_scenario": True}
        )
        
        print(f"📊 {model_id}: {measurement.requests_per_second:.2f} RPS (Score: {measurement.optimization_score:.1f})")
    
    # Génération de rapports
    print(f"\n📋 Generating reports...")
    for _, model_id, _, _, _, _ in processing_scenarios[:2]:
        report = await analyzer.get_throughput_report(model_id, days_back=1)
        if "error" not in report:
            print(f"\n📈 Report for {model_id}:")
            print(f"   Avg RPS: {report['throughput_stats']['avg_rps']:.2f}")
            print(f"   Optimization Score: {report['performance_metrics']['avg_optimization_score']:.1f}%")
            print(f"   Main bottlenecks: {list(report['bottleneck_analysis'].keys())}")
    
    print(f"✅ ThroughputAnalyzer demonstration completed")


if __name__ == "__main__":
    asyncio.run(main())