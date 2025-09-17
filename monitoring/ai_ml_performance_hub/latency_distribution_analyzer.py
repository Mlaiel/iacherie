"""
⏱️ Latency Distribution Analyzer - Enterprise Creator Experience Optimization
============================================================================

Analyseur ultra-avancé distribution latence pour optimisation expérience Creator Economy.
Analyse P50/P95/P99, SLA compliance, geographic distribution et impact business.

Fonctionnalités:
- P50/P95/P99 latency tracking avec précision microseconde
- Latency breakdown par composant système (DB/Cache/ML/API)
- Creator experience latency impact analysis
- Geographic latency distribution (CDN optimization)
- SLA compliance monitoring et alerting automatique
- Tail latency optimization pour Creator tiers Premium
- Real-time latency anomaly detection
- Business impact correlation (latence -> conversion rate)
- Creator tier latency differentiation et prioritization

Architecture: monitoring/ai_ml_performance_hub/latency_distribution_analyzer.py
Responsabilité: Latency analytics, experience optimization, SLA compliance

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
import bisect


class CreatorTier(Enum):
    """Niveaux créateurs pour SLA différenciés"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class LatencyComponent(Enum):
    """Composants système pour breakdown latence"""
    API_GATEWAY = "api_gateway"
    AUTHENTICATION = "authentication"
    DATABASE = "database"
    CACHE = "cache"
    ML_INFERENCE = "ml_inference"
    FILE_STORAGE = "file_storage"
    CDN = "cdn"
    EXTERNAL_API = "external_api"
    PROCESSING = "processing"
    RESPONSE_SERIALIZATION = "response_serialization"


class GeographicRegion(Enum):
    """Régions géographiques pour distribution latence"""
    NORTH_AMERICA = "north_america"
    EUROPE = "europe" 
    ASIA_PACIFIC = "asia_pacific"
    SOUTH_AMERICA = "south_america"
    AFRICA = "africa"
    MIDDLE_EAST = "middle_east"
    OCEANIA = "oceania"


class RequestType(Enum):
    """Types requêtes pour analyse latence"""
    CONTENT_UPLOAD = "content_upload"
    CONTENT_PROCESSING = "content_processing"
    CONTENT_SEARCH = "content_search"
    COLLABORATION_MATCH = "collaboration_match"
    MONETIZATION_CALC = "monetization_calc"
    ANALYTICS_QUERY = "analytics_query"
    REAL_TIME_CHAT = "real_time_chat"
    LIVE_STREAMING = "live_streaming"


@dataclass
class LatencyMeasurement:
    """Mesure latence détaillée"""
    request_id: str
    creator_id: str
    creator_tier: CreatorTier
    request_type: RequestType
    geographic_region: GeographicRegion
    
    # Timing measurements (microseconds for precision)
    total_latency_us: int
    component_latencies: Dict[LatencyComponent, int]
    
    # Context information
    request_size_bytes: int
    response_size_bytes: int
    cache_hit: bool
    cdn_hit: bool
    
    # Network information
    client_ip: str
    user_agent: str
    connection_type: str
    
    # Business context
    conversion_event: bool = False  # Did this request lead to conversion?
    satisfaction_score: Optional[float] = None  # User satisfaction (1-10)
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LatencyPercentiles:
    """Percentiles latence calculés"""
    p50_us: int
    p90_us: int
    p95_us: int
    p99_us: int
    p99_9_us: int
    max_us: int
    min_us: int
    mean_us: float
    std_dev_us: float
    sample_count: int
    calculation_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SLAViolation:
    """Violation SLA latence"""
    violation_id: str
    creator_tier: CreatorTier
    request_type: RequestType
    sla_threshold_us: int
    actual_latency_us: int
    violation_severity: str  # "minor", "major", "critical"
    impact_description: str
    recommended_actions: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LatencyTrend:
    """Tendance latence temporelle"""
    time_period: str  # "hourly", "daily", "weekly"
    p95_trend: List[Tuple[datetime, float]]  # (timestamp, p95_latency_ms)
    improvement_percent: float  # Positive = improvement, negative = degradation
    trend_confidence: float  # 0-1
    anomaly_detected: bool
    seasonal_pattern: Optional[str] = None


