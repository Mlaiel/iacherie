#!/usr/bin/env python3
"""
⚡ Real-Time Metrics Collector - Enterprise MLOps Platform
High-performance streaming metrics collection for Creator Economy
Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  PROPRIETARY SOFTWARE - COPYRIGHT NOTICE
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code owned by Fahed Mlaiel
- Commercial use PROHIBITED without written authorization
- Reverse engineering STRICTLY FORBIDDEN
- Distribution PROHIBITED without explicit license
- Violations will result in immediate legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team training included

Logique métier IA Chéries: Créateurs multi-format → IA processing → Protection → 
Monétisation → Collaboration & Gamification → SEO → Distribution
"""

import asyncio
import logging
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor
import warnings

# Suppress non-critical warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Optional high-performance dependencies
try:
    import numpy as np
    import pandas as pd
    PANDAS_NUMPY_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  Pandas/NumPy not available. Some features will be limited.")
    PANDAS_NUMPY_AVAILABLE = False

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  SciPy not available. Statistical functions will be limited.")
    SCIPY_AVAILABLE = False

# Creator Economy types
class CreatorType(Enum):
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ALL = "all"

class MetricType(Enum):
    """Types de métriques collectées"""
    PERFORMANCE = "performance"
    BUSINESS = "business"
    TECHNICAL = "technical"
    CREATOR_SPECIFIC = "creator_specific"
    INFRASTRUCTURE = "infrastructure"
    USER_EXPERIENCE = "user_experience"
    SECURITY = "security"
    QUALITY = "quality"

class MetricAggregation(Enum):
    """Méthodes d'agrégation des métriques"""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    LATEST = "latest"
    RATE = "rate"

class StreamingMode(Enum):
    """Modes de streaming des métriques"""
    PUSH = "push"
    PULL = "pull"
    HYBRID = "hybrid"
    BATCH = "batch"

@dataclass
class MetricPoint:
    """Point de métrique individuel"""
    timestamp: datetime
    metric_name: str
    value: Union[float, int, str, bool]
    tags: Dict[str, str] = field(default_factory=dict)
    creator_type: Optional[CreatorType] = None
    model_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricDefinition:
    """Définition d'une métrique"""
    name: str
    metric_type: MetricType
    description: str
    unit: str
    aggregation_method: MetricAggregation
    retention_days: int = 30
    sample_rate: float = 1.0  # 1.0 = 100% sampling
    creator_specific: bool = False
    business_critical: bool = False
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class StreamingConfig:
    """Configuration du streaming en temps réel"""
    buffer_size: int = 10000
    flush_interval_seconds: int = 5
    batch_size: int = 1000
    max_workers: int = 4
    enable_compression: bool = True
    enable_deduplication: bool = True
    streaming_mode: StreamingMode = StreamingMode.HYBRID
    high_throughput_mode: bool = False
    memory_limit_mb: int = 512
    disk_buffer_enabled: bool = True

