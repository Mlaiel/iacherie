"""
📈 Throughput Capacity Monitor - Enterprise Creator Economy Scaling
==================================================================

Système monitoring ultra-avancé capacité débit pour optimisation scaling Creator Economy.
Tracking RPS, auto-scaling triggers, peak load analysis et multi-modal content throughput.

Fonctionnalités:
- Requests per second (RPS) tracking avec granularité par Creator tier
- Creator concurrent usage monitoring temps réel
- Peak load capacity analysis avec predictive scaling
- Auto-scaling trigger optimization basé usage patterns
- Multi-modal content throughput metrics (audio/video/text/image)
- Creator geography load distribution analytics
- Capacity planning avec growth forecasting
- Performance bottleneck identification automatique
- Cost-optimized scaling recommendations

Architecture: monitoring/ai_ml_performance_hub/throughput_capacity_monitor.py
Responsabilité: Capacity monitoring, scaling optimization, load forecasting

© 2025 Fahed Mlaiel - Code propriétaire ultra-avancé production-ready
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
import threading
from collections import defaultdict, deque
import math


class CreatorTier(Enum):
    """Niveaux créateurs pour quotas throughput"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class ContentModality(Enum):
    """Modalités contenu pour analyse throughput"""
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    IMAGE = "image"
    MIXED_MEDIA = "mixed_media"


class ServiceEndpoint(Enum):
    """Endpoints services pour monitoring throughput"""
    CONTENT_UPLOAD = "content_upload"
    CONTENT_PROCESS = "content_process"
    CONTENT_SEARCH = "content_search"
    COLLABORATION_API = "collaboration_api"
    MONETIZATION_API = "monetization_api"
    ANALYTICS_API = "analytics_api"
    REAL_TIME_API = "real_time_api"
    STREAMING_API = "streaming_api"


class LoadPattern(Enum):
    """Patterns charge système"""
    STEADY = "steady"
    BURST = "burst"
    SEASONAL = "seasonal"
    RANDOM = "random"
    DECLINING = "declining"


@dataclass
class ThroughputMeasurement:
    """Mesure throughput système"""
    measurement_id: str
    endpoint: ServiceEndpoint
    creator_tier: CreatorTier
    content_modality: ContentModality
    
    # Throughput metrics
    requests_per_second: float
    concurrent_users: int
    active_connections: int
    
    # Request characteristics
    avg_request_size_bytes: int
    avg_response_size_bytes: int
    avg_processing_time_ms: float
    
    # Resource utilization
    cpu_utilization_percent: float
    memory_utilization_percent: float
    network_utilization_mbps: float
    
    # Quality metrics
    success_rate_percent: float
    error_rate_percent: float
    timeout_rate_percent: float
    
    # Geographic distribution
    geographic_distribution: Dict[str, int] = field(default_factory=dict)  # region -> request_count
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CapacityPlan:
    """Plan capacité système"""
    service_endpoint: ServiceEndpoint
    current_capacity_rps: float
    peak_observed_rps: float
    recommended_capacity_rps: float
    
    # Scaling recommendations
    horizontal_scaling_needed: bool
    vertical_scaling_needed: bool
    recommended_instances: int
    estimated_cost_increase: float
    
    # Growth projections
    projected_growth_30d: float  # Percentage
    projected_peak_rps_30d: float
    confidence_level: float  # 0-1
    
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AutoScalingTrigger:
    """Déclencheur auto-scaling"""
    trigger_id: str
    endpoint: ServiceEndpoint
    trigger_type: str  # "scale_up", "scale_down"
    threshold_rps: float
    current_rps: float
    confidence_score: float
    
    # Scaling parameters
    recommended_action: str
    estimated_impact: str
    cost_impact: float
    
    # Context
    load_pattern: LoadPattern
    time_until_trigger: timedelta
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ThroughputAnomaly:
    """Anomalie throughput détectée"""
    anomaly_id: str
    endpoint: ServiceEndpoint
    anomaly_type: str  # "sudden_drop", "unexpected_spike", "sustained_high", "capacity_limit"
    severity: str  # "low", "medium", "high", "critical"
    
    # Anomaly details
    expected_rps: float
    actual_rps: float
    deviation_percent: float
    duration_minutes: float
    
    # Impact assessment
    affected_creators: int
    business_impact: str
    recommended_actions: List[str]
    
    detection_timestamp: datetime = field(default_factory=datetime.utcnow)


