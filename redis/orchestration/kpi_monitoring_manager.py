#!/usr/bin/env python3
"""📈 KPI Monitoring Manager - Advanced Key Performance Indicator Tracking
=========================================================================
Expert: BUSINESS ANALYST + DATA ENGINEER + BACKEND SENIOR + ML ENGINEER
Technologies: KPI Analytics + Performance Monitoring + Business Intelligence + Predictive Analytics
Architecture: Level 3 - KPI Intelligence Layer
Date: 2025-01-14

Ultra-advanced KPI monitoring system with intelligent threshold management,
predictive KPI forecasting, and automated business intelligence insights.
=========================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
=========================================================================
"""

import asyncio
import logging
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis
import statistics
import math
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class KPICategory(Enum):
    """Catégories de KPI"""
    BUSINESS = "business"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    CREATOR_ECONOMY = "creator_economy"
    USER_ENGAGEMENT = "user_engagement"
    CONTENT_PERFORMANCE = "content_performance"
    PLATFORM_HEALTH = "platform_health"
    SECURITY = "security"
    GROWTH = "growth"

class KPIType(Enum):
    """Types de KPI"""
    COUNTER = "counter"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    AVERAGE = "average"
    RATE = "rate"
    CUMULATIVE = "cumulative"
    TREND = "trend"
    INDEX = "index"

class KPIStatus(Enum):
    """États des KPI"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    IMPROVING = "improving"
    DECLINING = "declining"

class ThresholdType(Enum):
    """Types de seuil"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    ADAPTIVE = "adaptive"
    SEASONAL = "seasonal"
    PREDICTIVE = "predictive"

class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class KPIThreshold:
    """Seuil de KPI"""
    threshold_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    threshold_type: ThresholdType = ThresholdType.STATIC
    warning_value: float = 0.0
    critical_value: float = 0.0
    excellent_value: Optional[float] = None
    is_lower_better: bool = False  # True si valeur plus basse = meilleur
    calculation_method: str = "simple"
    historical_data_points: int = 30
    adaptive_factor: float = 0.1
    seasonal_pattern: Optional[str] = None
    is_active: bool = True

@dataclass
class KPIDefinition:
    """Définition d'un KPI"""
    kpi_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: KPICategory = KPICategory.BUSINESS
    kpi_type: KPIType = KPIType.COUNTER
    unit: str = ""
    calculation_formula: str = ""
    data_sources: List[str] = field(default_factory=list)
    aggregation_period: timedelta = timedelta(hours=1)
    threshold: Optional[KPIThreshold] = None
    target_value: Optional[float] = None
    benchmark_value: Optional[float] = None
    weight: float = 1.0  # Importance relative
    is_business_critical: bool = False
    tags: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class KPIMeasurement:
    """Mesure d'un KPI"""
    measurement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    kpi_id: str = ""
    value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    calculation_details: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 1.0  # 0-1, qualité de la mesure
    confidence_interval: Optional[Tuple[float, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KPIAlert:
    """Alerte KPI"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    kpi_id: str = ""
    alert_level: AlertLevel = AlertLevel.WARNING
    message: str = ""
    current_value: float = 0.0
    threshold_value: float = 0.0
    deviation_percentage: float = 0.0
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    auto_resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class KPITrend:
    """Tendance KPI"""
    trend_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    kpi_id: str = ""
    trend_direction: str = "stable"  # improving, declining, stable
    trend_strength: float = 0.0  # -1 à 1
    trend_duration: timedelta = timedelta(days=0)
    slope: float = 0.0
    r_squared: float = 0.0
    confidence: float = 0.0
    forecast_value: Optional[float] = None
    forecast_horizon: Optional[timedelta] = None
    calculated_at: datetime = field(default_factory=datetime.now)

@dataclass
class KPIReport:
    """Rapport KPI"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: KPICategory = KPICategory.BUSINESS
    kpis: List[str] = field(default_factory=list)  # KPI IDs
    time_period: Tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now(), datetime.now()))
    summary: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    generated_by: str = ""

@dataclass
class KPIMonitoringConfig:
    """Configuration du gestionnaire KPI"""
    calculation_interval: timedelta = timedelta(minutes=5)
    threshold_check_interval: timedelta = timedelta(minutes=1)
    trend_analysis_interval: timedelta = timedelta(hours=1)
    historical_data_retention: timedelta = timedelta(days=90)
    enable_predictive_analytics: bool = True
    enable_anomaly_detection: bool = True
    enable_auto_threshold_adjustment: bool = True
    max_concurrent_calculations: int = 10
    cache_duration: timedelta = timedelta(minutes=5)
    alert_cooldown_period: timedelta = timedelta(minutes=15)
    min_data_points_for_trend: int = 10
    confidence_threshold: float = 0.7