class RealTimeMetricsCollector:
    """
    ⚡ Collecteur de métriques temps réel haute performance
    
    Expertise combinée:
    - Lead Dev IA: Intelligence artificielle et analytics avancés
    - Backend Senior: Architecture haute performance et scalabilité
    - ML Engineer: Métriques ML et observabilité modèles
    - DBA: Optimisation stockage et requêtes
    - Sécurité: Protection données et accès sécurisé
    - Microservices: Architecture distribuée et resilience
    - Audio: Métriques spécialisées multimédia
    - DevOps: Infrastructure et monitoring production
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        creator_type: Optional[CreatorType] = None,
        model_id: Optional[str] = None
    ):
        """
        Initialise le collecteur de métriques temps réel
        
        Args:
            config: Configuration du streaming
            creator_type: Type de créateur pour les métriques spécialisées
            model_id: Identifiant du modèle ML
        """
        self.config = config
        self.creator_type = creator_type
        self.model_id = model_id
        
        # Buffers et stockage en mémoire
        self.metrics_buffer = deque(maxlen=config.buffer_size)
        self.metrics_by_type = defaultdict(deque)
        self.aggregated_metrics = defaultdict(dict)
        
        # État du collecteur
        self.collector_state = {
            "running": False,
            "started_at": None,
            "metrics_collected": 0,
            "metrics_processed": 0,
            "errors_count": 0,
            "last_flush": None,
            "buffer_usage": 0.0,
            "throughput_mps": 0.0  # metrics per second
        }
        
        # Threading et async
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.streaming_thread: Optional[threading.Thread] = None
        self.flush_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Définitions des métriques
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        
        # Callbacks et hooks
        self.metric_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.flush_callbacks: List[Callable] = []
        
        # Performance tracking
        self.performance_stats = {
            "collection_latency_ms": deque(maxlen=1000),
            "processing_latency_ms": deque(maxlen=1000),
            "flush_latency_ms": deque(maxlen=1000),
            "memory_usage_mb": deque(maxlen=100)
        }
        
        # Copyright protection
        self._display_copyright_notice()
        
        # Initialize default metrics
        self._initialize_default_metrics()
        
        logger.info(f"⚡ RealTimeMetricsCollector initialized")
        logger.info(f"📊 Creator: {creator_type.value if creator_type else 'All'}")
        logger.info(f"🏷️  Model: {model_id or 'All'}")
        logger.info(f"⚙️  Buffer size: {config.buffer_size}")
        logger.info(f"🔄 Flush interval: {config.flush_interval_seconds}s")
    
    def _display_copyright_notice(self):
        """Afficher la notice de protection des droits d'auteur"""
        logger.info("="*80)
        logger.info("⚡ Real-Time Metrics Collector - Enterprise MLOps")
        logger.info("🔒 PROPRIETARY SOFTWARE - Fahed Mlaiel (mlaiel@live.de)")
        logger.info("⚠️  Unauthorized use, reproduction, or distribution is prohibited")
        logger.info("="*80)
    
    def _initialize_default_metrics(self):
        """Initialise les métriques par défaut"""
        
        # Métriques de performance ML
        self.register_metric(MetricDefinition(
            name="model_accuracy",
            metric_type=MetricType.PERFORMANCE,
            description="Model prediction accuracy",
            unit="percentage",
            aggregation_method=MetricAggregation.AVERAGE,
            business_critical=True,
            alert_thresholds={"warning": 0.85, "critical": 0.75}
        ))
        
        self.register_metric(MetricDefinition(
            name="model_latency",
            metric_type=MetricType.PERFORMANCE,
            description="Model inference latency",
            unit="milliseconds",
            aggregation_method=MetricAggregation.PERCENTILE_95,
            business_critical=True,
            alert_thresholds={"warning": 100, "critical": 500}
        ))
        
        self.register_metric(MetricDefinition(
            name="model_throughput",
            metric_type=MetricType.PERFORMANCE,
            description="Model predictions per second",
            unit="rps",
            aggregation_method=MetricAggregation.RATE,
            business_critical=True
        ))
        
        # Métriques business
        self.register_metric(MetricDefinition(
            name="user_engagement_rate",
            metric_type=MetricType.BUSINESS,
            description="User engagement with recommendations",
            unit="percentage",
            aggregation_method=MetricAggregation.AVERAGE,
            business_critical=True,
            creator_specific=True
        ))
        
        self.register_metric(MetricDefinition(
            name="creator_satisfaction_score",
            metric_type=MetricType.BUSINESS,
            description="Creator satisfaction with platform",
            unit="score",
            aggregation_method=MetricAggregation.AVERAGE,
            business_critical=True,
            creator_specific=True
        ))
        
        self.register_metric(MetricDefinition(
            name="revenue_per_user",
            metric_type=MetricType.BUSINESS,
            description="Average revenue per user",
            unit="currency",
            aggregation_method=MetricAggregation.AVERAGE,
            business_critical=True
        ))
        
        # Métriques techniques
        self.register_metric(MetricDefinition(
            name="api_response_time",
            metric_type=MetricType.TECHNICAL,
            description="API endpoint response time",
            unit="milliseconds",
            aggregation_method=MetricAggregation.PERCENTILE_95,
            alert_thresholds={"warning": 200, "critical": 1000}
        ))
        
        self.register_metric(MetricDefinition(
            name="error_rate",
            metric_type=MetricType.TECHNICAL,
            description="API error rate",
            unit="percentage",
            aggregation_method=MetricAggregation.RATE,
            alert_thresholds={"warning": 0.01, "critical": 0.05}
        ))
        
        # Métriques spécifiques aux créateurs
        if self.creator_type:
            self._initialize_creator_specific_metrics()
        
        logger.info(f"✅ Initialized {len(self.metric_definitions)} default metrics")
    
    def _initialize_creator_specific_metrics(self):
        """Initialise les métriques spécifiques au type de créateur"""
        
        if self.creator_type == CreatorType.MUSICIAN:
            self.register_metric(MetricDefinition(
                name="audio_quality_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Audio quality assessment score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="genre_classification_confidence",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Genre classification confidence",
                unit="percentage",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="audio_processing_time",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Audio processing time",
                unit="milliseconds",
                aggregation_method=MetricAggregation.PERCENTILE_95,
                creator_specific=True
            ))
        
        elif self.creator_type == CreatorType.BLOGGER:
            self.register_metric(MetricDefinition(
                name="content_readability_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Content readability score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="seo_optimization_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="SEO optimization score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="content_sentiment_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Content sentiment analysis score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
        
        elif self.creator_type == CreatorType.PHOTOGRAPHER:
            self.register_metric(MetricDefinition(
                name="image_quality_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Image quality assessment score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="aesthetic_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Image aesthetic quality score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="composition_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Image composition quality score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
        
        elif self.creator_type == CreatorType.INFLUENCER:
            self.register_metric(MetricDefinition(
                name="engagement_growth_rate",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Engagement growth rate",
                unit="percentage",
                aggregation_method=MetricAggregation.RATE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="reach_efficiency",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Content reach efficiency",
                unit="ratio",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="brand_alignment_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Brand alignment score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
        
        elif self.creator_type == CreatorType.COMEDIAN:
            self.register_metric(MetricDefinition(
                name="humor_effectiveness_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Humor effectiveness score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="audience_laughter_rate",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Audience laughter detection rate",
                unit="percentage",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
            
            self.register_metric(MetricDefinition(
                name="timing_precision_score",
                metric_type=MetricType.CREATOR_SPECIFIC,
                description="Comedy timing precision score",
                unit="score",
                aggregation_method=MetricAggregation.AVERAGE,
                creator_specific=True
            ))
        
        logger.info(f"✅ Initialized {self.creator_type.value} specific metrics")
    
    def register_metric(self, metric_def: MetricDefinition):
        """Enregistre une nouvelle définition de métrique"""
        self.metric_definitions[metric_def.name] = metric_def
        logger.debug(f"📊 Registered metric: {metric_def.name}")
    
    def start_collection(self) -> bool:
        """Démarre la collecte de métriques en temps réel"""
        try:
            if self.collector_state["running"]:
                logger.warning("⚠️  Metrics collection already running")
                return True
            
            self.collector_state["running"] = True
            self.collector_state["started_at"] = datetime.now()
            self.stop_event.clear()
            
            # Start streaming thread
            self.streaming_thread = threading.Thread(
                target=self._streaming_loop,
                daemon=True
            )
            self.streaming_thread.start()
            
            # Start flush thread
            self.flush_thread = threading.Thread(
                target=self._flush_loop,
                daemon=True
            )
            self.flush_thread.start()
            
            logger.info("🚀 Real-time metrics collection started")
            logger.info(f"⚙️  Mode: {self.config.streaming_mode.value}")
            logger.info(f"🔄 Flush interval: {self.config.flush_interval_seconds}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start metrics collection: {e}")
            self.collector_state["errors_count"] += 1
            return False
    
    def stop_collection(self):
        """Arrête la collecte de métriques"""
        try:
            logger.info("⏹️  Stopping metrics collection...")
            
            self.collector_state["running"] = False
            self.stop_event.set()
            
            # Wait for threads to finish
            if self.streaming_thread and self.streaming_thread.is_alive():
                self.streaming_thread.join(timeout=5.0)
            
            if self.flush_thread and self.flush_thread.is_alive():
                self.flush_thread.join(timeout=5.0)
            
            # Final flush
            self._flush_metrics()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info("🛑 Metrics collection stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping metrics collection: {e}")
    
    def collect_metric(
        self,
        metric_name: str,
        value: Union[float, int, str, bool],
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None,
        **metadata
    ) -> bool:
        """
        Collecte une métrique individuelle
        
        Args:
            metric_name: Nom de la métrique
            value: Valeur de la métrique
            tags: Tags additionnels
            timestamp: Timestamp (défaut: maintenant)
            **metadata: Métadonnées additionnelles
        
        Returns:
            bool: True si la métrique a été collectée avec succès
        """
        try:
            start_time = time.time()
            
            # Validate metric
            if metric_name not in self.metric_definitions:
                logger.warning(f"⚠️  Unknown metric: {metric_name}")
                # Don't reject unknown metrics in production - just log
            
            # Create metric point
            metric_point = MetricPoint(
                timestamp=timestamp or datetime.now(),
                metric_name=metric_name,
                value=value,
                tags=tags or {},
                creator_type=self.creator_type,
                model_id=self.model_id,
                metadata=metadata
            )
            
            # Add to buffer
            self.metrics_buffer.append(metric_point)
            
            # Add to type-specific buffer
            metric_def = self.metric_definitions.get(metric_name)
            if metric_def:
                self.metrics_by_type[metric_def.metric_type].append(metric_point)
            
            # Update state
            self.collector_state["metrics_collected"] += 1
            self.collector_state["buffer_usage"] = len(self.metrics_buffer) / self.config.buffer_size
            
            # Track performance
            collection_time = (time.time() - start_time) * 1000
            self.performance_stats["collection_latency_ms"].append(collection_time)
            
            # Execute callbacks
            for callback in self.metric_callbacks.get(metric_name, []):
                try:
                    callback(metric_point)
                except Exception as e:
                    logger.error(f"❌ Error in metric callback: {e}")
            
            logger.debug(f"📊 Collected metric: {metric_name} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error collecting metric {metric_name}: {e}")
            self.collector_state["errors_count"] += 1
            return False
    
    def collect_batch_metrics(self, metrics: List[Dict[str, Any]]) -> int:
        """
        Collecte un batch de métriques
        
        Args:
            metrics: Liste de dictionnaires contenant les métriques
        
        Returns:
            int: Nombre de métriques collectées avec succès
        """
        collected_count = 0
        
        for metric in metrics:
            try:
                metric_name = metric.get("name")
                value = metric.get("value")
                tags = metric.get("tags", {})
                timestamp_str = metric.get("timestamp")
                
                timestamp = None
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                
                if self.collect_metric(metric_name, value, tags, timestamp, **metric.get("metadata", {})):
                    collected_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Error in batch metric collection: {e}")
                self.collector_state["errors_count"] += 1
        
        logger.info(f"📊 Collected {collected_count}/{len(metrics)} batch metrics")
        return collected_count
    
    def _streaming_loop(self):
        """Boucle principale de streaming des métriques"""
        logger.info("🔄 Starting metrics streaming loop...")
        
        while not self.stop_event.is_set():
            try:
                start_time = time.time()
                
                # Process metrics buffer
                if self.metrics_buffer:
                    self._process_metrics_buffer()
                
                # Update throughput calculation
                processing_time = time.time() - start_time
                if processing_time > 0:
                    metrics_processed = self.collector_state["metrics_processed"]
                    throughput = metrics_processed / ((time.time() - self.collector_state["started_at"].timestamp()) + 1)
                    self.collector_state["throughput_mps"] = throughput
                
                # Track processing latency
                self.performance_stats["processing_latency_ms"].append(processing_time * 1000)
                
                # Sleep based on mode
                if self.config.high_throughput_mode:
                    time.sleep(0.01)  # 10ms for high throughput
                else:
                    time.sleep(0.1)   # 100ms for normal mode
                
            except Exception as e:
                logger.error(f"❌ Error in streaming loop: {e}")
                self.collector_state["errors_count"] += 1
                time.sleep(1)  # Error recovery delay
    
    def _process_metrics_buffer(self):
        """Traite le buffer de métriques"""
        try:
            batch_size = min(len(self.metrics_buffer), self.config.batch_size)
            
            if batch_size == 0:
                return
            
            # Extract batch from buffer
            batch = []
            for _ in range(batch_size):
                if self.metrics_buffer:
                    batch.append(self.metrics_buffer.popleft())
            
            # Process batch
            if batch:
                self._process_metrics_batch(batch)
                self.collector_state["metrics_processed"] += len(batch)
            
        except Exception as e:
            logger.error(f"❌ Error processing metrics buffer: {e}")
            self.collector_state["errors_count"] += 1
    
    def _process_metrics_batch(self, batch: List[MetricPoint]):
        """Traite un batch de métriques"""
        try:
            # Group by metric name for aggregation
            metrics_by_name = defaultdict(list)
            
            for metric_point in batch:
                metrics_by_name[metric_point.metric_name].append(metric_point)
            
            # Process each metric group
            for metric_name, points in metrics_by_name.items():
                self._aggregate_metric_points(metric_name, points)
            
            logger.debug(f"📊 Processed batch of {len(batch)} metrics")
            
        except Exception as e:
            logger.error(f"❌ Error processing metrics batch: {e}")
    
    def _aggregate_metric_points(self, metric_name: str, points: List[MetricPoint]):
        """Agrège les points de métriques selon la méthode définie"""
        try:
            metric_def = self.metric_definitions.get(metric_name)
            if not metric_def:
                return
            
            # Extract numeric values
            numeric_values = []
            for point in points:
                try:
                    if isinstance(point.value, (int, float)):
                        numeric_values.append(float(point.value))
                except (ValueError, TypeError):
                    continue
            
            if not numeric_values:
                return
            
            # Calculate aggregation
            aggregated_value = self._calculate_aggregation(
                numeric_values, 
                metric_def.aggregation_method
            )
            
            # Store aggregated result
            current_time = datetime.now()
            time_window = f"{current_time.strftime('%Y-%m-%d_%H-%M')}"
            
            if metric_name not in self.aggregated_metrics:
                self.aggregated_metrics[metric_name] = {}
            
            self.aggregated_metrics[metric_name][time_window] = {
                "value": aggregated_value,
                "count": len(points),
                "timestamp": current_time,
                "aggregation_method": metric_def.aggregation_method.value
            }
            
            logger.debug(f"📊 Aggregated {metric_name}: {aggregated_value} ({len(points)} points)")
            
        except Exception as e:
            logger.error(f"❌ Error aggregating metrics for {metric_name}: {e}")
    
    def _calculate_aggregation(
        self, 
        values: List[float], 
        method: MetricAggregation
    ) -> float:
        """Calcule l'agrégation selon la méthode spécifiée"""
        try:
            if not values:
                return 0.0
            
            if method == MetricAggregation.SUM:
                return sum(values)
            elif method == MetricAggregation.AVERAGE:
                return sum(values) / len(values)
            elif method == MetricAggregation.COUNT:
                return len(values)
            elif method == MetricAggregation.MIN:
                return min(values)
            elif method == MetricAggregation.MAX:
                return max(values)
            elif method == MetricAggregation.MEDIAN:
                if PANDAS_NUMPY_AVAILABLE:
                    return float(np.median(values))
                else:
                    sorted_values = sorted(values)
                    n = len(sorted_values)
                    return sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
            elif method == MetricAggregation.PERCENTILE_95:
                if PANDAS_NUMPY_AVAILABLE:
                    return float(np.percentile(values, 95))
                else:
                    sorted_values = sorted(values)
                    index = int(0.95 * (len(sorted_values) - 1))
                    return sorted_values[index]
            elif method == MetricAggregation.PERCENTILE_99:
                if PANDAS_NUMPY_AVAILABLE:
                    return float(np.percentile(values, 99))
                else:
                    sorted_values = sorted(values)
                    index = int(0.99 * (len(sorted_values) - 1))
                    return sorted_values[index]
            elif method == MetricAggregation.LATEST:
                return values[-1]
            elif method == MetricAggregation.RATE:
                # Simple rate calculation (could be enhanced)
                return len(values) / max(1, len(values) // 60)  # per minute
            else:
                return sum(values) / len(values)  # Default to average
                
        except Exception as e:
            logger.error(f"❌ Error calculating aggregation: {e}")
            return 0.0
    
    def _flush_loop(self):
        """Boucle de flush périodique des métriques"""
        logger.info("🔄 Starting metrics flush loop...")
        
        while not self.stop_event.is_set():
            try:
                # Wait for flush interval
                if self.stop_event.wait(self.config.flush_interval_seconds):
                    break  # Stop event was set
                
                # Perform flush
                self._flush_metrics()
                
            except Exception as e:
                logger.error(f"❌ Error in flush loop: {e}")
                self.collector_state["errors_count"] += 1
                time.sleep(1)  # Error recovery delay
    
    def _flush_metrics(self):
        """Flush les métriques vers le stockage/monitoring externe"""
        try:
            start_time = time.time()
            
            if not self.aggregated_metrics:
                return
            
            # Prepare flush data
            flush_data = {
                "timestamp": datetime.now().isoformat(),
                "model_id": self.model_id,
                "creator_type": self.creator_type.value if self.creator_type else None,
                "metrics": dict(self.aggregated_metrics),
                "collector_state": self.collector_state.copy()
            }
            
            # Execute flush callbacks
            for callback in self.flush_callbacks:
                try:
                    callback(flush_data)
                except Exception as e:
                    logger.error(f"❌ Error in flush callback: {e}")
            
            # Log flush summary
            metrics_count = len(self.aggregated_metrics)
            flush_time = (time.time() - start_time) * 1000
            
            self.performance_stats["flush_latency_ms"].append(flush_time)
            self.collector_state["last_flush"] = datetime.now()
            
            logger.debug(f"📊 Flushed {metrics_count} aggregated metrics in {flush_time:.2f}ms")
            
            # Clear aggregated metrics after flush (keep some history if needed)
            self._cleanup_old_aggregations()
            
        except Exception as e:
            logger.error(f"❌ Error flushing metrics: {e}")
            self.collector_state["errors_count"] += 1
    
    def _cleanup_old_aggregations(self):
        """Nettoie les anciennes agrégations"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)  # Keep 1 hour of aggregations
            
            for metric_name in list(self.aggregated_metrics.keys()):
                metric_data = self.aggregated_metrics[metric_name]
                
                # Remove old time windows
                for time_window in list(metric_data.keys()):
                    if metric_data[time_window]["timestamp"] < cutoff_time:
                        del metric_data[time_window]
                
                # Remove empty metrics
                if not metric_data:
                    del self.aggregated_metrics[metric_name]
                    
        except Exception as e:
            logger.error(f"❌ Error cleaning up aggregations: {e}")
    
    # Public API methods
    
    def add_metric_callback(self, metric_name: str, callback: Callable[[MetricPoint], None]):
        """Ajoute un callback pour une métrique spécifique"""
        self.metric_callbacks[metric_name].append(callback)
        logger.debug(f"📊 Added callback for metric: {metric_name}")
    
    def add_flush_callback(self, callback: Callable[[Dict], None]):
        """Ajoute un callback pour le flush des métriques"""
        self.flush_callbacks.append(callback)
        logger.debug("📊 Added flush callback")
    
    def get_collector_status(self) -> Dict[str, Any]:
        """Obtient le statut du collecteur"""
        return {
            "state": self.collector_state.copy(),
            "config": {
                "buffer_size": self.config.buffer_size,
                "flush_interval": self.config.flush_interval_seconds,
                "batch_size": self.config.batch_size,
                "streaming_mode": self.config.streaming_mode.value,
                "high_throughput_mode": self.config.high_throughput_mode
            },
            "metrics_definitions": len(self.metric_definitions),
            "creator_type": self.creator_type.value if self.creator_type else None,
            "model_id": self.model_id,
            "buffer_usage_percent": self.collector_state["buffer_usage"] * 100,
            "performance": self._get_performance_summary()
        }
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Obtient un résumé des performances"""
        try:
            summary = {}
            
            for metric_name, values in self.performance_stats.items():
                if values:
                    if PANDAS_NUMPY_AVAILABLE:
                        summary[metric_name] = {
                            "avg": float(np.mean(values)),
                            "min": float(np.min(values)),
                            "max": float(np.max(values)),
                            "p95": float(np.percentile(values, 95)),
                            "count": len(values)
                        }
                    else:
                        # Simple calculations without numpy
                        sorted_values = sorted(values)
                        summary[metric_name] = {
                            "avg": sum(values) / len(values),
                            "min": min(values),
                            "max": max(values),
                            "p95": sorted_values[int(0.95 * (len(sorted_values) - 1))],
                            "count": len(values)
                        }
                else:
                    summary[metric_name] = {"count": 0}
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating performance summary: {e}")
            return {}
    
    def get_metrics_summary(self, hours_back: int = 1) -> Dict[str, Any]:
        """Obtient un résumé des métriques collectées"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            summary = {
                "period_hours": hours_back,
                "metrics_by_type": defaultdict(list),
                "top_metrics": [],
                "alert_worthy_metrics": []
            }
            
            # Analyze aggregated metrics
            for metric_name, time_windows in self.aggregated_metrics.items():
                metric_def = self.metric_definitions.get(metric_name)
                
                # Get recent values
                recent_values = []
                for time_window, data in time_windows.items():
                    if data["timestamp"] > cutoff_time:
                        recent_values.append(data["value"])
                
                if recent_values and metric_def:
                    avg_value = sum(recent_values) / len(recent_values)
                    
                    summary["metrics_by_type"][metric_def.metric_type.value].append({
                        "name": metric_name,
                        "average_value": avg_value,
                        "sample_count": len(recent_values),
                        "unit": metric_def.unit
                    })
                    
                    # Check for alert thresholds
                    if metric_def.alert_thresholds:
                        for threshold_type, threshold_value in metric_def.alert_thresholds.items():
                            if (threshold_type == "warning" and avg_value < threshold_value) or \
                               (threshold_type == "critical" and avg_value < threshold_value):
                                summary["alert_worthy_metrics"].append({
                                    "name": metric_name,
                                    "value": avg_value,
                                    "threshold": threshold_value,
                                    "threshold_type": threshold_type
                                })
            
            # Top metrics by volume
            summary["top_metrics"] = sorted(
                [(name, len(windows)) for name, windows in self.aggregated_metrics.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return dict(summary)
            
        except Exception as e:
            logger.error(f"❌ Error generating metrics summary: {e}")
            return {"error": str(e)}
    
    def export_metrics(self, filepath: str, hours_back: int = 24):
        """Exporte les métriques vers un fichier"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            export_data = {
                "export_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "creator_type": self.creator_type.value if self.creator_type else None,
                    "model_id": self.model_id,
                    "period_hours": hours_back,
                    "collector_version": "1.0.0"
                },
                "collector_status": self.get_collector_status(),
                "metrics_definitions": {
                    name: {
                        "metric_type": defn.metric_type.value,
                        "description": defn.description,
                        "unit": defn.unit,
                        "aggregation_method": defn.aggregation_method.value,
                        "creator_specific": defn.creator_specific,
                        "business_critical": defn.business_critical
                    }
                    for name, defn in self.metric_definitions.items()
                },
                "aggregated_metrics": {},
                "performance_stats": dict(self.performance_stats)
            }
            
            # Export recent aggregated metrics
            for metric_name, time_windows in self.aggregated_metrics.items():
                recent_data = {}
                for time_window, data in time_windows.items():
                    if data["timestamp"] > cutoff_time:
                        recent_data[time_window] = {
                            "value": data["value"],
                            "count": data["count"],
                            "timestamp": data["timestamp"].isoformat(),
                            "aggregation_method": data["aggregation_method"]
                        }
                
                if recent_data:
                    export_data["aggregated_metrics"][metric_name] = recent_data
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"📊 Metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting metrics: {e}")
            raise

# Factory functions for easy usage

def create_real_time_collector(
    creator_type: str,
    model_id: str,
    buffer_size: int = 10000,
    flush_interval: int = 5,
    high_throughput: bool = False
) -> RealTimeMetricsCollector:
    """
    Factory function pour créer un collecteur de métriques temps réel
    
    Args:
        creator_type: Type de créateur (musician, blogger, photographer, influencer, comedian)
        model_id: Identifiant du modèle
        buffer_size: Taille du buffer
        flush_interval: Intervalle de flush en secondes
        high_throughput: Mode haute performance
    
    Returns:
        Instance configurée de RealTimeMetricsCollector
    """
    
    # Convert string to enum
    try:
        creator_enum = CreatorType(creator_type.lower())
    except ValueError:
        logger.warning(f"⚠️  Unknown creator type: {creator_type}, using ALL")
        creator_enum = CreatorType.ALL
    
    # Create configuration
    config = StreamingConfig(
        buffer_size=buffer_size,
        flush_interval_seconds=flush_interval,
        high_throughput_mode=high_throughput,
        streaming_mode=StreamingMode.HYBRID if not high_throughput else StreamingMode.PUSH
    )
    
    # Create collector
    collector = RealTimeMetricsCollector(
        config=config,
        creator_type=creator_enum,
        model_id=model_id
    )
    
    logger.info(f"⚡ Created real-time metrics collector for {creator_type} model {model_id}")
    
    return collector

# Enterprise usage example
if __name__ == "__main__":
    """
    Exemple d'utilisation enterprise du collecteur de métriques temps réel
    """
    
    def example_flush_callback(flush_data):
        """Exemple de callback de flush pour envoyer vers un système de monitoring"""
        logger.info(f"📊 FLUSH: {len(flush_data['metrics'])} metrics aggregated")
        # Ici, on enverrait les données vers Prometheus, InfluxDB, etc.
    
    def example_metric_callback(metric_point):
        """Exemple de callback pour traiter des métriques en temps réel"""
        if metric_point.metric_name == "model_accuracy" and metric_point.value < 0.8:
            logger.warning(f"🚨 Low accuracy detected: {metric_point.value}")
    
    # Create collector for musician creator
    collector = create_real_time_collector(
        creator_type="musician",
        model_id="ainflue_music_recommendation_v3",
        buffer_size=5000,
        flush_interval=10,
        high_throughput=False
    )
    
    # Add callbacks
    collector.add_flush_callback(example_flush_callback)
    collector.add_metric_callback("model_accuracy", example_metric_callback)
    
    # Start collection
    collector.start_collection()
    
    try:
        # Simulate metrics collection
        import random
        
        logger.info("🎵 Simulating musician metrics collection...")
        
        for i in range(100):
            # Simulate model performance metrics
            collector.collect_metric("model_accuracy", 0.85 + random.uniform(-0.1, 0.1))
            collector.collect_metric("model_latency", 50 + random.uniform(-20, 30))
            collector.collect_metric("model_throughput", 100 + random.uniform(-20, 40))
            
            # Simulate musician-specific metrics
            collector.collect_metric("audio_quality_score", 0.9 + random.uniform(-0.1, 0.1))
            collector.collect_metric("genre_classification_confidence", 0.88 + random.uniform(-0.1, 0.1))
            collector.collect_metric("audio_processing_time", 200 + random.uniform(-50, 100))
            
            # Simulate business metrics
            collector.collect_metric("user_engagement_rate", 0.75 + random.uniform(-0.1, 0.1))
            collector.collect_metric("creator_satisfaction_score", 4.2 + random.uniform(-0.5, 0.5))
            
            time.sleep(0.1)  # 100ms between metrics
        
        # Wait for processing
        time.sleep(5)
        
        # Get status and summary
        status = collector.get_collector_status()
        logger.info(f"📊 Collector Status: {json.dumps(status, indent=2, default=str)}")
        
        summary = collector.get_metrics_summary(hours_back=1)
        logger.info(f"📈 Metrics Summary: {json.dumps(summary, indent=2, default=str)}")
        
        # Export data
        collector.export_metrics("/tmp/metrics_export.json", hours_back=1)
        
    finally:
        # Stop collection
        collector.stop_collection()
        logger.info("✅ Demo completed successfully")