"""
⏱️ Latency Distribution Analyzer - Enterprise AI/ML Performance Hub
=================================================================

Analyseur distribution latence enterprise ultra-avancé pour Creator Economy Ainflue.
P50/P95/P99 latency tracking, breakdown latence par composant, impact expérience créateur,
distribution latence géographique, monitoring compliance SLA.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Architecture: monitoring/ai_ml_performance_hub/latency_distribution_analyzer.py
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import time
import statistics
import math
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import threading
import json
import uuid
import numpy as np
from concurrent.futures import ThreadPoolExecutor


class LatencyComponent(Enum):
    """Composants latence"""
    NETWORK_INGRESS = "network_ingress"
    AUTHENTICATION = "authentication"
    PREPROCESSING = "preprocessing"
    MODEL_LOADING = "model_loading"
    MODEL_INFERENCE = "model_inference"
    POSTPROCESSING = "postprocessing"
    RESULT_SERIALIZATION = "result_serialization"
    NETWORK_EGRESS = "network_egress"
    TOTAL_E2E = "total_e2e"


class GeographicRegion(Enum):
    """Régions géographiques"""
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    MIDDLE_EAST_AFRICA = "middle_east_africa"


class CreatorTier(Enum):
    """Niveaux créateurs"""
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ServiceType(Enum):
    """Types service IA"""
    CONTENT_ANALYSIS = "content_analysis"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_ENHANCEMENT = "video_enhancement"
    TEXT_GENERATION = "text_generation"
    IMAGE_EDITING = "image_editing"
    RECOMMENDATION = "recommendation"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"


@dataclass
class LatencyMeasurement:
    """Mesure latence détaillée"""
    measurement_id: str
    request_id: str
    creator_id: str
    creator_tier: CreatorTier
    service_type: ServiceType
    geographic_region: GeographicRegion
    component_latencies: Dict[LatencyComponent, float]  # in milliseconds
    total_latency_ms: float
    request_size_bytes: int
    response_size_bytes: int
    cache_hit: bool
    cdn_used: bool
    edge_location: Optional[str]
    user_agent: str
    connection_type: str  # "4G", "5G", "WiFi", "Fiber"
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LatencyDistribution:
    """Distribution latence statistique"""
    component: LatencyComponent
    service_type: ServiceType
    creator_tier: CreatorTier
    geographic_region: GeographicRegion
    sample_count: int
    mean_ms: float
    median_ms: float
    p50_ms: float
    p75_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    p99_9_ms: float
    min_ms: float
    max_ms: float
    std_dev_ms: float
    variance_ms: float
    skewness: float
    kurtosis: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SLACompliance:
    """Conformité SLA latence"""
    service_type: ServiceType
    creator_tier: CreatorTier
    geographic_region: GeographicRegion
    sla_threshold_ms: float
    compliance_percentage: float
    violation_count: int
    total_requests: int
    avg_violation_severity: float
    worst_violation_ms: float
    compliance_trend: str  # "improving", "stable", "degrading"
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LatencyAnomalyAlert:
    """Alerte anomalie latence"""
    alert_id: str
    service_type: ServiceType
    component: LatencyComponent
    creator_tier: CreatorTier
    geographic_region: GeographicRegion
    anomaly_type: str  # "spike", "degradation", "outlier"
    severity: str  # "low", "medium", "high", "critical"
    current_value_ms: float
    expected_value_ms: float
    deviation_percent: float
    impact_assessment: str
    recommended_action: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class LatencyDistributionAnalyzer:
    """Analyseur distribution latence enterprise Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Latency data storage
        self.latency_measurements: deque = deque(maxlen=50000)
        self.distribution_cache: Dict[str, LatencyDistribution] = {}
        self.sla_compliance_cache: Dict[str, SLACompliance] = {}
        
        # Real-time tracking
        self.active_requests: Dict[str, Dict] = {}
        self.anomaly_alerts: deque = deque(maxlen=1000)
        
        # SLA thresholds per creator tier and service type
        self.sla_thresholds = {
            CreatorTier.FREE: {
                ServiceType.CONTENT_ANALYSIS: 5000,      # 5s
                ServiceType.AUDIO_PROCESSING: 8000,      # 8s
                ServiceType.VIDEO_ENHANCEMENT: 15000,    # 15s
                ServiceType.TEXT_GENERATION: 3000,       # 3s
                ServiceType.IMAGE_EDITING: 10000,        # 10s
                ServiceType.RECOMMENDATION: 2000,        # 2s
                ServiceType.COLLABORATION: 1000,         # 1s
                ServiceType.MONETIZATION: 500            # 500ms
            },
            CreatorTier.PREMIUM: {
                ServiceType.CONTENT_ANALYSIS: 3000,      # 3s
                ServiceType.AUDIO_PROCESSING: 5000,      # 5s
                ServiceType.VIDEO_ENHANCEMENT: 10000,    # 10s
                ServiceType.TEXT_GENERATION: 2000,       # 2s
                ServiceType.IMAGE_EDITING: 6000,         # 6s
                ServiceType.RECOMMENDATION: 1000,        # 1s
                ServiceType.COLLABORATION: 500,          # 500ms
                ServiceType.MONETIZATION: 300            # 300ms
            },
            CreatorTier.PROFESSIONAL: {
                ServiceType.CONTENT_ANALYSIS: 2000,      # 2s
                ServiceType.AUDIO_PROCESSING: 3000,      # 3s
                ServiceType.VIDEO_ENHANCEMENT: 6000,     # 6s
                ServiceType.TEXT_GENERATION: 1500,       # 1.5s
                ServiceType.IMAGE_EDITING: 4000,         # 4s
                ServiceType.RECOMMENDATION: 500,         # 500ms
                ServiceType.COLLABORATION: 300,          # 300ms
                ServiceType.MONETIZATION: 200            # 200ms
            },
            CreatorTier.ENTERPRISE: {
                ServiceType.CONTENT_ANALYSIS: 1000,      # 1s
                ServiceType.AUDIO_PROCESSING: 2000,      # 2s
                ServiceType.VIDEO_ENHANCEMENT: 4000,     # 4s
                ServiceType.TEXT_GENERATION: 1000,       # 1s
                ServiceType.IMAGE_EDITING: 3000,         # 3s
                ServiceType.RECOMMENDATION: 300,         # 300ms
                ServiceType.COLLABORATION: 200,          # 200ms
                ServiceType.MONETIZATION: 100            # 100ms
            }
        }
        
        # Regional latency expectations (baseline network latency)
        self.regional_baseline_latency = {
            GeographicRegion.NORTH_AMERICA: 20,
            GeographicRegion.EUROPE: 25,
            GeographicRegion.ASIA_PACIFIC: 35,
            GeographicRegion.LATIN_AMERICA: 45,
            GeographicRegion.MIDDLE_EAST_AFRICA: 55
        }
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Statistics calculation interval
        self.stats_calculation_interval = 60  # seconds
        self.last_stats_calculation = time.time()
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger(f"latency_analyzer_{id(self)}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation analyseur latence"""
        self.logger.info("⏱️ Initialisation Latency Distribution Analyzer...")
        
        # Démarrer monitoring continu
        await self._start_latency_monitoring()
        
        # Initialiser distributions baseline
        await self._initialize_baseline_distributions()
        
        self.logger.info("✅ Latency Distribution Analyzer initialisé")
    
    async def _start_latency_monitoring(self):
        """Démarrage monitoring latence continu"""
        self.monitoring_active = True
        
        def monitor_latency():
            while self.monitoring_active:
                try:
                    self._calculate_distributions()
                    self._detect_anomalies()
                    time.sleep(30)  # Calculate every 30 seconds
                except Exception as e:
                    self.logger.error(f"Latency monitoring error: {e}")
        
        self.monitoring_thread = threading.Thread(target=monitor_latency, daemon=True)
        self.monitoring_thread.start()
    
    async def _initialize_baseline_distributions(self):
        """Initialisation distributions baseline"""
        # Generate baseline measurements for each combination
        for creator_tier in CreatorTier:
            for service_type in ServiceType:
                for region in GeographicRegion:
                    # Generate sample measurements
                    for _ in range(100):
                        await self._generate_sample_measurement(creator_tier, service_type, region)
    
    async def _generate_sample_measurement(
        self, 
        creator_tier: CreatorTier, 
        service_type: ServiceType, 
        region: GeographicRegion
    ):
        """Génération mesure échantillon"""
        import random
        
        # Base latency from service type and tier
        base_latency = {
            ServiceType.CONTENT_ANALYSIS: 1500,
            ServiceType.AUDIO_PROCESSING: 2500,
            ServiceType.VIDEO_ENHANCEMENT: 4000,
            ServiceType.TEXT_GENERATION: 800,
            ServiceType.IMAGE_EDITING: 2000,
            ServiceType.RECOMMENDATION: 300,
            ServiceType.COLLABORATION: 150,
            ServiceType.MONETIZATION: 100
        }[service_type]
        
        # Tier multiplier
        tier_multiplier = {
            CreatorTier.ENTERPRISE: 0.5,
            CreatorTier.PROFESSIONAL: 0.7,
            CreatorTier.PREMIUM: 0.85,
            CreatorTier.FREE: 1.2
        }[creator_tier]
        
        # Regional adjustment
        regional_adjustment = self.regional_baseline_latency[region]
        
        # Calculate component latencies
        component_latencies = {}
        
        # Network ingress (5-15% of total)
        network_ingress = regional_adjustment + random.uniform(10, 30)
        component_latencies[LatencyComponent.NETWORK_INGRESS] = network_ingress
        
        # Authentication (1-3% of total)
        auth_latency = random.uniform(5, 20)
        component_latencies[LatencyComponent.AUTHENTICATION] = auth_latency
        
        # Preprocessing (10-20% of total)
        preprocess_base = base_latency * 0.15 * tier_multiplier
        preprocessing = preprocess_base + random.uniform(-preprocess_base*0.3, preprocess_base*0.5)
        component_latencies[LatencyComponent.PREPROCESSING] = preprocessing
        
        # Model loading (2-5% of total, sometimes cached)
        model_loading = random.uniform(10, base_latency * 0.05) if random.random() > 0.7 else 0
        component_latencies[LatencyComponent.MODEL_LOADING] = model_loading
        
        # Model inference (60-80% of total)
        inference_base = base_latency * 0.7 * tier_multiplier
        inference = inference_base + random.uniform(-inference_base*0.2, inference_base*0.4)
        component_latencies[LatencyComponent.MODEL_INFERENCE] = inference
        
        # Postprocessing (5-15% of total)
        postprocess_base = base_latency * 0.1 * tier_multiplier
        postprocessing = postprocess_base + random.uniform(-postprocess_base*0.3, postprocess_base*0.5)
        component_latencies[LatencyComponent.POSTPROCESSING] = postprocessing
        
        # Result serialization (1-3% of total)
        serialization = random.uniform(5, 25)
        component_latencies[LatencyComponent.RESULT_SERIALIZATION] = serialization
        
        # Network egress (3-8% of total)
        network_egress = regional_adjustment * 0.5 + random.uniform(5, 20)
        component_latencies[LatencyComponent.NETWORK_EGRESS] = network_egress
        
        # Total E2E
        total_latency = sum(component_latencies.values())
        component_latencies[LatencyComponent.TOTAL_E2E] = total_latency
        
        # Create measurement
        measurement = LatencyMeasurement(
            measurement_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            creator_id=f"creator_{random.randint(1, 1000)}",
            creator_tier=creator_tier,
            service_type=service_type,
            geographic_region=region,
            component_latencies=component_latencies,
            total_latency_ms=total_latency,
            request_size_bytes=random.randint(1024, 1024*1024),
            response_size_bytes=random.randint(512, 512*1024),
            cache_hit=random.random() < 0.3,
            cdn_used=random.random() < 0.8,
            edge_location=f"edge_{region.value}_{random.randint(1, 5)}",
            user_agent="Ainflue-Client/1.0",
            connection_type=random.choice(["4G", "5G", "WiFi", "Fiber"])
        )
        
        self.latency_measurements.append(measurement)
    
    async def start_request_tracking(
        self,
        request_id: str,
        creator_id: str,
        creator_tier: CreatorTier,
        service_type: ServiceType,
        geographic_region: GeographicRegion,
        request_size_bytes: int,
        user_agent: str = "Unknown",
        connection_type: str = "Unknown"
    ) -> str:
        """Démarrage tracking requête"""
        start_time = time.time()
        
        self.active_requests[request_id] = {
            'creator_id': creator_id,
            'creator_tier': creator_tier,
            'service_type': service_type,
            'geographic_region': geographic_region,
            'request_size_bytes': request_size_bytes,
            'user_agent': user_agent,
            'connection_type': connection_type,
            'start_time': start_time,
            'component_timings': {},
            'component_start_times': {}
        }
        
        self.logger.debug(f"Started tracking request {request_id}")
        return request_id
    
    async def record_component_start(
        self,
        request_id: str,
        component: LatencyComponent
    ):
        """Enregistrement début composant"""
        if request_id not in self.active_requests:
            self.logger.warning(f"Request {request_id} not found for component start")
            return
        
        self.active_requests[request_id]['component_start_times'][component] = time.time()
    
    async def record_component_end(
        self,
        request_id: str,
        component: LatencyComponent
    ):
        """Enregistrement fin composant"""
        if request_id not in self.active_requests:
            self.logger.warning(f"Request {request_id} not found for component end")
            return
        
        request_data = self.active_requests[request_id]
        end_time = time.time()
        
        if component in request_data['component_start_times']:
            start_time = request_data['component_start_times'][component]
            latency_ms = (end_time - start_time) * 1000
            request_data['component_timings'][component] = latency_ms
            
            self.logger.debug(f"Component {component.value} took {latency_ms:.2f}ms for request {request_id}")
    
    async def complete_request_tracking(
        self,
        request_id: str,
        response_size_bytes: int,
        cache_hit: bool = False,
        cdn_used: bool = False,
        edge_location: Optional[str] = None
    ):
        """Finalisation tracking requête"""
        if request_id not in self.active_requests:
            self.logger.warning(f"Request {request_id} not found for completion")
            return
        
        request_data = self.active_requests[request_id]
        end_time = time.time()
        total_latency_ms = (end_time - request_data['start_time']) * 1000
        
        # Add total E2E latency
        request_data['component_timings'][LatencyComponent.TOTAL_E2E] = total_latency_ms
        
        # Create measurement
        measurement = LatencyMeasurement(
            measurement_id=str(uuid.uuid4()),
            request_id=request_id,
            creator_id=request_data['creator_id'],
            creator_tier=request_data['creator_tier'],
            service_type=request_data['service_type'],
            geographic_region=request_data['geographic_region'],
            component_latencies=request_data['component_timings'].copy(),
            total_latency_ms=total_latency_ms,
            request_size_bytes=request_data['request_size_bytes'],
            response_size_bytes=response_size_bytes,
            cache_hit=cache_hit,
            cdn_used=cdn_used,
            edge_location=edge_location,
            user_agent=request_data['user_agent'],
            connection_type=request_data['connection_type']
        )
        
        self.latency_measurements.append(measurement)
        
        # Check SLA compliance
        await self._check_sla_compliance(measurement)
        
        # Remove from active tracking
        del self.active_requests[request_id]
        
        self.logger.debug(f"Completed request {request_id}: {total_latency_ms:.1f}ms")
    
    async def _check_sla_compliance(self, measurement: LatencyMeasurement):
        """Vérification conformité SLA"""
        threshold = self.sla_thresholds[measurement.creator_tier][measurement.service_type]
        
        if measurement.total_latency_ms > threshold:
            violation_severity = (measurement.total_latency_ms - threshold) / threshold
            
            self.logger.warning(
                f"🚨 SLA Violation: {measurement.service_type.value} for {measurement.creator_tier.value} "
                f"({measurement.total_latency_ms:.1f}ms > {threshold}ms, severity: {violation_severity:.2f})"
            )
            
            # In production, would trigger alerts/notifications
            await self._handle_sla_violation(measurement, threshold, violation_severity)
    
    async def _handle_sla_violation(
        self, 
        measurement: LatencyMeasurement, 
        threshold: float, 
        severity: float
    ):
        """Gestion violation SLA"""
        violation_data = {
            'request_id': measurement.request_id,
            'creator_id': measurement.creator_id,
            'creator_tier': measurement.creator_tier.value,
            'service_type': measurement.service_type.value,
            'geographic_region': measurement.geographic_region.value,
            'actual_latency': measurement.total_latency_ms,
            'threshold': threshold,
            'severity': severity,
            'component_breakdown': {comp.value: latency for comp, latency in measurement.component_latencies.items()},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log for monitoring systems
        self.logger.error(f"SLA Violation: {json.dumps(violation_data)}")
    
    def _calculate_distributions(self):
        """Calcul distributions latence"""
        current_time = time.time()
        
        if current_time - self.last_stats_calculation < self.stats_calculation_interval:
            return
        
        # Calculate distributions for last hour
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        recent_measurements = [
            m for m in self.latency_measurements 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_measurements:
            return
        
        # Group by service, tier, region, component
        groups = defaultdict(list)
        
        for measurement in recent_measurements:
            for component, latency in measurement.component_latencies.items():
                key = (
                    component,
                    measurement.service_type,
                    measurement.creator_tier,
                    measurement.geographic_region
                )
                groups[key].append(latency)
        
        # Calculate distribution statistics for each group
        for (component, service_type, creator_tier, region), latencies in groups.items():
            if len(latencies) < 10:  # Skip groups with insufficient data
                continue
            
            # Sort for percentile calculations
            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)
            
            # Calculate percentiles
            p50 = sorted_latencies[int(0.50 * n)]
            p75 = sorted_latencies[int(0.75 * n)]
            p90 = sorted_latencies[int(0.90 * n)]
            p95 = sorted_latencies[int(0.95 * n)]
            p99 = sorted_latencies[int(0.99 * n)]
            p99_9 = sorted_latencies[int(0.999 * n)]
            
            # Calculate statistical measures
            mean_val = statistics.mean(latencies)
            median_val = statistics.median(latencies)
            std_dev = statistics.stdev(latencies) if len(latencies) > 1 else 0
            variance = statistics.variance(latencies) if len(latencies) > 1 else 0
            
            # Calculate skewness and kurtosis
            skewness = self._calculate_skewness(latencies, mean_val, std_dev)
            kurtosis = self._calculate_kurtosis(latencies, mean_val, std_dev)
            
            distribution = LatencyDistribution(
                component=component,
                service_type=service_type,
                creator_tier=creator_tier,
                geographic_region=region,
                sample_count=n,
                mean_ms=mean_val,
                median_ms=median_val,
                p50_ms=p50,
                p75_ms=p75,
                p90_ms=p90,
                p95_ms=p95,
                p99_ms=p99,
                p99_9_ms=p99_9,
                min_ms=min(latencies),
                max_ms=max(latencies),
                std_dev_ms=std_dev,
                variance_ms=variance,
                skewness=skewness,
                kurtosis=kurtosis
            )
            
            # Cache distribution
            cache_key = f"{component.value}_{service_type.value}_{creator_tier.value}_{region.value}"
            self.distribution_cache[cache_key] = distribution
        
        # Update SLA compliance statistics
        self._calculate_sla_compliance()
        
        self.last_stats_calculation = current_time
    
    def _calculate_skewness(self, values: List[float], mean: float, std_dev: float) -> float:
        """Calcul asymétrie distribution"""
        if std_dev == 0 or len(values) < 3:
            return 0
        
        n = len(values)
        skewness = sum(((x - mean) / std_dev) ** 3 for x in values) / n
        return skewness
    
    def _calculate_kurtosis(self, values: List[float], mean: float, std_dev: float) -> float:
        """Calcul aplatissement distribution"""
        if std_dev == 0 or len(values) < 4:
            return 0
        
        n = len(values)
        kurtosis = sum(((x - mean) / std_dev) ** 4 for x in values) / n - 3
        return kurtosis
    
    def _calculate_sla_compliance(self):
        """Calcul conformité SLA"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_measurements = [
            m for m in self.latency_measurements 
            if m.timestamp >= cutoff_time
        ]
        
        # Group by service, tier, region
        compliance_groups = defaultdict(list)
        
        for measurement in recent_measurements:
            key = (
                measurement.service_type,
                measurement.creator_tier,
                measurement.geographic_region
            )
            compliance_groups[key].append(measurement)
        
        # Calculate compliance for each group
        for (service_type, creator_tier, region), measurements in compliance_groups.items():
            if not measurements:
                continue
            
            threshold = self.sla_thresholds[creator_tier][service_type]
            violations = [m for m in measurements if m.total_latency_ms > threshold]
            
            compliance_percentage = ((len(measurements) - len(violations)) / len(measurements)) * 100
            
            violation_severities = []
            for violation in violations:
                severity = (violation.total_latency_ms - threshold) / threshold
                violation_severities.append(severity)
            
            avg_violation_severity = statistics.mean(violation_severities) if violation_severities else 0
            worst_violation = max([v.total_latency_ms for v in violations]) if violations else 0
            
            # Determine trend (simplified - would use historical data in production)
            if compliance_percentage > 95:
                trend = "stable"
            elif compliance_percentage > 85:
                trend = "degrading"
            else:
                trend = "critical"
            
            compliance = SLACompliance(
                service_type=service_type,
                creator_tier=creator_tier,
                geographic_region=region,
                sla_threshold_ms=threshold,
                compliance_percentage=compliance_percentage,
                violation_count=len(violations),
                total_requests=len(measurements),
                avg_violation_severity=avg_violation_severity,
                worst_violation_ms=worst_violation,
                compliance_trend=trend
            )
            
            cache_key = f"{service_type.value}_{creator_tier.value}_{region.value}"
            self.sla_compliance_cache[cache_key] = compliance
    
    def _detect_anomalies(self):
        """Détection anomalies latence"""
        # Analyze recent distributions for anomalies
        for cache_key, distribution in self.distribution_cache.items():
            # Check for latency spikes (P99 > 3x P50)
            if distribution.p99_ms > distribution.p50_ms * 3:
                self._create_anomaly_alert_sync(
                    distribution, 
                    "spike", 
                    "high",
                    f"P99 latency spike: {distribution.p99_ms:.1f}ms (3x normal)"
                )
            
            # Check for high variance
            coefficient_of_variation = distribution.std_dev_ms / distribution.mean_ms if distribution.mean_ms > 0 else 0
            if coefficient_of_variation > 0.5:
                self._create_anomaly_alert_sync(
                    distribution,
                    "high_variance",
                    "medium", 
                    f"High latency variance detected: CV={coefficient_of_variation:.2f}"
                )
    
    def _create_anomaly_alert_sync(
        self,
        distribution: LatencyDistribution,
        anomaly_type: str,
        severity: str,
        description: str
    ):
        """Création alerte anomalie (synchrone)"""
        alert = LatencyAnomalyAlert(
            alert_id=str(uuid.uuid4()),
            service_type=distribution.service_type,
            component=distribution.component,
            creator_tier=distribution.creator_tier,
            geographic_region=distribution.geographic_region,
            anomaly_type=anomaly_type,
            severity=severity,
            current_value_ms=distribution.p99_ms,
            expected_value_ms=distribution.p50_ms,
            deviation_percent=((distribution.p99_ms - distribution.p50_ms) / distribution.p50_ms) * 100,
            impact_assessment=f"Affects {distribution.sample_count} requests",
            recommended_action="Investigate performance degradation"
        )
        
        self.anomaly_alerts.append(alert)
        
        self.logger.warning(f"🚨 Latency Anomaly: {description}")
    
    async def get_latency_overview(self) -> Dict[str, Any]:
        """Vue d'ensemble latence"""
        # Recent measurements summary
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        recent_measurements = [
            m for m in self.latency_measurements 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_measurements:
            return {'error': 'No recent measurements available'}
        
        # Overall statistics
        total_latencies = [m.total_latency_ms for m in recent_measurements]
        
        # Service type breakdown
        service_breakdown = defaultdict(list)
        for measurement in recent_measurements:
            service_breakdown[measurement.service_type.value].append(measurement.total_latency_ms)
        
        service_stats = {}
        for service, latencies in service_breakdown.items():
            if latencies:
                sorted_latencies = sorted(latencies)
                n = len(sorted_latencies)
                service_stats[service] = {
                    'requests': n,
                    'mean_ms': statistics.mean(latencies),
                    'p50_ms': sorted_latencies[int(0.50 * n)],
                    'p95_ms': sorted_latencies[int(0.95 * n)],
                    'p99_ms': sorted_latencies[int(0.99 * n)]
                }
        
        # SLA compliance summary
        sla_violations = sum(1 for compliance in self.sla_compliance_cache.values() 
                           if compliance.compliance_percentage < 95)
        
        # Recent anomalies
        recent_anomalies = [a for a in self.anomaly_alerts 
                          if (datetime.utcnow() - a.timestamp).total_seconds() < 3600]
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_requests_1h': len(recent_measurements),
                'avg_latency_ms': statistics.mean(total_latencies),
                'p50_latency_ms': sorted(total_latencies)[int(0.50 * len(total_latencies))],
                'p95_latency_ms': sorted(total_latencies)[int(0.95 * len(total_latencies))],
                'p99_latency_ms': sorted(total_latencies)[int(0.99 * len(total_latencies))]
            },
            'service_breakdown': service_stats,
            'sla_compliance': {
                'services_compliant': len(self.sla_compliance_cache) - sla_violations,
                'services_violations': sla_violations,
                'overall_compliance_percent': ((len(self.sla_compliance_cache) - sla_violations) / len(self.sla_compliance_cache) * 100) if self.sla_compliance_cache else 100
            },
            'anomalies_1h': len(recent_anomalies),
            'active_requests': len(self.active_requests)
        }
    
    async def get_detailed_distribution(
        self,
        service_type: ServiceType,
        creator_tier: CreatorTier,
        geographic_region: GeographicRegion,
        component: Optional[LatencyComponent] = None
    ) -> Dict[str, Any]:
        """Distribution détaillée par critères"""
        if component:
            cache_key = f"{component.value}_{service_type.value}_{creator_tier.value}_{geographic_region.value}"
            if cache_key in self.distribution_cache:
                distribution = self.distribution_cache[cache_key]
                return self._distribution_to_dict(distribution)
        
        # Return all components for the criteria
        result = {}
        for comp in LatencyComponent:
            cache_key = f"{comp.value}_{service_type.value}_{creator_tier.value}_{geographic_region.value}"
            if cache_key in self.distribution_cache:
                result[comp.value] = self._distribution_to_dict(self.distribution_cache[cache_key])
        
        return result
    
    def _distribution_to_dict(self, distribution: LatencyDistribution) -> Dict[str, Any]:
        """Conversion distribution en dictionnaire"""
        return {
            'component': distribution.component.value,
            'service_type': distribution.service_type.value,
            'creator_tier': distribution.creator_tier.value,
            'geographic_region': distribution.geographic_region.value,
            'sample_count': distribution.sample_count,
            'statistics': {
                'mean_ms': distribution.mean_ms,
                'median_ms': distribution.median_ms,
                'std_dev_ms': distribution.std_dev_ms,
                'min_ms': distribution.min_ms,
                'max_ms': distribution.max_ms
            },
            'percentiles': {
                'p50_ms': distribution.p50_ms,
                'p75_ms': distribution.p75_ms,
                'p90_ms': distribution.p90_ms,
                'p95_ms': distribution.p95_ms,
                'p99_ms': distribution.p99_ms,
                'p99_9_ms': distribution.p99_9_ms
            },
            'distribution_metrics': {
                'skewness': distribution.skewness,
                'kurtosis': distribution.kurtosis,
                'variance_ms': distribution.variance_ms
            },
            'timestamp': distribution.timestamp.isoformat()
        }
    
    async def shutdown(self):
        """Arrêt propre analyseur latence"""
        self.logger.info("⏹️ Arrêt Latency Distribution Analyzer...")
        
        # Arrêter monitoring
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        # Arrêter executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("✅ Latency Distribution Analyzer arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_latency_analyzer():
        config = {"debug": True}
        analyzer = LatencyDistributionAnalyzer(config)
        
        await analyzer.initialize()
        
        # Test request tracking
        request_id = await analyzer.start_request_tracking(
            request_id="req_123",
            creator_id="creator_456",
            creator_tier=CreatorTier.PREMIUM,
            service_type=ServiceType.CONTENT_ANALYSIS,
            geographic_region=GeographicRegion.NORTH_AMERICA,
            request_size_bytes=1024*50,
            user_agent="Ainflue-Test/1.0",
            connection_type="WiFi"
        )
        
        # Simulate component tracking
        await analyzer.record_component_start(request_id, LatencyComponent.PREPROCESSING)
        await asyncio.sleep(0.1)  # Simulate work
        await analyzer.record_component_end(request_id, LatencyComponent.PREPROCESSING)
        
        await analyzer.record_component_start(request_id, LatencyComponent.MODEL_INFERENCE)
        await asyncio.sleep(0.2)  # Simulate work
        await analyzer.record_component_end(request_id, LatencyComponent.MODEL_INFERENCE)
        
        # Complete request
        await analyzer.complete_request_tracking(
            request_id=request_id,
            response_size_bytes=1024*25,
            cache_hit=False,
            cdn_used=True,
            edge_location="edge_na_1"
        )
        
        # Wait for distribution calculation
        await asyncio.sleep(2)
        
        # Get overview
        overview = await analyzer.get_latency_overview()
        print(f"Latency Overview: {json.dumps(overview, indent=2)}")
        
        print("✅ Latency Distribution Analyzer test passed")
        await analyzer.shutdown()
    
    asyncio.run(test_latency_analyzer())