class RedisKPIMonitoringManager:
    """Gestionnaire de monitoring KPI Redis enterprise"""
    
    def __init__(self, config: KPIMonitoringConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client or redis.Redis()
        self.is_running = False
        
        # Composants internes
        self.kpi_definitions = {}
        self.active_alerts = {}
        self.measurement_cache = defaultdict(lambda: deque(maxlen=1000))
        self.trend_cache = {}
        
        # Calculateurs et analyseurs
        self.calculation_queue = asyncio.Queue()
        self.trend_analyzer = KPITrendAnalyzer()
        self.threshold_manager = DynamicThresholdManager()
        
        # Métriques du gestionnaire
        self.manager_metrics = {
            'kpis_monitored': 0,
            'measurements_calculated': 0,
            'alerts_triggered': 0,
            'trends_analyzed': 0,
            'avg_calculation_time': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'last_calculation': None,
            'uptime_start': datetime.now()
        }
        
        # Tâches asynchrones
        self.calculation_task = None
        self.threshold_task = None
        self.trend_task = None
        self.cleanup_task = None
    
    async def initialize(self) -> bool:
        """Initialise le gestionnaire KPI"""
        try:
            logger.info("📈 Initializing KPI Monitoring Manager...")
            
            # Charger les définitions KPI
            await self._load_kpi_definitions()
            
            # Charger les données historiques
            await self._load_historical_measurements()
            
            # Créer des KPI par défaut si aucun n'existe
            if not self.kpi_definitions:
                await self._create_default_kpis()
            
            # Démarrer les tâches de fond
            await self._start_background_tasks()
            
            self.is_running = True
            logger.info("✅ KPI Monitoring Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize KPI Monitoring Manager: {e}")
            return False
    
    async def _load_kpi_definitions(self):
        """Charge les définitions KPI"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("kpi:definitions:*")]
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    kpi_data = json.loads(data)
                    
                    # Reconstituer l'objet KPIDefinition
                    if 'threshold' in kpi_data and kpi_data['threshold']:
                        threshold = KPIThreshold(**kpi_data['threshold'])
                        kpi_data['threshold'] = threshold
                    
                    kpi = KPIDefinition(**kpi_data)
                    self.kpi_definitions[kpi.kpi_id] = kpi
            
            logger.info(f"✅ Loaded {len(self.kpi_definitions)} KPI definitions")
            
        except Exception as e:
            logger.error(f"❌ Failed to load KPI definitions: {e}")
    
    async def _load_historical_measurements(self):
        """Charge les mesures historiques"""
        try:
            for kpi_id in self.kpi_definitions.keys():
                # Charger les dernières mesures
                key = f"kpi:measurements:{kpi_id}"
                measurements = self.redis_client.zrevrange(key, 0, 999, withscores=True)
                
                for measurement_data, timestamp in measurements:
                    if isinstance(measurement_data, bytes):
                        measurement_data = measurement_data.decode()
                    
                    try:
                        data = json.loads(measurement_data)
                        measurement = KPIMeasurement(**data)
                        self.measurement_cache[kpi_id].append(measurement)
                    except (json.JSONDecodeError, TypeError):
                        continue
            
            total_measurements = sum(len(cache) for cache in self.measurement_cache.values())
            logger.info(f"✅ Loaded {total_measurements} historical measurements")
            
        except Exception as e:
            logger.error(f"❌ Failed to load historical measurements: {e}")
    
    async def _create_default_kpis(self):
        """Crée des KPI par défaut"""
        try:
            default_kpis = [
                # KPI Business
                KPIDefinition(
                    name="Active Users",
                    description="Number of active users in the system",
                    category=KPICategory.USER_ENGAGEMENT,
                    kpi_type=KPIType.COUNTER,
                    unit="users",
                    calculation_formula="count(distinct user_id)",
                    threshold=KPIThreshold(
                        name="Active Users Threshold",
                        warning_value=500,
                        critical_value=200,
                        excellent_value=1000
                    ),
                    target_value=800,
                    is_business_critical=True,
                    created_by="system"
                ),
                
                # KPI Creator Economy
                KPIDefinition(
                    name="Creator Revenue",
                    description="Total revenue generated by creators",
                    category=KPICategory.CREATOR_ECONOMY,
                    kpi_type=KPIType.CUMULATIVE,
                    unit="USD",
                    calculation_formula="sum(creator_earnings)",
                    threshold=KPIThreshold(
                        name="Creator Revenue Threshold",
                        warning_value=10000,
                        critical_value=5000,
                        excellent_value=25000
                    ),
                    target_value=20000,
                    is_business_critical=True,
                    created_by="system"
                ),
                
                # KPI Performance
                KPIDefinition(
                    name="System Response Time",
                    description="Average system response time",
                    category=KPICategory.TECHNICAL,
                    kpi_type=KPIType.AVERAGE,
                    unit="ms",
                    calculation_formula="avg(response_time)",
                    threshold=KPIThreshold(
                        name="Response Time Threshold",
                        warning_value=200,
                        critical_value=500,
                        excellent_value=50,
                        is_lower_better=True
                    ),
                    target_value=100,
                    is_business_critical=True,
                    created_by="system"
                ),
                
                # KPI Content
                KPIDefinition(
                    name="Content Upload Rate",
                    description="Rate of content uploads per hour",
                    category=KPICategory.CONTENT_PERFORMANCE,
                    kpi_type=KPIType.RATE,
                    unit="uploads/hour",
                    calculation_formula="count(uploads) / hour",
                    threshold=KPIThreshold(
                        name="Upload Rate Threshold",
                        warning_value=50,
                        critical_value=20,
                        excellent_value=200
                    ),
                    target_value=100,
                    created_by="system"
                ),
                
                # KPI Engagement
                KPIDefinition(
                    name="User Engagement Rate",
                    description="Percentage of users actively engaging with content",
                    category=KPICategory.USER_ENGAGEMENT,
                    kpi_type=KPIType.PERCENTAGE,
                    unit="%",
                    calculation_formula="(engaged_users / total_users) * 100",
                    threshold=KPIThreshold(
                        name="Engagement Rate Threshold",
                        warning_value=15.0,
                        critical_value=10.0,
                        excellent_value=30.0
                    ),
                    target_value=25.0,
                    created_by="system"
                )
            ]
            
            for kpi in default_kpis:
                self.kpi_definitions[kpi.kpi_id] = kpi
                await self._store_kpi_definition(kpi)
            
            self.manager_metrics['kpis_monitored'] = len(self.kpi_definitions)
            logger.info(f"✅ Created {len(default_kpis)} default KPIs")
            
        except Exception as e:
            logger.error(f"❌ Failed to create default KPIs: {e}")
    
    async def _store_kpi_definition(self, kpi: KPIDefinition):
        """Stocke une définition KPI"""
        try:
            key = f"kpi:definitions:{kpi.kpi_id}"
            
            # Sérialiser la définition
            data = {
                'kpi_id': kpi.kpi_id,
                'name': kpi.name,
                'description': kpi.description,
                'category': kpi.category.value,
                'kpi_type': kpi.kpi_type.value,
                'unit': kpi.unit,
                'calculation_formula': kpi.calculation_formula,
                'data_sources': kpi.data_sources,
                'aggregation_period': kpi.aggregation_period.total_seconds(),
                'threshold': self._serialize_threshold(kpi.threshold) if kpi.threshold else None,
                'target_value': kpi.target_value,
                'benchmark_value': kpi.benchmark_value,
                'weight': kpi.weight,
                'is_business_critical': kpi.is_business_critical,
                'tags': kpi.tags,
                'created_by': kpi.created_by,
                'created_at': kpi.created_at.isoformat(),
                'is_active': kpi.is_active
            }
            
            self.redis_client.setex(key, 30 * 24 * 3600, json.dumps(data))
            
        except Exception as e:
            logger.error(f"❌ Failed to store KPI definition: {e}")
    
    def _serialize_threshold(self, threshold: KPIThreshold) -> Dict[str, Any]:
        """Sérialise un seuil KPI"""
        return {
            'threshold_id': threshold.threshold_id,
            'name': threshold.name,
            'threshold_type': threshold.threshold_type.value,
            'warning_value': threshold.warning_value,
            'critical_value': threshold.critical_value,
            'excellent_value': threshold.excellent_value,
            'is_lower_better': threshold.is_lower_better,
            'calculation_method': threshold.calculation_method,
            'historical_data_points': threshold.historical_data_points,
            'adaptive_factor': threshold.adaptive_factor,
            'seasonal_pattern': threshold.seasonal_pattern,
            'is_active': threshold.is_active
        }
    
    async def _start_background_tasks(self):
        """Démarre les tâches de fond"""
        self.calculation_task = asyncio.create_task(self._calculation_loop())
        self.threshold_task = asyncio.create_task(self._threshold_monitoring_loop())
        self.trend_task = asyncio.create_task(self._trend_analysis_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _calculation_loop(self):
        """Boucle de calcul des KPI"""
        while self.is_running:
            try:
                # Calculer tous les KPI actifs
                calculation_tasks = []
                for kpi in self.kpi_definitions.values():
                    if kpi.is_active:
                        task = asyncio.create_task(self._calculate_kpi(kpi))
                        calculation_tasks.append(task)
                
                # Limiter la concurrence
                semaphore = asyncio.Semaphore(self.config.max_concurrent_calculations)
                
                async def limited_calculation(task):
                    async with semaphore:
                        return await task
                
                if calculation_tasks:
                    results = await asyncio.gather(
                        *[limited_calculation(task) for task in calculation_tasks],
                        return_exceptions=True
                    )
                    
                    # Traiter les résultats
                    successful_calculations = sum(1 for result in results if not isinstance(result, Exception))
                    self.manager_metrics['measurements_calculated'] += successful_calculations
                    self.manager_metrics['last_calculation'] = datetime.now()
                
                await asyncio.sleep(self.config.calculation_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Error in calculation loop: {e}")
                await asyncio.sleep(30)
    
    async def _calculate_kpi(self, kpi: KPIDefinition) -> Optional[KPIMeasurement]:
        """Calcule un KPI spécifique"""
        try:
            start_time = time.time()
            
            # Période de calcul
            now = datetime.now()
            period_end = now
            period_start = now - kpi.aggregation_period
            
            # Récupérer les données source
            raw_data = await self._get_kpi_data(kpi, period_start, period_end)
            
            # Calculer la valeur
            value = await self._apply_calculation_formula(kpi, raw_data)
            
            # Calculer la qualité et la confiance
            quality_score = self._calculate_quality_score(raw_data, kpi)
            confidence_interval = self._calculate_confidence_interval(value, raw_data)
            
            # Créer la mesure
            measurement = KPIMeasurement(
                kpi_id=kpi.kpi_id,
                value=value,
                timestamp=now,
                period_start=period_start,
                period_end=period_end,
                raw_data=raw_data,
                calculation_details={
                    'formula': kpi.calculation_formula,
                    'data_points': len(raw_data) if isinstance(raw_data, list) else 1,
                    'calculation_time': time.time() - start_time
                },
                quality_score=quality_score,
                confidence_interval=confidence_interval
            )
            
            # Stocker la mesure
            await self._store_measurement(measurement)
            
            # Ajouter au cache
            self.measurement_cache[kpi.kpi_id].append(measurement)
            
            # Mettre à jour les métriques de performance
            calculation_time = time.time() - start_time
            self.manager_metrics['avg_calculation_time'] = (
                (self.manager_metrics['avg_calculation_time'] * 
                 (self.manager_metrics['measurements_calculated'] - 1) + calculation_time) /
                self.manager_metrics['measurements_calculated']
                if self.manager_metrics['measurements_calculated'] > 0 else calculation_time
            )
            
            return measurement
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate KPI {kpi.name}: {e}")
            return None
    
    async def _get_kpi_data(self, kpi: KPIDefinition, start_time: datetime, end_time: datetime) -> Any:
        """Récupère les données pour le calcul du KPI"""
        try:
            # Simuler la récupération de données selon le KPI
            if kpi.name == "Active Users":
                return np.random.randint(200, 1500)
            elif kpi.name == "Creator Revenue":
                return np.random.uniform(5000, 30000)
            elif kpi.name == "System Response Time":
                return np.random.uniform(30, 400)
            elif kpi.name == "Content Upload Rate":
                return np.random.randint(20, 300)
            elif kpi.name == "User Engagement Rate":
                return np.random.uniform(8, 35)
            else:
                # KPI générique
                return np.random.uniform(0, 100)
                
        except Exception as e:
            logger.error(f"❌ Failed to get KPI data: {e}")
            return 0
    
    async def _apply_calculation_formula(self, kpi: KPIDefinition, raw_data: Any) -> float:
        """Applique la formule de calcul du KPI"""
        try:
            # En production, parser et exécuter la formule réelle
            # Pour la simulation, retourner la donnée directement
            if isinstance(raw_data, (int, float)):
                return float(raw_data)
            elif isinstance(raw_data, list) and raw_data:
                if kpi.kpi_type == KPIType.AVERAGE:
                    return statistics.mean(raw_data)
                elif kpi.kpi_type == KPIType.COUNTER:
                    return len(raw_data)
                elif kpi.kpi_type == KPIType.CUMULATIVE:
                    return sum(raw_data)
                else:
                    return statistics.mean(raw_data)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"❌ Failed to apply calculation formula: {e}")
            return 0.0
    
    def _calculate_quality_score(self, raw_data: Any, kpi: KPIDefinition) -> float:
        """Calcule le score de qualité de la mesure"""
        try:
            # Critères de qualité basiques
            quality_factors = []
            
            # Disponibilité des données
            if raw_data is not None:
                quality_factors.append(1.0)
            else:
                quality_factors.append(0.0)
            
            # Complétude des données
            if isinstance(raw_data, list):
                expected_data_points = max(1, int(kpi.aggregation_period.total_seconds() / 60))  # 1 par minute
                completeness = min(1.0, len(raw_data) / expected_data_points)
                quality_factors.append(completeness)
            else:
                quality_factors.append(0.8)  # Score par défaut pour données simples
            
            # Cohérence temporelle (simulée)
            quality_factors.append(0.9)
            
            return statistics.mean(quality_factors)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate quality score: {e}")
            return 0.5
    
    def _calculate_confidence_interval(self, value: float, raw_data: Any) -> Optional[Tuple[float, float]]:
        """Calcule l'intervalle de confiance"""
        try:
            if isinstance(raw_data, list) and len(raw_data) > 1:
                std_dev = statistics.stdev(raw_data)
                margin = 1.96 * std_dev / math.sqrt(len(raw_data))  # 95% CI
                return (value - margin, value + margin)
            else:
                # Estimation simple pour données uniques
                margin = value * 0.05  # 5% de marge
                return (value - margin, value + margin)
                
        except Exception as e:
            logger.error(f"❌ Failed to calculate confidence interval: {e}")
            return None
    
    async def _store_measurement(self, measurement: KPIMeasurement):
        """Stocke une mesure KPI"""
        try:
            key = f"kpi:measurements:{measurement.kpi_id}"
            
            # Sérialiser la mesure
            data = {
                'measurement_id': measurement.measurement_id,
                'kpi_id': measurement.kpi_id,
                'value': measurement.value,
                'timestamp': measurement.timestamp.isoformat(),
                'period_start': measurement.period_start.isoformat(),
                'period_end': measurement.period_end.isoformat(),
                'raw_data': measurement.raw_data,
                'calculation_details': measurement.calculation_details,
                'quality_score': measurement.quality_score,
                'confidence_interval': measurement.confidence_interval,
                'metadata': measurement.metadata
            }
            
            # Stocker dans un sorted set avec timestamp comme score
            timestamp_score = measurement.timestamp.timestamp()
            self.redis_client.zadd(key, {json.dumps(data): timestamp_score})
            
            # Nettoyer les anciennes mesures
            cutoff_score = (datetime.now() - self.config.historical_data_retention).timestamp()
            self.redis_client.zremrangebyscore(key, 0, cutoff_score)
            
        except Exception as e:
            logger.error(f"❌ Failed to store measurement: {e}")
    
    async def _threshold_monitoring_loop(self):
        """Boucle de monitoring des seuils"""
        while self.is_running:
            try:
                for kpi in self.kpi_definitions.values():
                    if kpi.is_active and kpi.threshold and kpi.threshold.is_active:
                        await self._check_kpi_threshold(kpi)
                
                await asyncio.sleep(self.config.threshold_check_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Error in threshold monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _check_kpi_threshold(self, kpi: KPIDefinition):
        """Vérifie les seuils d'un KPI"""
        try:
            # Récupérer la dernière mesure
            measurements = self.measurement_cache.get(kpi.kpi_id)
            if not measurements:
                return
            
            latest_measurement = measurements[-1]
            current_value = latest_measurement.value
            threshold = kpi.threshold
            
            # Calculer les seuils dynamiques si nécessaire
            if threshold.threshold_type in [ThresholdType.DYNAMIC, ThresholdType.ADAPTIVE]:
                adjusted_thresholds = await self.threshold_manager.calculate_dynamic_thresholds(
                    kpi, list(measurements)
                )
                warning_value = adjusted_thresholds.get('warning', threshold.warning_value)
                critical_value = adjusted_thresholds.get('critical', threshold.critical_value)
            else:
                warning_value = threshold.warning_value
                critical_value = threshold.critical_value
            
            # Déterminer l'état
            alert_level = None
            threshold_value = None
            
            if threshold.is_lower_better:
                # Pour les métriques où plus bas = mieux
                if current_value >= critical_value:
                    alert_level = AlertLevel.CRITICAL
                    threshold_value = critical_value
                elif current_value >= warning_value:
                    alert_level = AlertLevel.WARNING
                    threshold_value = warning_value
            else:
                # Pour les métriques où plus haut = mieux
                if current_value <= critical_value:
                    alert_level = AlertLevel.CRITICAL
                    threshold_value = critical_value
                elif current_value <= warning_value:
                    alert_level = AlertLevel.WARNING
                    threshold_value = warning_value
            
            # Déclencher une alerte si nécessaire
            if alert_level:
                await self._trigger_kpi_alert(kpi, current_value, threshold_value, alert_level)
            else:
                # Résoudre les alertes existantes si la valeur est revenue normale
                await self._resolve_kpi_alerts(kpi.kpi_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to check KPI threshold for {kpi.name}: {e}")
    
    async def _trigger_kpi_alert(self, kpi: KPIDefinition, current_value: float,
                               threshold_value: float, alert_level: AlertLevel):
        """Déclenche une alerte KPI"""
        try:
            # Vérifier la période de cooldown
            cooldown_key = f"alert_cooldown:{kpi.kpi_id}:{alert_level.value}"
            if self.redis_client.exists(cooldown_key):
                return  # Alerte en cooldown
            
            # Calculer la déviation
            deviation = abs(current_value - threshold_value) / threshold_value * 100
            
            # Créer l'alerte
            alert = KPIAlert(
                kpi_id=kpi.kpi_id,
                alert_level=alert_level,
                message=f"KPI '{kpi.name}' {alert_level.value}: {current_value:.2f} {kpi.unit}",
                current_value=current_value,
                threshold_value=threshold_value,
                deviation_percentage=deviation
            )
            
            # Stocker l'alerte
            self.active_alerts[alert.alert_id] = alert
            await self._store_alert(alert)
            
            # Définir le cooldown
            cooldown_seconds = int(self.config.alert_cooldown_period.total_seconds())
            self.redis_client.setex(cooldown_key, cooldown_seconds, "1")
            
            # Publier l'alerte
            await self._publish_alert(alert, kpi)
            
            # Mettre à jour les métriques
            self.manager_metrics['alerts_triggered'] += 1
            
            logger.warning(f"🚨 KPI ALERT [{alert_level.value.upper()}]: {alert.message}")
            
        except Exception as e:
            logger.error(f"❌ Failed to trigger KPI alert: {e}")
    
    async def _resolve_kpi_alerts(self, kpi_id: str):
        """Résout les alertes d'un KPI"""
        try:
            resolved_alerts = []
            
            for alert_id, alert in list(self.active_alerts.items()):
                if alert.kpi_id == kpi_id and not alert.acknowledged:
                    alert.auto_resolved = True
                    alert.resolved_at = datetime.now()
                    await self._store_alert(alert)
                    resolved_alerts.append(alert_id)
            
            # Supprimer des alertes actives
            for alert_id in resolved_alerts:
                del self.active_alerts[alert_id]
            
            if resolved_alerts:
                logger.info(f"✅ Auto-resolved {len(resolved_alerts)} alerts for KPI {kpi_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to resolve KPI alerts: {e}")
    
    async def _store_alert(self, alert: KPIAlert):
        """Stocke une alerte KPI"""
        try:
            key = f"kpi:alerts:{alert.alert_id}"
            data = {
                'alert_id': alert.alert_id,
                'kpi_id': alert.kpi_id,
                'alert_level': alert.alert_level.value,
                'message': alert.message,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'deviation_percentage': alert.deviation_percentage,
                'triggered_at': alert.triggered_at.isoformat(),
                'acknowledged': alert.acknowledged,
                'acknowledged_by': alert.acknowledged_by,
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                'auto_resolved': alert.auto_resolved,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            
            self.redis_client.setex(key, 7 * 24 * 3600, json.dumps(data))  # 7 jours
            
        except Exception as e:
            logger.error(f"❌ Failed to store alert: {e}")
    
    async def _publish_alert(self, alert: KPIAlert, kpi: KPIDefinition):
        """Publie une alerte sur Redis"""
        try:
            alert_data = {
                'alert_id': alert.alert_id,
                'kpi_name': kpi.name,
                'kpi_category': kpi.category.value,
                'alert_level': alert.alert_level.value,
                'message': alert.message,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'deviation_percentage': alert.deviation_percentage,
                'triggered_at': alert.triggered_at.isoformat(),
                'is_business_critical': kpi.is_business_critical
            }
            
            self.redis_client.publish("kpi:alerts", json.dumps(alert_data))
            
        except Exception as e:
            logger.error(f"❌ Failed to publish alert: {e}")
    
    async def _trend_analysis_loop(self):
        """Boucle d'analyse des tendances"""
        while self.is_running:
            try:
                for kpi in self.kpi_definitions.values():
                    if kpi.is_active:
                        await self._analyze_kpi_trend(kpi)
                
                await asyncio.sleep(self.config.trend_analysis_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Error in trend analysis loop: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_kpi_trend(self, kpi: KPIDefinition):
        """Analyse la tendance d'un KPI"""
        try:
            measurements = self.measurement_cache.get(kpi.kpi_id)
            if not measurements or len(measurements) < self.config.min_data_points_for_trend:
                return
            
            # Analyser la tendance
            trend = await self.trend_analyzer.analyze_trend(list(measurements))
            
            if trend and trend.confidence >= self.config.confidence_threshold:
                # Stocker la tendance
                trend.kpi_id = kpi.kpi_id
                self.trend_cache[kpi.kpi_id] = trend
                await self._store_trend(trend)
                
                # Mettre à jour les métriques
                self.manager_metrics['trends_analyzed'] += 1
                
                logger.debug(f"📊 Analyzed trend for {kpi.name}: {trend.trend_direction}")
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze trend for {kpi.name}: {e}")
    
    async def _store_trend(self, trend: KPITrend):
        """Stocke une analyse de tendance"""
        try:
            key = f"kpi:trends:{trend.kpi_id}"
            data = {
                'trend_id': trend.trend_id,
                'kpi_id': trend.kpi_id,
                'trend_direction': trend.trend_direction,
                'trend_strength': trend.trend_strength,
                'trend_duration': trend.trend_duration.total_seconds(),
                'slope': trend.slope,
                'r_squared': trend.r_squared,
                'confidence': trend.confidence,
                'forecast_value': trend.forecast_value,
                'forecast_horizon': trend.forecast_horizon.total_seconds() if trend.forecast_horizon else None,
                'calculated_at': trend.calculated_at.isoformat()
            }
            
            self.redis_client.setex(key, 24 * 3600, json.dumps(data))  # 24 heures
            
        except Exception as e:
            logger.error(f"❌ Failed to store trend: {e}")
    
    async def _cleanup_loop(self):
        """Boucle de nettoyage"""
        while self.is_running:
            try:
                # Nettoyer les anciennes mesures
                await self._cleanup_old_measurements()
                
                # Nettoyer les alertes résolues
                await self._cleanup_resolved_alerts()
                
                # Nettoyer le cache
                await self._cleanup_cache()
                
                logger.info("✅ KPI cleanup completed")
                
                # Nettoyer une fois par jour
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                logger.error(f"❌ Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_measurements(self):
        """Nettoie les anciennes mesures"""
        try:
            cutoff_time = datetime.now() - self.config.historical_data_retention
            cutoff_score = cutoff_time.timestamp()
            
            for kpi_id in self.kpi_definitions.keys():
                key = f"kpi:measurements:{kpi_id}"
                removed = self.redis_client.zremrangebyscore(key, 0, cutoff_score)
                if removed:
                    logger.debug(f"Cleaned {removed} old measurements for KPI {kpi_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old measurements: {e}")
    
    async def _cleanup_resolved_alerts(self):
        """Nettoie les alertes résolues"""
        try:
            cutoff_time = datetime.now() - timedelta(days=7)
            
            keys = [key.decode() for key in self.redis_client.keys("kpi:alerts:*")]
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    alert_data = json.loads(data)
                    if (alert_data.get('auto_resolved') or alert_data.get('acknowledged')):
                        resolved_time = alert_data.get('resolved_at') or alert_data.get('acknowledged_at')
                        if resolved_time:
                            resolved_dt = datetime.fromisoformat(resolved_time)
                            if resolved_dt < cutoff_time:
                                self.redis_client.delete(key)
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup resolved alerts: {e}")
    
    async def _cleanup_cache(self):
        """Nettoie le cache en mémoire"""
        try:
            # Limiter la taille du cache de mesures
            for kpi_id, measurements in self.measurement_cache.items():
                if len(measurements) > 1000:
                    # Garder seulement les 1000 dernières
                    self.measurement_cache[kpi_id] = deque(
                        list(measurements)[-1000:], maxlen=1000
                    )
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup cache: {e}")
    
    async def get_kpi_status(self, kpi_id: str) -> Dict[str, Any]:
        """Récupère le statut complet d'un KPI"""
        try:
            if kpi_id not in self.kpi_definitions:
                raise ValueError(f"KPI {kpi_id} not found")
            
            kpi = self.kpi_definitions[kpi_id]
            measurements = self.measurement_cache.get(kpi_id, [])
            trend = self.trend_cache.get(kpi_id)
            
            # Déterminer le statut
            status = KPIStatus.UNKNOWN
            latest_value = None
            
            if measurements:
                latest_measurement = measurements[-1]
                latest_value = latest_measurement.value
                
                if kpi.threshold:
                    if kpi.threshold.is_lower_better:
                        if latest_value <= (kpi.threshold.excellent_value or kpi.threshold.warning_value * 0.8):
                            status = KPIStatus.EXCELLENT
                        elif latest_value <= kpi.threshold.warning_value:
                            status = KPIStatus.GOOD
                        elif latest_value <= kpi.threshold.critical_value:
                            status = KPIStatus.WARNING
                        else:
                            status = KPIStatus.CRITICAL
                    else:
                        if latest_value >= (kpi.threshold.excellent_value or kpi.threshold.warning_value * 1.2):
                            status = KPIStatus.EXCELLENT
                        elif latest_value >= kpi.threshold.warning_value:
                            status = KPIStatus.GOOD
                        elif latest_value >= kpi.threshold.critical_value:
                            status = KPIStatus.WARNING
                        else:
                            status = KPIStatus.CRITICAL
            
            # Assembler le statut complet
            return {
                'kpi_id': kpi_id,
                'name': kpi.name,
                'category': kpi.category.value,
                'current_value': latest_value,
                'unit': kpi.unit,
                'status': status.value,
                'target_value': kpi.target_value,
                'trend': {
                    'direction': trend.trend_direction if trend else 'unknown',
                    'strength': trend.trend_strength if trend else 0,
                    'confidence': trend.confidence if trend else 0
                } if trend else None,
                'recent_measurements': [
                    {
                        'value': m.value,
                        'timestamp': m.timestamp.isoformat(),
                        'quality_score': m.quality_score
                    } for m in list(measurements)[-10:]  # 10 dernières mesures
                ],
                'active_alerts': [
                    {
                        'alert_id': alert.alert_id,
                        'level': alert.alert_level.value,
                        'message': alert.message,
                        'triggered_at': alert.triggered_at.isoformat()
                    } for alert in self.active_alerts.values() 
                    if alert.kpi_id == kpi_id and not alert.auto_resolved
                ],
                'last_updated': measurements[-1].timestamp.isoformat() if measurements else None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get KPI status: {e}")
            return {}
    
    async def get_manager_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques du gestionnaire"""
        try:
            uptime = datetime.now() - self.manager_metrics['uptime_start']
            
            return {
                'kpis_monitored': len(self.kpi_definitions),
                'measurements_calculated': self.manager_metrics['measurements_calculated'],
                'alerts_triggered': self.manager_metrics['alerts_triggered'],
                'trends_analyzed': self.manager_metrics['trends_analyzed'],
                'avg_calculation_time_ms': self.manager_metrics['avg_calculation_time'] * 1000,
                'active_alerts': len(self.active_alerts),
                'cache_hit_rate': (self.manager_metrics['cache_hits'] / 
                                 (self.manager_metrics['cache_hits'] + self.manager_metrics['cache_misses'])
                                 if self.manager_metrics['cache_hits'] + self.manager_metrics['cache_misses'] > 0 else 0),
                'last_calculation': (self.manager_metrics['last_calculation'].isoformat() 
                                   if self.manager_metrics['last_calculation'] else None),
                'uptime_hours': uptime.total_seconds() / 3600,
                'is_running': self.is_running
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get manager metrics: {e}")
            return {}
    
    async def shutdown(self):
        """Arrête le gestionnaire KPI"""
        try:
            logger.info("🛑 Shutting down KPI Monitoring Manager...")
            
            self.is_running = False
            
            # Arrêter toutes les tâches
            tasks = [self.calculation_task, self.threshold_task, self.trend_task, self.cleanup_task]
            for task in tasks:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            logger.info("✅ KPI Monitoring Manager shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

class KPITrendAnalyzer:
    """Analyseur de tendances KPI"""
    
    async def analyze_trend(self, measurements: List[KPIMeasurement]) -> Optional[KPITrend]:
        """Analyse la tendance d'une série de mesures"""
        try:
            if len(measurements) < 3:
                return None
            
            # Extraire les valeurs et timestamps
            values = [m.value for m in measurements]
            timestamps = [m.timestamp.timestamp() for m in measurements]
            
            # Calcul de la régression linéaire simple
            n = len(values)
            sum_x = sum(range(n))
            sum_y = sum(values)
            sum_xy = sum(i * values[i] for i in range(n))
            sum_x2 = sum(i * i for i in range(n))
            
            # Calcul de la pente
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Calcul du coefficient de détermination (R²)
            mean_y = sum_y / n
            ss_tot = sum((y - mean_y) ** 2 for y in values)
            ss_res = sum((values[i] - (slope * i + (sum_y - slope * sum_x) / n)) ** 2 for i in range(n))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Déterminer la direction de la tendance
            if abs(slope) < 0.01:
                direction = "stable"
                strength = 0
            elif slope > 0:
                direction = "improving"
                strength = min(1.0, abs(slope) / (max(values) - min(values)) * 10)
            else:
                direction = "declining"
                strength = min(1.0, abs(slope) / (max(values) - min(values)) * 10)
            
            # Calcul de la confiance
            confidence = min(1.0, r_squared * (1 + len(measurements) / 100))
            
            # Prédiction simple
            forecast_value = values[-1] + slope * 5  # 5 périodes dans le futur
            
            return KPITrend(
                trend_direction=direction,
                trend_strength=strength,
                trend_duration=measurements[-1].timestamp - measurements[0].timestamp,
                slope=slope,
                r_squared=r_squared,
                confidence=confidence,
                forecast_value=forecast_value,
                forecast_horizon=timedelta(hours=5)
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze trend: {e}")
            return None

class DynamicThresholdManager:
    """Gestionnaire de seuils dynamiques"""
    
    async def calculate_dynamic_thresholds(self, kpi: KPIDefinition, 
                                         measurements: List[KPIMeasurement]) -> Dict[str, float]:
        """Calcule les seuils dynamiques basés sur l'historique"""
        try:
            if len(measurements) < 10:
                # Pas assez de données, utiliser les seuils statiques
                return {
                    'warning': kpi.threshold.warning_value,
                    'critical': kpi.threshold.critical_value
                }
            
            values = [m.value for m in measurements[-kpi.threshold.historical_data_points:]]
            
            # Calculs statistiques
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
            
            # Seuils adaptatifs basés sur la distribution
            if kpi.threshold.is_lower_better:
                warning_threshold = mean_val + std_val * 1.5
                critical_threshold = mean_val + std_val * 2.5
            else:
                warning_threshold = mean_val - std_val * 1.5
                critical_threshold = mean_val - std_val * 2.5
            
            # Appliquer le facteur adaptatif
            factor = kpi.threshold.adaptive_factor
            warning_threshold = (1 - factor) * kpi.threshold.warning_value + factor * warning_threshold
            critical_threshold = (1 - factor) * kpi.threshold.critical_value + factor * critical_threshold
            
            return {
                'warning': warning_threshold,
                'critical': critical_threshold
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate dynamic thresholds: {e}")
            return {
                'warning': kpi.threshold.warning_value,
                'critical': kpi.threshold.critical_value
            }

# Factory function pour créer le gestionnaire
async def create_kpi_monitoring_manager(
    config: Optional[KPIMonitoringConfig] = None,
    redis_client: Optional[redis.Redis] = None
) -> RedisKPIMonitoringManager:
    """Crée et initialise un gestionnaire de monitoring KPI"""
    
    if config is None:
        config = KPIMonitoringConfig()
    
    manager = RedisKPIMonitoringManager(config, redis_client)
    
    if await manager.initialize():
        return manager
    else:
        raise RuntimeError("Failed to initialize KPI Monitoring Manager")

__all__ = [
    'RedisKPIMonitoringManager',
    'KPIMonitoringConfig',
    'KPIDefinition',
    'KPIMeasurement',
    'KPIAlert',
    'KPITrend',
    'KPIReport',
    'KPIThreshold',
    'KPICategory',
    'KPIType',
    'KPIStatus',
    'ThresholdType',
    'AlertLevel',
    'KPITrendAnalyzer',
    'DynamicThresholdManager',
    'create_kpi_monitoring_manager'
]