class LatencyDistributionAnalyzer:
    """Analyseur distribution latence enterprise Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Latency data storage
        self.latency_measurements: deque = deque(maxlen=100000)  # Keep last 100k measurements
        self.measurements_by_tier: Dict[CreatorTier, deque] = {
            tier: deque(maxlen=20000) for tier in CreatorTier
        }
        self.measurements_by_region: Dict[GeographicRegion, deque] = {
            region: deque(maxlen=15000) for region in GeographicRegion
        }
        self.measurements_by_type: Dict[RequestType, deque] = {
            req_type: deque(maxlen=10000) for req_type in RequestType
        }
        
        # Real-time percentile tracking
        self.percentile_cache: Dict[str, LatencyPercentiles] = {}
        self.percentile_cache_ttl = config.get('percentile_cache_ttl', 30)  # seconds
        
        # SLA definitions (microseconds)
        self.sla_thresholds = {
            CreatorTier.FREE: {
                RequestType.CONTENT_UPLOAD: 5_000_000,      # 5s
                RequestType.CONTENT_PROCESSING: 30_000_000,  # 30s  
                RequestType.CONTENT_SEARCH: 2_000_000,      # 2s
                RequestType.COLLABORATION_MATCH: 3_000_000,  # 3s
                RequestType.MONETIZATION_CALC: 1_000_000,   # 1s
                RequestType.ANALYTICS_QUERY: 10_000_000,    # 10s
                RequestType.REAL_TIME_CHAT: 500_000,        # 500ms
                RequestType.LIVE_STREAMING: 200_000         # 200ms
            },
            CreatorTier.PRO: {
                RequestType.CONTENT_UPLOAD: 3_000_000,      # 3s
                RequestType.CONTENT_PROCESSING: 15_000_000,  # 15s
                RequestType.CONTENT_SEARCH: 1_000_000,      # 1s
                RequestType.COLLABORATION_MATCH: 2_000_000,  # 2s
                RequestType.MONETIZATION_CALC: 500_000,     # 500ms
                RequestType.ANALYTICS_QUERY: 5_000_000,     # 5s
                RequestType.REAL_TIME_CHAT: 300_000,        # 300ms
                RequestType.LIVE_STREAMING: 150_000         # 150ms
            },
            CreatorTier.ENTERPRISE: {
                RequestType.CONTENT_UPLOAD: 2_000_000,      # 2s
                RequestType.CONTENT_PROCESSING: 10_000_000,  # 10s
                RequestType.CONTENT_SEARCH: 500_000,        # 500ms
                RequestType.COLLABORATION_MATCH: 1_000_000,  # 1s
                RequestType.MONETIZATION_CALC: 300_000,     # 300ms
                RequestType.ANALYTICS_QUERY: 3_000_000,     # 3s
                RequestType.REAL_TIME_CHAT: 200_000,        # 200ms
                RequestType.LIVE_STREAMING: 100_000         # 100ms
            },
            CreatorTier.PREMIUM: {
                RequestType.CONTENT_UPLOAD: 1_000_000,      # 1s
                RequestType.CONTENT_PROCESSING: 5_000_000,   # 5s
                RequestType.CONTENT_SEARCH: 300_000,        # 300ms
                RequestType.COLLABORATION_MATCH: 500_000,    # 500ms
                RequestType.MONETIZATION_CALC: 200_000,     # 200ms
                RequestType.ANALYTICS_QUERY: 2_000_000,     # 2s
                RequestType.REAL_TIME_CHAT: 100_000,        # 100ms
                RequestType.LIVE_STREAMING: 50_000          # 50ms
            }
        }
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = config.get('monitoring_interval', 5.0)  # seconds
        
        # SLA violations tracking
        self.sla_violations: deque = deque(maxlen=1000)
        
        # Anomaly detection
        self.anomaly_threshold_multiplier = config.get('anomaly_threshold', 3.0)  # 3x standard deviation
        
        # Business impact tracking
        self.latency_conversion_correlation = {}  # Track latency vs conversion rates
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger("latency_distribution_analyzer")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [LATENCY] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation analyseur latence"""
        self.logger.info("⏱️ Initialisation Latency Distribution Analyzer...")
        
        # Initialize baseline measurements
        await self._generate_baseline_measurements()
        
        # Start real-time monitoring
        await self._start_latency_monitoring()
        
        self.logger.info("✅ Latency Distribution Analyzer initialisé")
    
    async def _generate_baseline_measurements(self):
        """Génération mesures baseline pour bootstrap"""
        import random
        
        # Generate realistic baseline data for each tier/region/type combination
        base_time = datetime.utcnow() - timedelta(hours=1)
        
        for i in range(1000):  # Generate 1000 baseline measurements
            # Vary timestamp
            timestamp = base_time + timedelta(seconds=i * 3.6)  # One per 3.6s over 1 hour
            
            # Random distribution of tiers, regions, types
            tier = random.choice(list(CreatorTier))
            region = random.choice(list(GeographicRegion))
            req_type = random.choice(list(RequestType))
            
            # Base latency varies by tier (Premium gets better performance)
            base_latency_multiplier = {
                CreatorTier.PREMIUM: 0.5,
                CreatorTier.ENTERPRISE: 0.7,
                CreatorTier.PRO: 1.0,
                CreatorTier.FREE: 1.5
            }[tier]
            
            # Base latency varies by request type
            type_base_latencies = {
                RequestType.CONTENT_UPLOAD: 2_000_000,      # 2s base
                RequestType.CONTENT_PROCESSING: 10_000_000, # 10s base
                RequestType.CONTENT_SEARCH: 500_000,        # 500ms base
                RequestType.COLLABORATION_MATCH: 1_000_000, # 1s base
                RequestType.MONETIZATION_CALC: 300_000,     # 300ms base
                RequestType.ANALYTICS_QUERY: 2_000_000,     # 2s base
                RequestType.REAL_TIME_CHAT: 150_000,        # 150ms base
                RequestType.LIVE_STREAMING: 75_000          # 75ms base
            }
            
            base_latency = type_base_latencies[req_type] * base_latency_multiplier
            
            # Add random variation (log-normal distribution for realistic tail latency)
            variation = random.lognormvariate(0, 0.5)  # Mean=1, some tail events
            total_latency = int(base_latency * variation)
            
            # Generate component breakdown
            component_latencies = self._generate_component_breakdown(total_latency, req_type)
            
            measurement = LatencyMeasurement(
                request_id=str(uuid.uuid4()),
                creator_id=f"creator_{random.randint(1, 1000)}",
                creator_tier=tier,
                request_type=req_type,
                geographic_region=region,
                total_latency_us=total_latency,
                component_latencies=component_latencies,
                request_size_bytes=random.randint(1024, 10_000_000),  # 1KB to 10MB
                response_size_bytes=random.randint(512, 1_000_000),   # 0.5KB to 1MB
                cache_hit=random.random() < 0.7,  # 70% cache hit rate
                cdn_hit=random.random() < 0.8,    # 80% CDN hit rate
                client_ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (Test Client)",
                connection_type=random.choice(["fiber", "4g", "5g", "wifi"]),
                conversion_event=random.random() < 0.05,  # 5% conversion rate
                satisfaction_score=random.uniform(7.0, 9.5) if total_latency < 1_000_000 else random.uniform(4.0, 7.0),
                timestamp=timestamp
            )
            
            await self.record_latency_measurement(measurement)
    
    def _generate_component_breakdown(
        self, 
        total_latency_us: int, 
        req_type: RequestType
    ) -> Dict[LatencyComponent, int]:
        """Génération répartition latence par composant"""
        import random
        
        # Define typical component distributions by request type
        component_distributions = {
            RequestType.CONTENT_UPLOAD: {
                LatencyComponent.API_GATEWAY: 0.02,
                LatencyComponent.AUTHENTICATION: 0.05,
                LatencyComponent.FILE_STORAGE: 0.70,
                LatencyComponent.DATABASE: 0.10,
                LatencyComponent.PROCESSING: 0.10,
                LatencyComponent.RESPONSE_SERIALIZATION: 0.03
            },
            RequestType.CONTENT_PROCESSING: {
                LatencyComponent.API_GATEWAY: 0.01,
                LatencyComponent.AUTHENTICATION: 0.02,
                LatencyComponent.ML_INFERENCE: 0.80,
                LatencyComponent.DATABASE: 0.05,
                LatencyComponent.FILE_STORAGE: 0.10,
                LatencyComponent.RESPONSE_SERIALIZATION: 0.02
            },
            RequestType.CONTENT_SEARCH: {
                LatencyComponent.API_GATEWAY: 0.05,
                LatencyComponent.AUTHENTICATION: 0.10,
                LatencyComponent.DATABASE: 0.60,
                LatencyComponent.CACHE: 0.15,
                LatencyComponent.PROCESSING: 0.08,
                LatencyComponent.RESPONSE_SERIALIZATION: 0.02
            },
            RequestType.REAL_TIME_CHAT: {
                LatencyComponent.API_GATEWAY: 0.10,
                LatencyComponent.AUTHENTICATION: 0.15,
                LatencyComponent.DATABASE: 0.30,
                LatencyComponent.CACHE: 0.25,
                LatencyComponent.PROCESSING: 0.15,
                LatencyComponent.RESPONSE_SERIALIZATION: 0.05
            }
        }
        
        # Use default distribution if request type not found
        distribution = component_distributions.get(req_type, {
            LatencyComponent.API_GATEWAY: 0.05,
            LatencyComponent.AUTHENTICATION: 0.10,
            LatencyComponent.DATABASE: 0.40,
            LatencyComponent.CACHE: 0.20,
            LatencyComponent.PROCESSING: 0.20,
            LatencyComponent.RESPONSE_SERIALIZATION: 0.05
        })
        
        # Allocate latency to components with some randomness
        component_latencies = {}
        remaining_latency = total_latency_us
        
        components = list(distribution.keys())
        for i, component in enumerate(components):
            if i == len(components) - 1:  # Last component gets remaining
                component_latencies[component] = remaining_latency
            else:
                base_allocation = int(total_latency_us * distribution[component])
                # Add some randomness (±30%)
                variation = random.uniform(0.7, 1.3)
                allocated = int(base_allocation * variation)
                allocated = min(allocated, remaining_latency)  # Don't exceed remaining
                component_latencies[component] = allocated
                remaining_latency -= allocated
        
        return component_latencies
    
    async def _start_latency_monitoring(self):
        """Démarrage monitoring latence temps réel"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info("🔍 Latency monitoring started")
    
    def _monitoring_loop(self):
        """Boucle monitoring latence temps réel"""
        while self.monitoring_active:
            try:
                # Update percentile calculations
                self._update_percentile_cache()
                
                # Check SLA violations
                self._check_sla_violations()
                
                # Detect anomalies
                self._detect_latency_anomalies()
                
                # Update business impact correlations
                self._update_business_correlations()
                
                # Cleanup old data
                self._cleanup_old_measurements()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in latency monitoring loop: {str(e)}")
                time.sleep(5)
    
    async def record_latency_measurement(self, measurement: LatencyMeasurement):
        """Enregistrement mesure latence"""
        # Store in main collection
        self.latency_measurements.append(measurement)
        
        # Store in segmented collections
        self.measurements_by_tier[measurement.creator_tier].append(measurement)
        self.measurements_by_region[measurement.geographic_region].append(measurement)
        self.measurements_by_type[measurement.request_type].append(measurement)
        
        # Check for immediate SLA violation
        sla_threshold = self.sla_thresholds.get(measurement.creator_tier, {}).get(measurement.request_type)
        if sla_threshold and measurement.total_latency_us > sla_threshold:
            await self._record_sla_violation(measurement, sla_threshold)
        
        # Invalidate relevant percentile caches
        self._invalidate_percentile_cache(measurement)
        
        self.logger.debug(
            f"Recorded latency: {measurement.total_latency_us/1000:.1f}ms "
            f"({measurement.creator_tier.value}, {measurement.request_type.value})"
        )
    
    async def _record_sla_violation(self, measurement: LatencyMeasurement, sla_threshold: int):
        """Enregistrement violation SLA"""
        severity = self._calculate_violation_severity(measurement.total_latency_us, sla_threshold)
        
        violation = SLAViolation(
            violation_id=str(uuid.uuid4()),
            creator_tier=measurement.creator_tier,
            request_type=measurement.request_type,
            sla_threshold_us=sla_threshold,
            actual_latency_us=measurement.total_latency_us,
            violation_severity=severity,
            impact_description=f"Latency {measurement.total_latency_us/1000:.1f}ms exceeded SLA {sla_threshold/1000:.1f}ms",
            recommended_actions=self._generate_sla_remediation_actions(measurement, severity)
        )
        
        self.sla_violations.append(violation)
        
        if severity in ['major', 'critical']:
            self.logger.warning(
                f"🚨 SLA Violation ({severity}): {measurement.creator_tier.value} "
                f"{measurement.request_type.value} - {measurement.total_latency_us/1000:.1f}ms "
                f"(SLA: {sla_threshold/1000:.1f}ms)"
            )
    
    def _calculate_violation_severity(self, actual_latency: int, sla_threshold: int) -> str:
        """Calcul sévérité violation SLA"""
        ratio = actual_latency / sla_threshold
        
        if ratio >= 5.0:
            return "critical"
        elif ratio >= 2.0:
            return "major"
        else:
            return "minor"
    
    def _generate_sla_remediation_actions(
        self, 
        measurement: LatencyMeasurement, 
        severity: str
    ) -> List[str]:
        """Génération actions correctives SLA"""
        actions = []
        
        # Analyze component breakdown to identify bottlenecks
        max_component = max(measurement.component_latencies.items(), key=lambda x: x[1])
        bottleneck_component, bottleneck_latency = max_component
        
        if bottleneck_component == LatencyComponent.DATABASE:
            actions.extend([
                "Optimize database queries",
                "Add database indexes",
                "Scale database read replicas",
                "Enable query caching"
            ])
        elif bottleneck_component == LatencyComponent.ML_INFERENCE:
            actions.extend([
                "Optimize model inference",
                "Use model quantization",
                "Scale inference servers",
                "Implement model caching"
            ])
        elif bottleneck_component == LatencyComponent.FILE_STORAGE:
            actions.extend([
                "Use CDN for file delivery",
                "Optimize file compression",
                "Scale storage bandwidth",
                "Implement async processing"
            ])
        
        # Add severity-specific actions
        if severity == "critical":
            actions.insert(0, "Immediate incident response required")
            actions.append("Consider emergency resource scaling")
        
        return actions[:5]  # Return top 5 actions
    
    def _invalidate_percentile_cache(self, measurement: LatencyMeasurement):
        """Invalidation cache percentiles"""
        # Invalidate caches that could be affected by this measurement
        cache_keys_to_invalidate = [
            f"overall",
            f"tier_{measurement.creator_tier.value}",
            f"region_{measurement.geographic_region.value}",
            f"type_{measurement.request_type.value}",
            f"tier_{measurement.creator_tier.value}_type_{measurement.request_type.value}"
        ]
        
        for key in cache_keys_to_invalidate:
            if key in self.percentile_cache:
                del self.percentile_cache[key]
    
    def _update_percentile_cache(self):
        """Mise à jour cache percentiles"""
        current_time = time.time()
        
        # Clean expired cache entries
        expired_keys = []
        for key, percentiles in self.percentile_cache.items():
            if hasattr(percentiles, '_cache_timestamp'):
                if current_time - percentiles._cache_timestamp > self.percentile_cache_ttl:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self.percentile_cache[key]
    
    def _check_sla_violations(self):
        """Vérification violations SLA récentes"""
        # Check recent measurements for patterns
        recent_time = datetime.utcnow() - timedelta(minutes=5)
        recent_violations = [
            v for v in self.sla_violations 
            if v.timestamp > recent_time
        ]
        
        if len(recent_violations) > 10:  # More than 10 violations in 5 minutes
            self.logger.warning(
                f"🚨 High SLA violation rate: {len(recent_violations)} violations in 5 minutes"
            )
    
    def _detect_latency_anomalies(self):
        """Détection anomalies latence"""
        try:
            # Check overall latency trends
            recent_measurements = list(self.latency_measurements)[-100:]  # Last 100 measurements
            if len(recent_measurements) < 50:
                return
            
            recent_latencies = [m.total_latency_us for m in recent_measurements]
            mean_latency = statistics.mean(recent_latencies)
            std_dev = statistics.stdev(recent_latencies) if len(recent_latencies) > 1 else 0
            
            # Historical baseline (measurements older than 1 hour)
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            historical_measurements = [
                m for m in list(self.latency_measurements)[-1000:] 
                if m.timestamp < cutoff_time
            ]
            
            if len(historical_measurements) < 50:
                return
            
            historical_latencies = [m.total_latency_us for m in historical_measurements]
            historical_mean = statistics.mean(historical_latencies)
            historical_std = statistics.stdev(historical_latencies) if len(historical_latencies) > 1 else 0
            
            # Detect significant deviation
            if mean_latency > historical_mean + (self.anomaly_threshold_multiplier * historical_std):
                self.logger.warning(
                    f"🔍 Latency anomaly detected: Current mean {mean_latency/1000:.1f}ms "
                    f"vs historical {historical_mean/1000:.1f}ms "
                    f"(+{((mean_latency - historical_mean) / historical_mean * 100):.1f}%)"
                )
                
        except Exception as e:
            self.logger.error(f"Error in anomaly detection: {str(e)}")
    
    def _update_business_correlations(self):
        """Mise à jour corrélations business impact"""
        try:
            # Analyze correlation between latency and conversion rates
            recent_measurements = list(self.latency_measurements)[-1000:]  # Last 1000 measurements
            
            if len(recent_measurements) < 100:
                return
            
            # Group by latency buckets
            latency_buckets = {
                'fast': [],      # < 500ms
                'medium': [],    # 500ms - 2s
                'slow': [],      # 2s - 5s
                'very_slow': []  # > 5s
            }
            
            for measurement in recent_measurements:
                latency_ms = measurement.total_latency_us / 1000
                
                if latency_ms < 500:
                    bucket = 'fast'
                elif latency_ms < 2000:
                    bucket = 'medium'
                elif latency_ms < 5000:
                    bucket = 'slow'
                else:
                    bucket = 'very_slow'
                
                latency_buckets[bucket].append(measurement)
            
            # Calculate conversion rates by bucket
            conversion_rates = {}
            for bucket, measurements in latency_buckets.items():
                if measurements:
                    conversions = sum(1 for m in measurements if m.conversion_event)
                    conversion_rate = conversions / len(measurements)
                    conversion_rates[bucket] = conversion_rate
            
            self.latency_conversion_correlation = conversion_rates
            
            # Log significant correlations
            if 'fast' in conversion_rates and 'slow' in conversion_rates:
                fast_rate = conversion_rates['fast']
                slow_rate = conversion_rates['slow']
                
                if fast_rate > slow_rate * 1.5:  # 50% better conversion for fast requests
                    self.logger.info(
                        f"📊 Latency-conversion correlation: Fast requests ({fast_rate:.1%}) "
                        f"vs slow requests ({slow_rate:.1%}) conversion rate"
                    )
                    
        except Exception as e:
            self.logger.error(f"Error updating business correlations: {str(e)}")
    
    def _cleanup_old_measurements(self):
        """Nettoyage mesures anciennes"""
        # Already handled by deque maxlen, but could add time-based cleanup here
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Count old measurements for logging
        old_count = sum(
            1 for m in list(self.latency_measurements)[-1000:] 
            if m.timestamp < cutoff_time
        )
        
        if old_count > 500:
            self.logger.debug(f"🧹 Old measurements detected: {old_count} older than 24h")
    
    async def calculate_percentiles(
        self, 
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> LatencyPercentiles:
        """Calcul percentiles latence avec filtrage optionnel"""
        
        # Generate cache key
        cache_key = "overall"
        if filter_criteria:
            key_parts = []
            for k, v in sorted(filter_criteria.items()):
                key_parts.append(f"{k}_{v}")
            cache_key = "_".join(key_parts)
        
        # Check cache
        if cache_key in self.percentile_cache:
            cached = self.percentile_cache[cache_key]
            if hasattr(cached, '_cache_timestamp'):
                if time.time() - cached._cache_timestamp < self.percentile_cache_ttl:
                    return cached
        
        # Get measurements based on filter criteria
        measurements = self._filter_measurements(filter_criteria)
        
        if not measurements:
            return LatencyPercentiles(
                p50_us=0, p90_us=0, p95_us=0, p99_us=0, p99_9_us=0,
                max_us=0, min_us=0, mean_us=0.0, std_dev_us=0.0,
                sample_count=0
            )
        
        # Extract latencies and sort
        latencies = sorted([m.total_latency_us for m in measurements])
        n = len(latencies)
        
        # Calculate percentiles
        percentiles = LatencyPercentiles(
            p50_us=latencies[int(n * 0.5)],
            p90_us=latencies[int(n * 0.9)],
            p95_us=latencies[int(n * 0.95)],
            p99_us=latencies[int(n * 0.99)],
            p99_9_us=latencies[int(n * 0.999)] if n >= 1000 else latencies[-1],
            max_us=latencies[-1],
            min_us=latencies[0],
            mean_us=statistics.mean(latencies),
            std_dev_us=statistics.stdev(latencies) if n > 1 else 0.0,
            sample_count=n
        )
        
        # Cache result
        percentiles._cache_timestamp = time.time()
        self.percentile_cache[cache_key] = percentiles
        
        return percentiles
    
    def _filter_measurements(self, filter_criteria: Optional[Dict[str, Any]]) -> List[LatencyMeasurement]:
        """Filtrage mesures selon critères"""
        if not filter_criteria:
            return list(self.latency_measurements)
        
        measurements = list(self.latency_measurements)
        
        # Apply filters
        if 'creator_tier' in filter_criteria:
            tier = CreatorTier(filter_criteria['creator_tier'])
            measurements = [m for m in measurements if m.creator_tier == tier]
        
        if 'request_type' in filter_criteria:
            req_type = RequestType(filter_criteria['request_type'])
            measurements = [m for m in measurements if m.request_type == req_type]
        
        if 'geographic_region' in filter_criteria:
            region = GeographicRegion(filter_criteria['geographic_region'])
            measurements = [m for m in measurements if m.geographic_region == region]
        
        if 'time_range_hours' in filter_criteria:
            hours = filter_criteria['time_range_hours']
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            measurements = [m for m in measurements if m.timestamp > cutoff_time]
        
        if 'min_latency_ms' in filter_criteria:
            min_latency_us = filter_criteria['min_latency_ms'] * 1000
            measurements = [m for m in measurements if m.total_latency_us >= min_latency_us]
        
        if 'max_latency_ms' in filter_criteria:
            max_latency_us = filter_criteria['max_latency_ms'] * 1000
            measurements = [m for m in measurements if m.total_latency_us <= max_latency_us]
        
        return measurements
    
    async def get_latency_breakdown_analysis(
        self,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyse breakdown latence par composant"""
        measurements = self._filter_measurements(filter_criteria)
        
        if not measurements:
            return {'error': 'No measurements found for criteria'}
        
        # Aggregate component latencies
        component_stats = defaultdict(list)
        
        for measurement in measurements:
            for component, latency in measurement.component_latencies.items():
                component_stats[component].append(latency)
        
        # Calculate statistics for each component
        breakdown_analysis = {}
        total_measurements = len(measurements)
        
        for component, latencies in component_stats.items():
            if latencies:
                breakdown_analysis[component.value] = {
                    'mean_us': statistics.mean(latencies),
                    'median_us': statistics.median(latencies),
                    'p95_us': sorted(latencies)[int(len(latencies) * 0.95)],
                    'max_us': max(latencies),
                    'std_dev_us': statistics.stdev(latencies) if len(latencies) > 1 else 0.0,
                    'sample_count': len(latencies),
                    'percentage_of_requests': (len(latencies) / total_measurements) * 100
                }
        
        # Identify top bottlenecks
        bottlenecks = []
        for component, stats in breakdown_analysis.items():
            if stats['mean_us'] > 100_000:  # Components with >100ms average
                bottlenecks.append({
                    'component': component,
                    'mean_latency_ms': stats['mean_us'] / 1000,
                    'impact_score': stats['mean_us'] * stats['percentage_of_requests'] / 100
                })
        
        bottlenecks.sort(key=lambda x: x['impact_score'], reverse=True)
        
        return {
            'component_breakdown': breakdown_analysis,
            'top_bottlenecks': bottlenecks[:5],
            'total_measurements_analyzed': total_measurements,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_sla_compliance_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Rapport conformité SLA"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Get recent measurements
        recent_measurements = [
            m for m in list(self.latency_measurements) 
            if m.timestamp > cutoff_time
        ]
        
        if not recent_measurements:
            return {'error': 'No measurements in specified time window'}
        
        # Calculate compliance by tier and request type
        compliance_by_tier = {}
        
        for tier in CreatorTier:
            tier_measurements = [m for m in recent_measurements if m.creator_tier == tier]
            if not tier_measurements:
                continue
            
            tier_compliance = {}
            tier_thresholds = self.sla_thresholds.get(tier, {})
            
            for req_type in RequestType:
                type_measurements = [m for m in tier_measurements if m.request_type == req_type]
                if not type_measurements:
                    continue
                
                sla_threshold = tier_thresholds.get(req_type)
                if not sla_threshold:
                    continue
                
                # Calculate compliance
                compliant_requests = sum(
                    1 for m in type_measurements 
                    if m.total_latency_us <= sla_threshold
                )
                total_requests = len(type_measurements)
                compliance_percentage = (compliant_requests / total_requests) * 100
                
                # Calculate percentiles for this segment
                latencies = [m.total_latency_us for m in type_measurements]
                latencies.sort()
                
                tier_compliance[req_type.value] = {
                    'sla_threshold_ms': sla_threshold / 1000,
                    'compliance_percentage': round(compliance_percentage, 2),
                    'total_requests': total_requests,
                    'violations': total_requests - compliant_requests,
                    'p50_ms': round(latencies[int(len(latencies) * 0.5)] / 1000, 2),
                    'p95_ms': round(latencies[int(len(latencies) * 0.95)] / 1000, 2),
                    'p99_ms': round(latencies[int(len(latencies) * 0.99)] / 1000, 2)
                }
            
            compliance_by_tier[tier.value] = tier_compliance
        
        # Overall compliance
        total_requests = len(recent_measurements)
        total_violations = sum(
            1 for m in recent_measurements
            if m.total_latency_us > self.sla_thresholds.get(m.creator_tier, {}).get(m.request_type, float('inf'))
        )
        overall_compliance = ((total_requests - total_violations) / total_requests) * 100 if total_requests > 0 else 0
        
        # Recent violations summary
        recent_violations = [
            v for v in list(self.sla_violations) 
            if v.timestamp > cutoff_time
        ]
        
        violations_by_severity = defaultdict(int)
        for violation in recent_violations:
            violations_by_severity[violation.violation_severity] += 1
        
        return {
            'time_window_hours': time_window_hours,
            'overall_compliance_percentage': round(overall_compliance, 2),
            'total_requests_analyzed': total_requests,
            'total_violations': total_violations,
            'compliance_by_tier': compliance_by_tier,
            'violations_by_severity': dict(violations_by_severity),
            'recent_violations_count': len(recent_violations),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_geographic_latency_analysis(self) -> Dict[str, Any]:
        """Analyse latence par région géographique"""
        regional_analysis = {}
        
        for region in GeographicRegion:
            region_measurements = list(self.measurements_by_region[region])
            if not region_measurements:
                continue
            
            # Calculate percentiles for this region
            latencies = [m.total_latency_us for m in region_measurements]
            latencies.sort()
            n = len(latencies)
            
            if n == 0:
                continue
            
            # CDN and cache hit rates
            cdn_hits = sum(1 for m in region_measurements if m.cdn_hit)
            cache_hits = sum(1 for m in region_measurements if m.cache_hit)
            
            regional_analysis[region.value] = {
                'sample_count': n,
                'latency_percentiles': {
                    'p50_ms': round(latencies[int(n * 0.5)] / 1000, 2),
                    'p95_ms': round(latencies[int(n * 0.95)] / 1000, 2),
                    'p99_ms': round(latencies[int(n * 0.99)] / 1000, 2),
                    'mean_ms': round(statistics.mean(latencies) / 1000, 2)
                },
                'cache_performance': {
                    'cdn_hit_rate': round((cdn_hits / n) * 100, 1),
                    'cache_hit_rate': round((cache_hits / n) * 100, 1)
                },
                'optimization_opportunities': self._identify_regional_optimizations(region, region_measurements)
            }
        
        # Identify best and worst performing regions
        if regional_analysis:
            sorted_regions = sorted(
                regional_analysis.items(),
                key=lambda x: x[1]['latency_percentiles']['p95_ms']
            )
            
            best_region = sorted_regions[0] if sorted_regions else None
            worst_region = sorted_regions[-1] if sorted_regions else None
            
            return {
                'regional_breakdown': regional_analysis,
                'best_performing_region': {
                    'region': best_region[0],
                    'p95_latency_ms': best_region[1]['latency_percentiles']['p95_ms']
                } if best_region else None,
                'worst_performing_region': {
                    'region': worst_region[0],
                    'p95_latency_ms': worst_region[1]['latency_percentiles']['p95_ms']
                } if worst_region else None,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
        
        return {'error': 'No regional data available'}
    
    def _identify_regional_optimizations(
        self, 
        region: GeographicRegion, 
        measurements: List[LatencyMeasurement]
    ) -> List[str]:
        """Identification optimisations par région"""
        optimizations = []
        
        if not measurements:
            return optimizations
        
        # Analyze CDN performance
        cdn_hits = sum(1 for m in measurements if m.cdn_hit)
        cdn_hit_rate = cdn_hits / len(measurements)
        
        if cdn_hit_rate < 0.8:  # Less than 80% CDN hit rate
            optimizations.append(f"Improve CDN coverage in {region.value}")
        
        # Analyze cache performance
        cache_hits = sum(1 for m in measurements if m.cache_hit)
        cache_hit_rate = cache_hits / len(measurements)
        
        if cache_hit_rate < 0.7:  # Less than 70% cache hit rate
            optimizations.append(f"Optimize caching strategy for {region.value}")
        
        # Analyze latency patterns
        latencies = [m.total_latency_us for m in measurements]
        avg_latency = statistics.mean(latencies)
        
        if avg_latency > 2_000_000:  # > 2 seconds average
            optimizations.append(f"Deploy edge servers in {region.value}")
        
        return optimizations[:3]  # Return top 3 optimizations
    
    async def get_business_impact_analysis(self) -> Dict[str, Any]:
        """Analyse impact business de la latence"""
        # Calculate conversion rates by latency buckets
        conversion_analysis = {
            'latency_conversion_correlation': self.latency_conversion_correlation,
            'business_impact_insights': []
        }
        
        if self.latency_conversion_correlation:
            # Calculate potential revenue impact
            conversion_rates = self.latency_conversion_correlation
            
            if 'fast' in conversion_rates and 'slow' in conversion_rates:
                fast_rate = conversion_rates['fast']
                slow_rate = conversion_rates['slow']
                improvement_potential = fast_rate - slow_rate
                
                if improvement_potential > 0:
                    conversion_analysis['business_impact_insights'].append({
                        'insight': 'Latency optimization opportunity',
                        'description': f'Fast requests convert {improvement_potential:.1%} better than slow requests',
                        'recommendation': 'Focus on reducing tail latency to improve conversion rates'
                    })
        
        # Analyze creator tier satisfaction correlation
        tier_satisfaction = {}
        for tier in CreatorTier:
            tier_measurements = list(self.measurements_by_tier[tier])
            if tier_measurements:
                satisfactions = [m.satisfaction_score for m in tier_measurements if m.satisfaction_score is not None]
                if satisfactions:
                    tier_satisfaction[tier.value] = {
                        'avg_satisfaction': round(statistics.mean(satisfactions), 2),
                        'sample_count': len(satisfactions)
                    }
        
        conversion_analysis['creator_satisfaction_by_tier'] = tier_satisfaction
        
        return conversion_analysis
    
    async def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Dashboard complet distribution latence"""
        # Overall percentiles
        overall_percentiles = await self.calculate_percentiles()
        
        # SLA compliance
        sla_report = await self.get_sla_compliance_report(24)
        
        # Geographic analysis
        geo_analysis = await self.get_geographic_latency_analysis()
        
        # Component breakdown
        breakdown_analysis = await self.get_latency_breakdown_analysis()
        
        # Business impact
        business_impact = await self.get_business_impact_analysis()
        
        # Recent trends
        recent_measurements = list(self.latency_measurements)[-1000:]
        total_measurements = len(self.latency_measurements)
        
        return {
            'overview': {
                'total_measurements': total_measurements,
                'recent_measurements_1000': len(recent_measurements),
                'overall_percentiles_ms': {
                    'p50': round(overall_percentiles.p50_us / 1000, 2),
                    'p95': round(overall_percentiles.p95_us / 1000, 2),
                    'p99': round(overall_percentiles.p99_us / 1000, 2),
                    'p99_9': round(overall_percentiles.p99_9_us / 1000, 2)
                },
                'sample_count': overall_percentiles.sample_count
            },
            'sla_compliance': sla_report,
            'geographic_analysis': geo_analysis,
            'component_breakdown': breakdown_analysis,
            'business_impact': business_impact,
            'system_health': {
                'monitoring_active': self.monitoring_active,
                'cache_entries': len(self.percentile_cache),
                'recent_violations': len([v for v in self.sla_violations if v.timestamp > datetime.utcnow() - timedelta(hours=1)]),
                'last_update': datetime.utcnow().isoformat()
            }
        }
    
    async def shutdown(self):
        """Arrêt propre analyseur latence"""
        self.logger.info("⏹️ Shutting down Latency Distribution Analyzer...")
        
        # Stop monitoring
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        # Clear data structures
        self.latency_measurements.clear()
        for tier_deque in self.measurements_by_tier.values():
            tier_deque.clear()
        for region_deque in self.measurements_by_region.values():
            region_deque.clear()
        for type_deque in self.measurements_by_type.values():
            type_deque.clear()
        
        self.percentile_cache.clear()
        self.sla_violations.clear()
        
        self.logger.info("✅ Latency Distribution Analyzer shutdown complete")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_latency_analyzer():
        config = {
            'monitoring_interval': 0.5,  # Fast for testing
            'percentile_cache_ttl': 10,
            'anomaly_threshold': 2.0
        }
        
        analyzer = LatencyDistributionAnalyzer(config)
        await analyzer.initialize()
        
        # Test additional measurements
        import random
        for i in range(50):
            measurement = LatencyMeasurement(
                request_id=str(uuid.uuid4()),
                creator_id=f"test_creator_{i}",
                creator_tier=random.choice(list(CreatorTier)),
                request_type=random.choice(list(RequestType)),
                geographic_region=random.choice(list(GeographicRegion)),
                total_latency_us=random.randint(50_000, 3_000_000),  # 50ms to 3s
                component_latencies={
                    LatencyComponent.API_GATEWAY: random.randint(10_000, 50_000),
                    LatencyComponent.DATABASE: random.randint(100_000, 500_000),
                    LatencyComponent.PROCESSING: random.randint(50_000, 200_000)
                },
                request_size_bytes=random.randint(1024, 100_000),
                response_size_bytes=random.randint(512, 50_000),
                cache_hit=random.random() < 0.7,
                cdn_hit=random.random() < 0.8,
                client_ip=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                user_agent="Test Client",
                connection_type="test",
                conversion_event=random.random() < 0.1
            )
            
            await analyzer.record_latency_measurement(measurement)
        
        # Test percentile calculation
        percentiles = await analyzer.calculate_percentiles()
        print(f"✅ Overall P95: {percentiles.p95_us / 1000:.1f}ms")
        
        # Test filtered percentiles
        pro_percentiles = await analyzer.calculate_percentiles({
            'creator_tier': 'pro'
        })
        print(f"✅ Pro tier P95: {pro_percentiles.p95_us / 1000:.1f}ms")
        
        # Test SLA compliance
        sla_report = await analyzer.get_sla_compliance_report(1)
        print(f"✅ Overall SLA compliance: {sla_report['overall_compliance_percentage']}%")
        
        # Test component breakdown
        breakdown = await analyzer.get_latency_breakdown_analysis()
        print(f"✅ Component analysis: {len(breakdown['component_breakdown'])} components")
        
        # Test dashboard
        dashboard = await analyzer.get_comprehensive_dashboard()
        print(f"✅ Dashboard: {dashboard['overview']['total_measurements']} total measurements")
        
        print("✅ Latency Distribution Analyzer test completed")
        await analyzer.shutdown()
    
    asyncio.run(test_latency_analyzer())