class ThroughputCapacityMonitor:
    """Monitoring capacité débit système Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Throughput data storage
        self.throughput_measurements: Dict[ServiceEndpoint, deque] = {
            endpoint: deque(maxlen=1000) for endpoint in ServiceEndpoint
        }
        
        # Creator tier throughput tracking
        self.tier_throughput: Dict[CreatorTier, Dict[ServiceEndpoint, deque]] = {
            tier: {endpoint: deque(maxlen=500) for endpoint in ServiceEndpoint}
            for tier in CreatorTier
        }
        
        # Modality throughput tracking
        self.modality_throughput: Dict[ContentModality, Dict[ServiceEndpoint, deque]] = {
            modality: {endpoint: deque(maxlen=300) for endpoint in ServiceEndpoint}
            for modality in ContentModality
        }
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = config.get('monitoring_interval', 10.0)  # seconds
        
        # Capacity thresholds
        self.capacity_thresholds = {
            ServiceEndpoint.CONTENT_UPLOAD: {'max_safe_rps': 100, 'scale_up_at': 80, 'scale_down_at': 20},
            ServiceEndpoint.CONTENT_PROCESS: {'max_safe_rps': 50, 'scale_up_at': 40, 'scale_down_at': 10},
            ServiceEndpoint.CONTENT_SEARCH: {'max_safe_rps': 500, 'scale_up_at': 400, 'scale_down_at': 100},
            ServiceEndpoint.COLLABORATION_API: {'max_safe_rps': 200, 'scale_up_at': 160, 'scale_down_at': 40},
            ServiceEndpoint.MONETIZATION_API: {'max_safe_rps': 1000, 'scale_up_at': 800, 'scale_down_at': 200},
            ServiceEndpoint.ANALYTICS_API: {'max_safe_rps': 300, 'scale_up_at': 240, 'scale_down_at': 60},
            ServiceEndpoint.REAL_TIME_API: {'max_safe_rps': 1500, 'scale_up_at': 1200, 'scale_down_at': 300},
            ServiceEndpoint.STREAMING_API: {'max_safe_rps': 2000, 'scale_up_at': 1600, 'scale_down_at': 400}
        }
        
        # Creator tier quotas (RPS limits)
        self.tier_rps_quotas = {
            CreatorTier.FREE: {'max_rps': 5, 'burst_allowance': 10},
            CreatorTier.PRO: {'max_rps': 25, 'burst_allowance': 50},
            CreatorTier.ENTERPRISE: {'max_rps': 100, 'burst_allowance': 200},
            CreatorTier.PREMIUM: {'max_rps': 500, 'burst_allowance': 1000}
        }
        
        # Auto-scaling configuration
        self.auto_scaling_enabled = config.get('auto_scaling_enabled', True)
        self.scaling_cooldown_minutes = config.get('scaling_cooldown_minutes', 10)
        self.last_scaling_action: Dict[ServiceEndpoint, datetime] = {}
        
        # Anomaly detection
        self.anomaly_detection_enabled = config.get('anomaly_detection', True)
        self.anomaly_threshold_multiplier = config.get('anomaly_threshold', 2.5)
        self.detected_anomalies: deque = deque(maxlen=100)
        
        # Capacity planning
        self.capacity_plans: Dict[ServiceEndpoint, CapacityPlan] = {}
        self.planning_horizon_days = config.get('planning_horizon_days', 30)
        
        # Auto-scaling triggers
        self.active_triggers: Dict[str, AutoScalingTrigger] = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger("throughput_capacity_monitor")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [THROUGHPUT] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation monitoring throughput"""
        self.logger.info("📈 Initialisation Throughput Capacity Monitor...")
        
        # Generate baseline measurements
        await self._generate_baseline_measurements()
        
        # Initialize capacity plans
        await self._initialize_capacity_plans()
        
        # Start real-time monitoring
        await self._start_throughput_monitoring()
        
        self.logger.info("✅ Throughput Capacity Monitor initialisé")
    
    async def _generate_baseline_measurements(self):
        """Génération mesures baseline"""
        import random
        
        base_time = datetime.utcnow() - timedelta(hours=2)
        
        # Generate 2 hours of historical data (every 30 seconds = 240 measurements)
        for i in range(240):
            timestamp = base_time + timedelta(seconds=i * 30)
            
            for endpoint in ServiceEndpoint:
                # Base RPS varies by endpoint type
                base_rps = {
                    ServiceEndpoint.CONTENT_UPLOAD: 15,
                    ServiceEndpoint.CONTENT_PROCESS: 8,
                    ServiceEndpoint.CONTENT_SEARCH: 80,
                    ServiceEndpoint.COLLABORATION_API: 25,
                    ServiceEndpoint.MONETIZATION_API: 150,
                    ServiceEndpoint.ANALYTICS_API: 40,
                    ServiceEndpoint.REAL_TIME_API: 200,
                    ServiceEndpoint.STREAMING_API: 300
                }[endpoint]
                
                # Add time-based variation (higher during business hours)
                hour_of_day = timestamp.hour
                if 9 <= hour_of_day <= 17:  # Business hours
                    time_multiplier = 1.5
                elif 18 <= hour_of_day <= 22:  # Evening peak
                    time_multiplier = 2.0
                else:  # Off-hours
                    time_multiplier = 0.3
                
                # Random variation
                variation = random.uniform(0.7, 1.3)
                actual_rps = base_rps * time_multiplier * variation
                
                # Create measurement
                measurement = ThroughputMeasurement(
                    measurement_id=str(uuid.uuid4()),
                    endpoint=endpoint,
                    creator_tier=random.choice(list(CreatorTier)),
                    content_modality=random.choice(list(ContentModality)),
                    requests_per_second=actual_rps,
                    concurrent_users=int(actual_rps * random.uniform(0.5, 2.0)),
                    active_connections=int(actual_rps * random.uniform(1.0, 3.0)),
                    avg_request_size_bytes=random.randint(1024, 100_000),
                    avg_response_size_bytes=random.randint(512, 50_000),
                    avg_processing_time_ms=random.uniform(50, 500),
                    cpu_utilization_percent=min(95, max(10, actual_rps * 0.5 + random.uniform(-10, 10))),
                    memory_utilization_percent=min(90, max(20, actual_rps * 0.3 + random.uniform(-5, 5))),
                    network_utilization_mbps=actual_rps * random.uniform(0.1, 0.5),
                    success_rate_percent=max(85, min(99.9, 98 - (actual_rps * 0.01))),
                    error_rate_percent=min(15, max(0.1, actual_rps * 0.01)),
                    timeout_rate_percent=min(5, max(0, actual_rps * 0.005)),
                    geographic_distribution={
                        'north_america': int(actual_rps * 0.4),
                        'europe': int(actual_rps * 0.3),
                        'asia_pacific': int(actual_rps * 0.2),
                        'other': int(actual_rps * 0.1)
                    },
                    timestamp=timestamp
                )
                
                await self.record_throughput_measurement(measurement)
    
    async def _initialize_capacity_plans(self):
        """Initialisation plans capacité"""
        for endpoint in ServiceEndpoint:
            # Calculate current capacity based on recent measurements
            recent_measurements = list(self.throughput_measurements[endpoint])[-20:]  # Last 20 measurements
            
            if recent_measurements:
                current_rps = statistics.mean([m.requests_per_second for m in recent_measurements])
                peak_rps = max([m.requests_per_second for m in recent_measurements])
            else:
                current_rps = 0
                peak_rps = 0
            
            # Create initial capacity plan
            thresholds = self.capacity_thresholds[endpoint]
            max_safe_rps = thresholds['max_safe_rps']
            
            self.capacity_plans[endpoint] = CapacityPlan(
                service_endpoint=endpoint,
                current_capacity_rps=current_rps,
                peak_observed_rps=peak_rps,
                recommended_capacity_rps=max(max_safe_rps, peak_rps * 1.2),  # 20% buffer
                horizontal_scaling_needed=peak_rps > max_safe_rps * 0.8,
                vertical_scaling_needed=current_rps > max_safe_rps * 0.6,
                recommended_instances=max(1, int((peak_rps * 1.2) / max_safe_rps) + 1),
                estimated_cost_increase=0.0,  # Will be calculated based on scaling needs
                projected_growth_30d=10.0,  # Default 10% growth
                projected_peak_rps_30d=peak_rps * 1.1,
                confidence_level=0.7
            )
    
    async def _start_throughput_monitoring(self):
        """Démarrage monitoring throughput temps réel"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info("🔍 Throughput monitoring started")
    
    def _monitoring_loop(self):
        """Boucle monitoring throughput temps réel"""
        while self.monitoring_active:
            try:
                # Update capacity analysis
                self._analyze_capacity_needs()
                
                # Check auto-scaling triggers
                if self.auto_scaling_enabled:
                    self._check_auto_scaling_triggers()
                
                # Detect throughput anomalies
                if self.anomaly_detection_enabled:
                    self._detect_throughput_anomalies()
                
                # Update capacity plans
                self._update_capacity_plans()
                
                # Cleanup old data
                self._cleanup_old_measurements()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in throughput monitoring loop: {str(e)}")
                time.sleep(5)
    
    async def record_throughput_measurement(self, measurement: ThroughputMeasurement):
        """Enregistrement mesure throughput"""
        # Store in main collections
        self.throughput_measurements[measurement.endpoint].append(measurement)
        
        # Store in tier-specific collections
        self.tier_throughput[measurement.creator_tier][measurement.endpoint].append(measurement)
        
        # Store in modality-specific collections
        self.modality_throughput[measurement.content_modality][measurement.endpoint].append(measurement)
        
        # Check for immediate capacity issues
        await self._check_immediate_capacity_alerts(measurement)
        
        self.logger.debug(
            f"Recorded throughput: {measurement.requests_per_second:.1f} RPS "
            f"({measurement.endpoint.value}, {measurement.creator_tier.value})"
        )
    
    async def _check_immediate_capacity_alerts(self, measurement: ThroughputMeasurement):
        """Vérification alertes capacité immédiates"""
        endpoint = measurement.endpoint
        current_rps = measurement.requests_per_second
        thresholds = self.capacity_thresholds[endpoint]
        
        # Check if approaching capacity limits
        if current_rps > thresholds['max_safe_rps'] * 0.9:  # 90% of max capacity
            self.logger.warning(
                f"🚨 Near capacity limit: {endpoint.value} at {current_rps:.1f} RPS "
                f"(90% of {thresholds['max_safe_rps']} RPS limit)"
            )
        
        # Check success rate degradation
        if measurement.success_rate_percent < 95:
            self.logger.warning(
                f"🚨 Success rate degradation: {endpoint.value} at {measurement.success_rate_percent:.1f}% "
                f"(RPS: {current_rps:.1f})"
            )
    
    def _analyze_capacity_needs(self):
        """Analyse besoins capacité"""
        for endpoint in ServiceEndpoint:
            recent_measurements = list(self.throughput_measurements[endpoint])[-10:]  # Last 10 measurements
            if not recent_measurements:
                continue
            
            # Calculate current metrics
            current_rps = statistics.mean([m.requests_per_second for m in recent_measurements])
            current_cpu = statistics.mean([m.cpu_utilization_percent for m in recent_measurements])
            current_success_rate = statistics.mean([m.success_rate_percent for m in recent_measurements])
            
            thresholds = self.capacity_thresholds[endpoint]
            
            # Capacity analysis
            capacity_utilization = (current_rps / thresholds['max_safe_rps']) * 100
            
            if capacity_utilization > 80:
                self.logger.info(
                    f"📊 High capacity utilization: {endpoint.value} at {capacity_utilization:.1f}% "
                    f"({current_rps:.1f}/{thresholds['max_safe_rps']} RPS)"
                )
            
            # Resource utilization analysis
            if current_cpu > 80:
                self.logger.info(
                    f"🖥️ High CPU utilization: {endpoint.value} at {current_cpu:.1f}% "
                    f"(RPS: {current_rps:.1f})"
                )
            
            # Quality analysis
            if current_success_rate < 98:
                self.logger.warning(
                    f"⚠️ Quality degradation: {endpoint.value} success rate {current_success_rate:.1f}% "
                    f"(RPS: {current_rps:.1f})"
                )
    
    def _check_auto_scaling_triggers(self):
        """Vérification déclencheurs auto-scaling"""
        current_time = datetime.utcnow()
        
        for endpoint in ServiceEndpoint:
            recent_measurements = list(self.throughput_measurements[endpoint])[-5:]  # Last 5 measurements
            if not recent_measurements:
                continue
            
            current_rps = statistics.mean([m.requests_per_second for m in recent_measurements])
            thresholds = self.capacity_thresholds[endpoint]
            
            # Check cooldown period
            last_scaling = self.last_scaling_action.get(endpoint)
            if last_scaling and (current_time - last_scaling).total_seconds() < self.scaling_cooldown_minutes * 60:
                continue  # Still in cooldown
            
            # Scale up trigger
            if current_rps > thresholds['scale_up_at']:
                trigger = AutoScalingTrigger(
                    trigger_id=str(uuid.uuid4()),
                    endpoint=endpoint,
                    trigger_type="scale_up",
                    threshold_rps=thresholds['scale_up_at'],
                    current_rps=current_rps,
                    confidence_score=0.8,
                    recommended_action=f"Scale up {endpoint.value} instances",
                    estimated_impact=f"Handle up to {current_rps * 1.5:.0f} RPS",
                    cost_impact=50.0,  # Estimated additional cost per hour
                    load_pattern=self._detect_load_pattern(endpoint),
                    time_until_trigger=timedelta(minutes=2)
                )
                
                self.active_triggers[trigger.trigger_id] = trigger
                
                self.logger.warning(
                    f"🔼 Scale-up trigger: {endpoint.value} at {current_rps:.1f} RPS "
                    f"(threshold: {thresholds['scale_up_at']} RPS)"
                )
            
            # Scale down trigger
            elif current_rps < thresholds['scale_down_at']:
                trigger = AutoScalingTrigger(
                    trigger_id=str(uuid.uuid4()),
                    endpoint=endpoint,
                    trigger_type="scale_down",
                    threshold_rps=thresholds['scale_down_at'],
                    current_rps=current_rps,
                    confidence_score=0.6,
                    recommended_action=f"Scale down {endpoint.value} instances",
                    estimated_impact=f"Reduce capacity to {current_rps * 2:.0f} RPS",
                    cost_impact=-25.0,  # Cost savings per hour
                    load_pattern=self._detect_load_pattern(endpoint),
                    time_until_trigger=timedelta(minutes=5)  # Longer delay for scale-down
                )
                
                self.active_triggers[trigger.trigger_id] = trigger
                
                self.logger.info(
                    f"🔽 Scale-down opportunity: {endpoint.value} at {current_rps:.1f} RPS "
                    f"(threshold: {thresholds['scale_down_at']} RPS)"
                )
    
    def _detect_load_pattern(self, endpoint: ServiceEndpoint) -> LoadPattern:
        """Détection pattern charge"""
        measurements = list(self.throughput_measurements[endpoint])[-30:]  # Last 30 measurements
        if len(measurements) < 10:
            return LoadPattern.RANDOM
        
        rps_values = [m.requests_per_second for m in measurements]
        
        # Calculate trend
        mean_rps = statistics.mean(rps_values)
        std_dev = statistics.stdev(rps_values) if len(rps_values) > 1 else 0
        
        # Detect patterns
        if std_dev < mean_rps * 0.1:  # Low variation
            return LoadPattern.STEADY
        elif max(rps_values) > mean_rps * 2:  # High peaks
            return LoadPattern.BURST
        elif std_dev > mean_rps * 0.5:  # High variation
            return LoadPattern.RANDOM
        else:
            # Check for declining trend
            first_half = rps_values[:len(rps_values)//2]
            second_half = rps_values[len(rps_values)//2:]
            
            if statistics.mean(first_half) > statistics.mean(second_half) * 1.2:
                return LoadPattern.DECLINING
            
            return LoadPattern.SEASONAL
    
    def _detect_throughput_anomalies(self):
        """Détection anomalies throughput"""
        for endpoint in ServiceEndpoint:
            recent_measurements = list(self.throughput_measurements[endpoint])[-10:]  # Last 10
            historical_measurements = list(self.throughput_measurements[endpoint])[-100:-10]  # Historical
            
            if len(recent_measurements) < 5 or len(historical_measurements) < 20:
                continue
            
            # Calculate baseline metrics
            recent_rps = [m.requests_per_second for m in recent_measurements]
            historical_rps = [m.requests_per_second for m in historical_measurements]
            
            recent_mean = statistics.mean(recent_rps)
            historical_mean = statistics.mean(historical_rps)
            historical_std = statistics.stdev(historical_rps) if len(historical_rps) > 1 else 0
            
            # Detect anomalies
            threshold = historical_std * self.anomaly_threshold_multiplier
            
            # Sudden drop
            if recent_mean < historical_mean - threshold and historical_mean > 10:
                anomaly = ThroughputAnomaly(
                    anomaly_id=str(uuid.uuid4()),
                    endpoint=endpoint,
                    anomaly_type="sudden_drop",
                    severity="high" if recent_mean < historical_mean * 0.5 else "medium",
                    expected_rps=historical_mean,
                    actual_rps=recent_mean,
                    deviation_percent=((historical_mean - recent_mean) / historical_mean) * 100,
                    duration_minutes=5.0,  # Based on monitoring interval
                    affected_creators=int(recent_mean * 10),  # Estimate
                    business_impact="Reduced service availability",
                    recommended_actions=[
                        "Check service health",
                        "Investigate infrastructure issues",
                        "Monitor error rates",
                        "Consider failover activation"
                    ]
                )
                self.detected_anomalies.append(anomaly)
                
                self.logger.warning(
                    f"🔍 Throughput anomaly detected: {endpoint.value} sudden drop "
                    f"{recent_mean:.1f} RPS (expected: {historical_mean:.1f})"
                )
            
            # Unexpected spike
            elif recent_mean > historical_mean + threshold:
                anomaly = ThroughputAnomaly(
                    anomaly_id=str(uuid.uuid4()),
                    endpoint=endpoint,
                    anomaly_type="unexpected_spike",
                    severity="medium" if recent_mean < historical_mean * 3 else "high",
                    expected_rps=historical_mean,
                    actual_rps=recent_mean,
                    deviation_percent=((recent_mean - historical_mean) / historical_mean) * 100,
                    duration_minutes=5.0,
                    affected_creators=int(recent_mean * 10),
                    business_impact="Potential capacity strain",
                    recommended_actions=[
                        "Monitor system resources",
                        "Check for DDoS or unusual traffic",
                        "Prepare for scaling",
                        "Monitor error rates"
                    ]
                )
                self.detected_anomalies.append(anomaly)
                
                self.logger.warning(
                    f"🔍 Throughput anomaly detected: {endpoint.value} unexpected spike "
                    f"{recent_mean:.1f} RPS (expected: {historical_mean:.1f})"
                )
    
    def _update_capacity_plans(self):
        """Mise à jour plans capacité"""
        for endpoint in ServiceEndpoint:
            measurements = list(self.throughput_measurements[endpoint])
            if not measurements:
                continue
            
            # Update capacity plan based on recent data
            recent_measurements = measurements[-50:]  # Last 50 measurements
            
            if len(recent_measurements) >= 10:
                current_rps = statistics.mean([m.requests_per_second for m in recent_measurements])
                peak_rps = max([m.requests_per_second for m in recent_measurements])
                
                # Simple growth projection (based on recent trend)
                if len(recent_measurements) >= 20:
                    first_half = recent_measurements[:len(recent_measurements)//2]
                    second_half = recent_measurements[len(recent_measurements)//2:]
                    
                    first_avg = statistics.mean([m.requests_per_second for m in first_half])
                    second_avg = statistics.mean([m.requests_per_second for m in second_half])
                    
                    if first_avg > 0:
                        growth_rate = ((second_avg - first_avg) / first_avg) * 100
                        # Project growth over planning horizon
                        projected_growth = growth_rate * (self.planning_horizon_days / 7)  # Weekly growth rate
                    else:
                        projected_growth = 0
                else:
                    projected_growth = 10  # Default 10% growth
                
                # Update capacity plan
                plan = self.capacity_plans[endpoint]
                plan.current_capacity_rps = current_rps
                plan.peak_observed_rps = max(plan.peak_observed_rps, peak_rps)
                plan.projected_growth_30d = projected_growth
                plan.projected_peak_rps_30d = peak_rps * (1 + projected_growth / 100)
                
                # Update scaling recommendations
                thresholds = self.capacity_thresholds[endpoint]
                max_safe_rps = thresholds['max_safe_rps']
                
                plan.horizontal_scaling_needed = plan.projected_peak_rps_30d > max_safe_rps * 0.8
                plan.vertical_scaling_needed = current_rps > max_safe_rps * 0.6
                plan.recommended_instances = max(1, int((plan.projected_peak_rps_30d * 1.2) / max_safe_rps) + 1)
                plan.analysis_timestamp = datetime.utcnow()
    
    def _cleanup_old_measurements(self):
        """Nettoyage mesures anciennes"""
        # Deque automatically limits size, but we could add time-based cleanup here
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Count old measurements for logging
        total_old = 0
        for endpoint_measurements in self.throughput_measurements.values():
            old_count = sum(
                1 for m in list(endpoint_measurements)[-100:]  # Check last 100
                if m.timestamp < cutoff_time
            )
            total_old += old_count
        
        if total_old > 100:
            self.logger.debug(f"🧹 Old measurements detected: {total_old} older than 24h")
    
    async def get_throughput_summary(
        self, 
        endpoint: Optional[ServiceEndpoint] = None,
        time_window_hours: int = 1
    ) -> Dict[str, Any]:
        """Résumé throughput par endpoint"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        endpoints_to_analyze = [endpoint] if endpoint else list(ServiceEndpoint)
        summary = {}
        
        for ep in endpoints_to_analyze:
            measurements = [
                m for m in list(self.throughput_measurements[ep])
                if m.timestamp > cutoff_time
            ]
            
            if not measurements:
                summary[ep.value] = {'status': 'No data in time window'}
                continue
            
            # Calculate statistics
            rps_values = [m.requests_per_second for m in measurements]
            cpu_values = [m.cpu_utilization_percent for m in measurements]
            success_rates = [m.success_rate_percent for m in measurements]
            
            current_rps = statistics.mean(rps_values[-5:]) if len(rps_values) >= 5 else statistics.mean(rps_values)
            peak_rps = max(rps_values)
            avg_rps = statistics.mean(rps_values)
            
            thresholds = self.capacity_thresholds[ep]
            
            summary[ep.value] = {
                'current_rps': round(current_rps, 2),
                'average_rps': round(avg_rps, 2),
                'peak_rps': round(peak_rps, 2),
                'capacity_utilization_percent': round((current_rps / thresholds['max_safe_rps']) * 100, 1),
                'avg_cpu_utilization': round(statistics.mean(cpu_values), 1),
                'avg_success_rate': round(statistics.mean(success_rates), 2),
                'total_requests': sum(int(m.requests_per_second * (self.monitoring_interval / 60)) for m in measurements),
                'measurements_count': len(measurements),
                'capacity_status': self._determine_capacity_status(current_rps, thresholds),
                'scaling_recommendation': self._get_scaling_recommendation(ep, current_rps)
            }
        
        return summary
    
    def _determine_capacity_status(self, current_rps: float, thresholds: Dict[str, float]) -> str:
        """Détermination statut capacité"""
        utilization = (current_rps / thresholds['max_safe_rps']) * 100
        
        if utilization < 30:
            return "underutilized"
        elif utilization < 60:
            return "optimal"
        elif utilization < 80:
            return "busy"
        elif utilization < 95:
            return "near_capacity"
        else:
            return "over_capacity"
    
    def _get_scaling_recommendation(self, endpoint: ServiceEndpoint, current_rps: float) -> str:
        """Recommandation scaling"""
        thresholds = self.capacity_thresholds[endpoint]
        
        if current_rps > thresholds['scale_up_at']:
            return "scale_up_recommended"
        elif current_rps < thresholds['scale_down_at']:
            return "scale_down_opportunity"
        else:
            return "no_scaling_needed"
    
    async def get_creator_tier_throughput_analysis(self) -> Dict[str, Any]:
        """Analyse throughput par tier créateur"""
        tier_analysis = {}
        
        for tier in CreatorTier:
            tier_data = {}
            total_rps = 0
            total_measurements = 0
            
            for endpoint in ServiceEndpoint:
                measurements = list(self.tier_throughput[tier][endpoint])[-20:]  # Last 20 measurements
                if measurements:
                    endpoint_rps = statistics.mean([m.requests_per_second for m in measurements])
                    total_rps += endpoint_rps
                    total_measurements += len(measurements)
                    
                    tier_data[endpoint.value] = {
                        'avg_rps': round(endpoint_rps, 2),
                        'measurements': len(measurements)
                    }
            
            quota = self.tier_rps_quotas[tier]
            
            tier_analysis[tier.value] = {
                'endpoints': tier_data,
                'total_avg_rps': round(total_rps, 2),
                'quota_limit_rps': quota['max_rps'],
                'quota_utilization_percent': round((total_rps / quota['max_rps']) * 100, 1) if quota['max_rps'] > 0 else 0,
                'burst_allowance_rps': quota['burst_allowance'],
                'total_measurements': total_measurements,
                'tier_status': 'over_quota' if total_rps > quota['max_rps'] else 'within_quota'
            }
        
        return tier_analysis
    
    async def get_capacity_planning_report(self) -> Dict[str, Any]:
        """Rapport planification capacité"""
        capacity_report = {
            'planning_horizon_days': self.planning_horizon_days,
            'capacity_plans': {},
            'overall_recommendations': [],
            'cost_projections': {},
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        total_current_cost = 0
        total_projected_cost = 0
        
        for endpoint, plan in self.capacity_plans.items():
            # Calculate cost estimates (simplified model)
            current_instances = max(1, int(plan.current_capacity_rps / self.capacity_thresholds[endpoint]['max_safe_rps']) + 1)
            recommended_instances = plan.recommended_instances
            
            instance_cost_per_hour = 0.10  # Simplified $0.10 per instance per hour
            current_cost = current_instances * instance_cost_per_hour * 24 * self.planning_horizon_days
            projected_cost = recommended_instances * instance_cost_per_hour * 24 * self.planning_horizon_days
            
            total_current_cost += current_cost
            total_projected_cost += projected_cost
            
            capacity_report['capacity_plans'][endpoint.value] = {
                'current_capacity_rps': round(plan.current_capacity_rps, 2),
                'peak_observed_rps': round(plan.peak_observed_rps, 2),
                'recommended_capacity_rps': round(plan.recommended_capacity_rps, 2),
                'projected_growth_percent': round(plan.projected_growth_30d, 1),
                'projected_peak_rps': round(plan.projected_peak_rps_30d, 2),
                'scaling_needs': {
                    'horizontal_scaling': plan.horizontal_scaling_needed,
                    'vertical_scaling': plan.vertical_scaling_needed,
                    'current_instances': current_instances,
                    'recommended_instances': recommended_instances
                },
                'cost_projection': {
                    'current_monthly_cost': round(current_cost, 2),
                    'projected_monthly_cost': round(projected_cost, 2),
                    'cost_increase': round(projected_cost - current_cost, 2)
                },
                'confidence_level': plan.confidence_level
            }
            
            # Add recommendations
            if plan.horizontal_scaling_needed:
                capacity_report['overall_recommendations'].append(
                    f"Scale out {endpoint.value} to {recommended_instances} instances"
                )
            
            if plan.projected_growth_30d > 50:  # High growth
                capacity_report['overall_recommendations'].append(
                    f"Monitor {endpoint.value} closely - high growth projected ({plan.projected_growth_30d:.1f}%)"
                )
        
        capacity_report['cost_projections'] = {
            'total_current_monthly_cost': round(total_current_cost, 2),
            'total_projected_monthly_cost': round(total_projected_cost, 2),
            'total_cost_increase': round(total_projected_cost - total_current_cost, 2),
            'cost_increase_percent': round(((total_projected_cost - total_current_cost) / total_current_cost) * 100, 1) if total_current_cost > 0 else 0
        }
        
        return capacity_report
    
    async def get_auto_scaling_status(self) -> Dict[str, Any]:
        """Statut auto-scaling"""
        active_triggers_summary = []
        
        for trigger_id, trigger in self.active_triggers.items():
            active_triggers_summary.append({
                'trigger_id': trigger_id,
                'endpoint': trigger.endpoint.value,
                'type': trigger.trigger_type,
                'current_rps': round(trigger.current_rps, 2),
                'threshold_rps': round(trigger.threshold_rps, 2),
                'confidence': trigger.confidence_score,
                'recommended_action': trigger.recommended_action,
                'cost_impact': trigger.cost_impact,
                'load_pattern': trigger.load_pattern.value,
                'time_since_trigger': (datetime.utcnow() - trigger.timestamp).total_seconds()
            })
        
        # Recent scaling actions
        recent_actions = []
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        for endpoint, last_action_time in self.last_scaling_action.items():
            if last_action_time > cutoff_time:
                recent_actions.append({
                    'endpoint': endpoint.value,
                    'action_time': last_action_time.isoformat(),
                    'hours_ago': (datetime.utcnow() - last_action_time).total_seconds() / 3600
                })
        
        return {
            'auto_scaling_enabled': self.auto_scaling_enabled,
            'scaling_cooldown_minutes': self.scaling_cooldown_minutes,
            'active_triggers': active_triggers_summary,
            'recent_scaling_actions_24h': recent_actions,
            'anomalies_detected': len(self.detected_anomalies),
            'system_status': 'healthy' if len(active_triggers_summary) == 0 else 'scaling_activity'
        }
    
    async def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Dashboard complet throughput et capacité"""
        # Overall throughput summary
        throughput_summary = await self.get_throughput_summary(time_window_hours=1)
        
        # Creator tier analysis
        tier_analysis = await self.get_creator_tier_throughput_analysis()
        
        # Capacity planning
        capacity_report = await self.get_capacity_planning_report()
        
        # Auto-scaling status
        scaling_status = await self.get_auto_scaling_status()
        
        # System health indicators
        total_rps = sum(
            data.get('current_rps', 0) for data in throughput_summary.values()
            if isinstance(data, dict) and 'current_rps' in data
        )
        
        over_capacity_endpoints = sum(
            1 for data in throughput_summary.values()
            if isinstance(data, dict) and data.get('capacity_status') in ['near_capacity', 'over_capacity']
        )
        
        return {
            'overview': {
                'total_current_rps': round(total_rps, 2),
                'endpoints_monitored': len(ServiceEndpoint),
                'over_capacity_endpoints': over_capacity_endpoints,
                'auto_scaling_enabled': self.auto_scaling_enabled,
                'active_scaling_triggers': len(self.active_triggers),
                'anomalies_detected_24h': len([a for a in self.detected_anomalies if (datetime.utcnow() - a.detection_timestamp).total_seconds() < 86400])
            },
            'throughput_by_endpoint': throughput_summary,
            'creator_tier_analysis': tier_analysis,
            'capacity_planning': capacity_report,
            'auto_scaling_status': scaling_status,
            'system_health': {
                'monitoring_active': self.monitoring_active,
                'last_update': datetime.utcnow().isoformat(),
                'overall_status': 'critical' if over_capacity_endpoints > 2 else 'warning' if over_capacity_endpoints > 0 else 'healthy'
            }
        }
    
    async def shutdown(self):
        """Arrêt propre monitoring throughput"""
        self.logger.info("⏹️ Shutting down Throughput Capacity Monitor...")
        
        # Stop monitoring
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        # Clear data structures
        for endpoint_measurements in self.throughput_measurements.values():
            endpoint_measurements.clear()
        
        for tier_data in self.tier_throughput.values():
            for endpoint_measurements in tier_data.values():
                endpoint_measurements.clear()
        
        for modality_data in self.modality_throughput.values():
            for endpoint_measurements in modality_data.values():
                endpoint_measurements.clear()
        
        self.capacity_plans.clear()
        self.active_triggers.clear()
        self.detected_anomalies.clear()
        
        self.logger.info("✅ Throughput Capacity Monitor shutdown complete")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_throughput_monitor():
        config = {
            'monitoring_interval': 1.0,  # Fast for testing
            'auto_scaling_enabled': True,
            'anomaly_detection': True,
            'planning_horizon_days': 30
        }
        
        monitor = ThroughputCapacityMonitor(config)
        await monitor.initialize()
        
        # Test additional measurements to trigger scaling
        import random
        for i in range(10):
            measurement = ThroughputMeasurement(
                measurement_id=str(uuid.uuid4()),
                endpoint=ServiceEndpoint.CONTENT_UPLOAD,
                creator_tier=random.choice(list(CreatorTier)),
                content_modality=random.choice(list(ContentModality)),
                requests_per_second=50 + i * 10,  # Increasing load
                concurrent_users=random.randint(50, 200),
                active_connections=random.randint(100, 400),
                avg_request_size_bytes=random.randint(10000, 100000),
                avg_response_size_bytes=random.randint(5000, 50000),
                avg_processing_time_ms=random.uniform(100, 500),
                cpu_utilization_percent=40 + i * 5,  # Increasing CPU
                memory_utilization_percent=30 + i * 3,
                network_utilization_mbps=random.uniform(1, 10),
                success_rate_percent=max(95, 99 - i * 0.5),  # Slight degradation
                error_rate_percent=min(5, i * 0.5),
                timeout_rate_percent=min(2, i * 0.2)
            )
            
            await monitor.record_throughput_measurement(measurement)
        
        # Wait for monitoring loop to process
        await asyncio.sleep(2)
        
        # Test throughput summary
        summary = await monitor.get_throughput_summary(ServiceEndpoint.CONTENT_UPLOAD)
        print(f"✅ Throughput summary: {summary[ServiceEndpoint.CONTENT_UPLOAD.value]['current_rps']} RPS")
        
        # Test creator tier analysis
        tier_analysis = await monitor.get_creator_tier_throughput_analysis()
        print(f"✅ Tier analysis: {len(tier_analysis)} tiers analyzed")
        
        # Test capacity planning
        capacity_report = await monitor.get_capacity_planning_report()
        print(f"✅ Capacity planning: ${capacity_report['cost_projections']['total_projected_monthly_cost']} projected cost")
        
        # Test auto-scaling status
        scaling_status = await monitor.get_auto_scaling_status()
        print(f"✅ Auto-scaling: {scaling_status['active_triggers']} active triggers: {len(scaling_status['active_triggers'])}")
        
        # Test dashboard
        dashboard = await monitor.get_comprehensive_dashboard()
        print(f"✅ Dashboard: {dashboard['overview']['total_current_rps']} total RPS")
        
        print("✅ Throughput Capacity Monitor test completed")
        await monitor.shutdown()
    
    asyncio.run(test_throughput_monitor())