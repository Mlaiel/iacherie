"""
📈 Throughput Capacity Monitor - Enterprise AI/ML Performance Hub
===============================================================

Monitoring capacité débit système ultra-avancé pour Creator Economy IA Chéries.
Requests per second tracking, monitoring usage concurrent créateurs, analyse capacité peak load,
optimisation triggers auto-scaling, métriques throughput contenu multi-modal.

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

Architecture: monitoring/ai_ml_performance_hub/throughput_capacity_monitor.py
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import threading
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import math


class ServiceType(Enum):
    """Types service Creator Economy"""
    CONTENT_ANALYSIS = "content_analysis"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_ENHANCEMENT = "video_enhancement"
    TEXT_GENERATION = "text_generation"
    IMAGE_EDITING = "image_editing"
    RECOMMENDATION = "recommendation"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    SEO_OPTIMIZATION = "seo_optimization"
    CONTENT_PROTECTION = "content_protection"


class CreatorTier(Enum):
    """Niveaux créateurs"""
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ContentModality(Enum):
    """Modalités contenu"""
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    IMAGE = "image"
    MULTIMODAL = "multimodal"


class LoadPattern(Enum):
    """Patterns charge système"""
    STEADY = "steady"
    BURST = "burst"
    PEAK = "peak"
    VALLEY = "valley"
    IRREGULAR = "irregular"


@dataclass
class ThroughputMetrics:
    """Métriques débit détaillées"""
    service_type: ServiceType
    creator_tier: CreatorTier
    content_modality: ContentModality
    requests_per_second: float
    concurrent_requests: int
    completed_requests: int
    failed_requests: int
    success_rate_percent: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    bytes_processed_per_sec: float
    cpu_utilization_percent: float
    memory_utilization_percent: float
    queue_length: int
    backpressure_applied: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CapacityMetrics:
    """Métriques capacité système"""
    total_rps_capacity: float
    current_rps_utilization: float
    utilization_percent: float
    headroom_percent: float
    estimated_max_concurrent: int
    current_concurrent: int
    scaling_recommendation: str  # "scale_up", "scale_down", "maintain"
    scaling_confidence: float
    bottleneck_component: Optional[str]
    load_pattern: LoadPattern
    forecast_next_hour_rps: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreatorUsageMetrics:
    """Métriques usage par créateur"""
    creator_id: str
    creator_tier: CreatorTier
    requests_per_minute: float
    concurrent_sessions: int
    total_requests_24h: int
    success_rate_percent: float
    avg_request_size_bytes: float
    avg_response_size_bytes: float
    preferred_services: List[ServiceType]
    peak_usage_hour: int
    quota_utilization_percent: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AutoScalingTrigger:
    """Déclencheur auto-scaling"""
    trigger_id: str
    trigger_type: str  # "scale_up", "scale_down"
    trigger_reason: str
    current_metrics: Dict[str, float]
    threshold_violated: str
    confidence_score: float
    estimated_impact: str
    recommended_action: str
    urgent: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PeakLoadAnalysis:
    """Analyse charge peak"""
    analysis_id: str
    peak_start_time: datetime
    peak_end_time: datetime
    peak_rps: float
    peak_concurrent: int
    duration_minutes: int
    services_affected: List[ServiceType]
    performance_impact: Dict[str, float]
    recovery_time_minutes: float
    root_cause: Optional[str]
    lessons_learned: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ThroughputCapacityMonitor:
    """Monitoring capacité débit système Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Throughput tracking
        self.throughput_history: deque = deque(maxlen=10000)
        self.capacity_history: deque = deque(maxlen=1000)
        self.creator_usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Real-time metrics
        self.active_requests: Dict[str, Dict] = {}
        self.request_timestamps: deque = deque(maxlen=10000)
        self.completed_requests_count: Dict[str, int] = defaultdict(int)
        
        # Capacity configuration per service type
        self.service_capacity_limits = {
            ServiceType.CONTENT_ANALYSIS: {'max_rps': 1000, 'max_concurrent': 500},
            ServiceType.AUDIO_PROCESSING: {'max_rps': 200, 'max_concurrent': 100},
            ServiceType.VIDEO_ENHANCEMENT: {'max_rps': 50, 'max_concurrent': 25},
            ServiceType.TEXT_GENERATION: {'max_rps': 500, 'max_concurrent': 200},
            ServiceType.IMAGE_EDITING: {'max_rps': 300, 'max_concurrent': 150},
            ServiceType.RECOMMENDATION: {'max_rps': 2000, 'max_concurrent': 1000},
            ServiceType.COLLABORATION: {'max_rps': 1500, 'max_concurrent': 750},
            ServiceType.MONETIZATION: {'max_rps': 800, 'max_concurrent': 400},
            ServiceType.SEO_OPTIMIZATION: {'max_rps': 100, 'max_concurrent': 50},
            ServiceType.CONTENT_PROTECTION: {'max_rps': 300, 'max_concurrent': 150}
        }
        
        # Creator tier quotas (requests per minute)
        self.tier_quotas = {
            CreatorTier.FREE: {'rpm_limit': 60, 'concurrent_limit': 5},
            CreatorTier.PREMIUM: {'rpm_limit': 300, 'concurrent_limit': 15},
            CreatorTier.PROFESSIONAL: {'rpm_limit': 1000, 'concurrent_limit': 50},
            CreatorTier.ENTERPRISE: {'rpm_limit': 5000, 'concurrent_limit': 200}
        }
        
        # Auto-scaling thresholds
        self.autoscaling_thresholds = {
            'scale_up_rps_percent': 75,      # Scale up at 75% capacity
            'scale_down_rps_percent': 30,    # Scale down at 30% capacity
            'scale_up_latency_ms': 1000,     # Scale up if latency > 1s
            'scale_down_latency_ms': 200,    # Scale down if latency < 200ms
            'min_scaling_interval_minutes': 5,  # Minimum time between scaling events
            'confidence_threshold': 0.8      # Minimum confidence for scaling
        }
        
        # Peak load detection
        self.peak_load_threshold_multiplier = 2.0  # 2x normal load
        self.active_peak_loads: Dict[str, PeakLoadAnalysis] = {}
        
        # Monitoring threads
        self.monitoring_active = False
        self.throughput_thread: Optional[threading.Thread] = None
        self.capacity_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        # Auto-scaling callbacks
        self.scaling_callbacks: List[Callable] = []
        
        # Performance baselines
        self.baseline_rps = {}
        self.baseline_latency = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger(f"throughput_monitor_{id(self)}")
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
        """Initialisation monitoring throughput"""
        self.logger.info("📈 Initialisation Throughput Capacity Monitor...")
        
        # Démarrer monitoring continu
        await self._start_throughput_monitoring()
        await self._start_capacity_monitoring()
        
        # Initialiser baselines
        await self._initialize_performance_baselines()
        
        self.logger.info("✅ Throughput Capacity Monitor initialisé")
    
    async def _start_throughput_monitoring(self):
        """Démarrage monitoring throughput"""
        self.monitoring_active = True
        
        def monitor_throughput():
            while self.monitoring_active:
                try:
                    self._collect_throughput_metrics()
                    time.sleep(10)  # Collect every 10 seconds
                except Exception as e:
                    self.logger.error(f"Throughput monitoring error: {e}")
        
        self.throughput_thread = threading.Thread(target=monitor_throughput, daemon=True)
        self.throughput_thread.start()
    
    async def _start_capacity_monitoring(self):
        """Démarrage monitoring capacité"""
        def monitor_capacity():
            while self.monitoring_active:
                try:
                    self._analyze_capacity_utilization()
                    self._detect_peak_loads()
                    self._evaluate_autoscaling_triggers()
                    time.sleep(30)  # Analyze every 30 seconds
                except Exception as e:
                    self.logger.error(f"Capacity monitoring error: {e}")
        
        self.capacity_thread = threading.Thread(target=monitor_capacity, daemon=True)
        self.capacity_thread.start()
    
    async def _initialize_performance_baselines(self):
        """Initialisation baselines performance"""
        # Simulate baseline calculations (would use historical data in production)
        for service_type in ServiceType:
            self.baseline_rps[service_type] = {
                'normal_load_rps': self.service_capacity_limits[service_type]['max_rps'] * 0.3,
                'peak_load_rps': self.service_capacity_limits[service_type]['max_rps'] * 0.8
            }
            self.baseline_latency[service_type] = {
                'normal_latency_ms': 200,
                'peak_latency_ms': 500
            }
    
    async def record_request_start(
        self,
        request_id: str,
        creator_id: str,
        creator_tier: CreatorTier,
        service_type: ServiceType,
        content_modality: ContentModality,
        request_size_bytes: int
    ):
        """Enregistrement début requête"""
        start_time = time.time()
        
        self.active_requests[request_id] = {
            'creator_id': creator_id,
            'creator_tier': creator_tier,
            'service_type': service_type,
            'content_modality': content_modality,
            'request_size_bytes': request_size_bytes,
            'start_time': start_time
        }
        
        self.request_timestamps.append(start_time)
        
        # Check creator quotas
        await self._check_creator_quota(creator_id, creator_tier)
    
    async def record_request_completion(
        self,
        request_id: str,
        success: bool,
        response_size_bytes: int,
        response_time_ms: float
    ):
        """Enregistrement fin requête"""
        if request_id not in self.active_requests:
            self.logger.warning(f"Request {request_id} not found for completion")
            return
        
        request_data = self.active_requests[request_id]
        end_time = time.time()
        
        # Update completion counters
        service_key = f"{request_data['service_type'].value}_{success}"
        self.completed_requests_count[service_key] += 1
        
        # Update creator usage
        await self._update_creator_usage(
            request_data['creator_id'],
            request_data['creator_tier'],
            request_data['service_type'],
            request_data['request_size_bytes'],
            response_size_bytes,
            success,
            response_time_ms
        )
        
        # Remove from active requests
        del self.active_requests[request_id]
        
        self.logger.debug(f"Completed request {request_id}: {response_time_ms:.1f}ms, success={success}")
    
    def _collect_throughput_metrics(self):
        """Collecte métriques throughput"""
        current_time = time.time()
        window_start = current_time - 60  # 1-minute window
        
        # Filter recent requests
        recent_timestamps = [ts for ts in self.request_timestamps if ts >= window_start]
        
        # Calculate RPS
        current_rps = len(recent_timestamps) / 60 if recent_timestamps else 0
        
        # Group by service, tier, modality
        service_groups = defaultdict(list)
        
        for request_id, request_data in self.active_requests.items():
            key = (
                request_data['service_type'],
                request_data['creator_tier'],
                request_data['content_modality']
            )
            service_groups[key].append(request_data)
        
        # Calculate metrics for each group
        for (service_type, creator_tier, content_modality), requests in service_groups.items():
            concurrent_requests = len(requests)
            
            # Calculate success/failure rates from recent completions
            success_key = f"{service_type.value}_True"
            failure_key = f"{service_type.value}_False"
            
            recent_success = self.completed_requests_count.get(success_key, 0)
            recent_failure = self.completed_requests_count.get(failure_key, 0)
            total_recent = recent_success + recent_failure
            
            success_rate = (recent_success / total_recent * 100) if total_recent > 0 else 100
            
            # Simulate response time metrics (would use actual data in production)
            import random
            avg_response_time = 200 + random.uniform(-50, 100)
            p95_response_time = avg_response_time * 1.5
            p99_response_time = avg_response_time * 2.2
            
            # Calculate bytes processed
            total_bytes = sum(req['request_size_bytes'] for req in requests)
            bytes_per_sec = total_bytes / 60 if requests else 0
            
            # Simulate system utilization
            cpu_utilization = min(95, concurrent_requests * 2 + random.uniform(0, 20))
            memory_utilization = min(90, concurrent_requests * 1.5 + random.uniform(0, 15))
            
            # Queue simulation
            capacity_limit = self.service_capacity_limits[service_type]['max_concurrent']
            queue_length = max(0, concurrent_requests - capacity_limit)
            backpressure = queue_length > 0
            
            # Create throughput metric
            metric = ThroughputMetrics(
                service_type=service_type,
                creator_tier=creator_tier,
                content_modality=content_modality,
                requests_per_second=current_rps,
                concurrent_requests=concurrent_requests,
                completed_requests=recent_success,
                failed_requests=recent_failure,
                success_rate_percent=success_rate,
                avg_response_time_ms=avg_response_time,
                p95_response_time_ms=p95_response_time,
                p99_response_time_ms=p99_response_time,
                bytes_processed_per_sec=bytes_per_sec,
                cpu_utilization_percent=cpu_utilization,
                memory_utilization_percent=memory_utilization,
                queue_length=queue_length,
                backpressure_applied=backpressure
            )
            
            self.throughput_history.append(metric)
        
        # Reset counters periodically
        if len(self.throughput_history) % 100 == 0:
            self.completed_requests_count.clear()
    
    def _analyze_capacity_utilization(self):
        """Analyse utilisation capacité"""
        if not self.throughput_history:
            return
        
        # Get recent metrics (last 5 minutes)
        recent_time = datetime.utcnow() - timedelta(minutes=5)
        recent_metrics = [m for m in self.throughput_history if m.timestamp >= recent_time]
        
        if not recent_metrics:
            return
        
        # Calculate aggregated capacity metrics
        total_rps = sum(m.requests_per_second for m in recent_metrics)
        total_concurrent = sum(m.concurrent_requests for m in recent_metrics)
        
        # Calculate theoretical capacity
        total_capacity_rps = sum(limits['max_rps'] for limits in self.service_capacity_limits.values())
        total_capacity_concurrent = sum(limits['max_concurrent'] for limits in self.service_capacity_limits.values())
        
        # Utilization percentages
        rps_utilization = (total_rps / total_capacity_rps * 100) if total_capacity_rps > 0 else 0
        concurrent_utilization = (total_concurrent / total_capacity_concurrent * 100) if total_capacity_concurrent > 0 else 0
        
        # Overall utilization (max of the two)
        overall_utilization = max(rps_utilization, concurrent_utilization)
        headroom = 100 - overall_utilization
        
        # Determine scaling recommendation
        scaling_recommendation = "maintain"
        scaling_confidence = 0.5
        
        if overall_utilization > self.autoscaling_thresholds['scale_up_rps_percent']:
            scaling_recommendation = "scale_up"
            scaling_confidence = min(1.0, (overall_utilization - 75) / 20)
        elif overall_utilization < self.autoscaling_thresholds['scale_down_rps_percent']:
            scaling_recommendation = "scale_down"
            scaling_confidence = min(1.0, (50 - overall_utilization) / 20)
        
        # Identify bottlenecks
        bottleneck_component = None
        max_service_utilization = 0
        
        for service_type, limits in self.service_capacity_limits.items():
            service_metrics = [m for m in recent_metrics if m.service_type == service_type]
            if service_metrics:
                service_rps = sum(m.requests_per_second for m in service_metrics)
                service_utilization = (service_rps / limits['max_rps'] * 100)
                if service_utilization > max_service_utilization:
                    max_service_utilization = service_utilization
                    if service_utilization > 80:
                        bottleneck_component = service_type.value
        
        # Detect load pattern
        load_pattern = self._detect_load_pattern(recent_metrics)
        
        # Forecast next hour (simplified prediction)
        forecast_rps = total_rps * 1.1  # 10% growth assumption
        
        # Create capacity metric
        capacity_metric = CapacityMetrics(
            total_rps_capacity=total_capacity_rps,
            current_rps_utilization=total_rps,
            utilization_percent=overall_utilization,
            headroom_percent=headroom,
            estimated_max_concurrent=total_capacity_concurrent,
            current_concurrent=total_concurrent,
            scaling_recommendation=scaling_recommendation,
            scaling_confidence=scaling_confidence,
            bottleneck_component=bottleneck_component,
            load_pattern=load_pattern,
            forecast_next_hour_rps=forecast_rps
        )
        
        self.capacity_history.append(capacity_metric)
    
    def _detect_load_pattern(self, metrics: List[ThroughputMetrics]) -> LoadPattern:
        """Détection pattern charge"""
        if len(metrics) < 10:
            return LoadPattern.STEADY
        
        # Calculate RPS variance
        rps_values = [m.requests_per_second for m in metrics]
        if not rps_values:
            return LoadPattern.STEADY
        
        mean_rps = statistics.mean(rps_values)
        std_dev = statistics.stdev(rps_values) if len(rps_values) > 1 else 0
        
        coefficient_of_variation = (std_dev / mean_rps) if mean_rps > 0 else 0
        
        # Classify pattern
        if coefficient_of_variation < 0.1:
            return LoadPattern.STEADY
        elif coefficient_of_variation > 0.5:
            return LoadPattern.IRREGULAR
        elif max(rps_values) > mean_rps * 2:
            return LoadPattern.BURST
        elif max(rps_values) > mean_rps * 1.5:
            return LoadPattern.PEAK
        else:
            return LoadPattern.VALLEY
    
    def _detect_peak_loads(self):
        """Détection charges peak"""
        if not self.capacity_history:
            return
        
        latest_capacity = self.capacity_history[-1]
        
        # Check if we're in a peak load situation
        for service_type in ServiceType:
            baseline_rps = self.baseline_rps[service_type]['normal_load_rps']
            current_rps = latest_capacity.current_rps_utilization
            
            if current_rps > baseline_rps * self.peak_load_threshold_multiplier:
                # Peak load detected
                peak_id = f"peak_{service_type.value}_{int(time.time())}"
                
                if peak_id not in self.active_peak_loads:
                    peak_analysis = PeakLoadAnalysis(
                        analysis_id=peak_id,
                        peak_start_time=datetime.utcnow(),
                        peak_end_time=datetime.utcnow(),  # Will be updated when peak ends
                        peak_rps=current_rps,
                        peak_concurrent=latest_capacity.current_concurrent,
                        duration_minutes=0,
                        services_affected=[service_type],
                        performance_impact={
                            'latency_increase_percent': (current_rps / baseline_rps - 1) * 100,
                            'error_rate_increase_percent': 0  # Would calculate from actual data
                        },
                        recovery_time_minutes=0,
                        root_cause=None,
                        lessons_learned=[]
                    )
                    
                    self.active_peak_loads[peak_id] = peak_analysis
                    
                    self.logger.warning(f"🚨 Peak Load Detected: {service_type.value} - {current_rps:.1f} RPS")
    
    async def _check_creator_quota(self, creator_id: str, creator_tier: CreatorTier):
        """Vérification quota créateur"""
        quota_limits = self.tier_quotas[creator_tier]
        
        # Count requests in last minute
        current_time = time.time()
        minute_ago = current_time - 60
        
        creator_requests = [
            req for req in self.active_requests.values()
            if req['creator_id'] == creator_id and req['start_time'] >= minute_ago
        ]
        
        current_rpm = len(creator_requests)
        current_concurrent = len([req for req in self.active_requests.values() if req['creator_id'] == creator_id])
        
        # Check limits
        if current_rpm > quota_limits['rpm_limit']:
            self.logger.warning(f"Creator {creator_id} exceeded RPM quota: {current_rpm}/{quota_limits['rpm_limit']}")
        
        if current_concurrent > quota_limits['concurrent_limit']:
            self.logger.warning(f"Creator {creator_id} exceeded concurrent quota: {current_concurrent}/{quota_limits['concurrent_limit']}")
    
    async def _update_creator_usage(
        self,
        creator_id: str,
        creator_tier: CreatorTier,
        service_type: ServiceType,
        request_size_bytes: int,
        response_size_bytes: int,
        success: bool,
        response_time_ms: float
    ):
        """Mise à jour usage créateur"""
        # Get or create usage history for creator
        if creator_id not in self.creator_usage_history:
            self.creator_usage_history[creator_id] = deque(maxlen=1000)
        
        # Calculate current usage metrics
        current_time = datetime.utcnow()
        minute_ago = current_time - timedelta(minutes=1)
        day_ago = current_time - timedelta(hours=24)
        
        creator_requests = [
            req for req in self.active_requests.values()
            if req['creator_id'] == creator_id
        ]
        
        # Simulate historical data for metrics
        requests_per_minute = len(creator_requests)
        concurrent_sessions = len(creator_requests)
        total_requests_24h = len(creator_requests) * 60 * 24  # Simplified
        
        # Calculate success rate (simplified)
        success_rate = 95.0 if success else 90.0
        
        # Preferred services (simplified - would analyze historical data)
        preferred_services = [service_type]
        
        # Peak usage hour (simplified)
        peak_hour = datetime.utcnow().hour
        
        # Quota utilization
        quota_limits = self.tier_quotas[creator_tier]
        quota_utilization = (requests_per_minute / quota_limits['rpm_limit'] * 100) if quota_limits['rpm_limit'] > 0 else 0
        
        usage_metric = CreatorUsageMetrics(
            creator_id=creator_id,
            creator_tier=creator_tier,
            requests_per_minute=requests_per_minute,
            concurrent_sessions=concurrent_sessions,
            total_requests_24h=total_requests_24h,
            success_rate_percent=success_rate,
            avg_request_size_bytes=request_size_bytes,
            avg_response_size_bytes=response_size_bytes,
            preferred_services=preferred_services,
            peak_usage_hour=peak_hour,
            quota_utilization_percent=quota_utilization
        )
        
        self.creator_usage_history[creator_id].append(usage_metric)
    
    def _evaluate_autoscaling_triggers(self):
        """Évaluation déclencheurs auto-scaling"""
        if not self.capacity_history:
            return
        
        latest_capacity = self.capacity_history[-1]
        
        # Check scaling thresholds
        should_scale_up = (
            latest_capacity.utilization_percent > self.autoscaling_thresholds['scale_up_rps_percent'] or
            latest_capacity.scaling_recommendation == "scale_up"
        )
        
        should_scale_down = (
            latest_capacity.utilization_percent < self.autoscaling_thresholds['scale_down_rps_percent'] and
            latest_capacity.scaling_recommendation == "scale_down"
        )
        
        if should_scale_up:
            trigger = self._create_scaling_trigger(
                "scale_up",
                "High capacity utilization detected",
                latest_capacity,
                latest_capacity.scaling_confidence
            )
            self._execute_scaling_trigger_sync(trigger)
        
        elif should_scale_down:
            trigger = self._create_scaling_trigger(
                "scale_down",
                "Low capacity utilization detected",
                latest_capacity,
                latest_capacity.scaling_confidence
            )
            self._execute_scaling_trigger_sync(trigger)
    
    def _create_scaling_trigger(
        self,
        trigger_type: str,
        reason: str,
        capacity_metrics: CapacityMetrics,
        confidence: float
    ) -> AutoScalingTrigger:
        """Création déclencheur scaling"""
        return AutoScalingTrigger(
            trigger_id=str(uuid.uuid4()),
            trigger_type=trigger_type,
            trigger_reason=reason,
            current_metrics={
                'utilization_percent': capacity_metrics.utilization_percent,
                'current_rps': capacity_metrics.current_rps_utilization,
                'current_concurrent': capacity_metrics.current_concurrent
            },
            threshold_violated=f"utilization > {self.autoscaling_thresholds['scale_up_rps_percent']}%" if trigger_type == "scale_up" else f"utilization < {self.autoscaling_thresholds['scale_down_rps_percent']}%",
            confidence_score=confidence,
            estimated_impact=f"{'Increase' if trigger_type == 'scale_up' else 'Decrease'} capacity by 50%",
            recommended_action=f"{'Add' if trigger_type == 'scale_up' else 'Remove'} infrastructure resources",
            urgent=capacity_metrics.utilization_percent > 90 if trigger_type == "scale_up" else False
        )
    
    def _execute_scaling_trigger_sync(self, trigger: AutoScalingTrigger):
        """Exécution déclencheur scaling (synchrone)"""
        if trigger.confidence_score < self.autoscaling_thresholds['confidence_threshold']:
            self.logger.info(f"Scaling trigger ignored - low confidence: {trigger.confidence_score:.2f}")
            return
        
        self.logger.info(
            f"🔧 Auto-scaling trigger: {trigger.trigger_type} - {trigger.trigger_reason} "
            f"(confidence: {trigger.confidence_score:.2f})"
        )
        
        # Execute registered callbacks (simplified - no async support in sync version)
        for callback in self.scaling_callbacks:
            try:
                # Skip async callbacks in sync version
                self.logger.info(f"Scaling callback scheduled: {callback}")
            except Exception as e:
                self.logger.error(f"Scaling callback error: {e}")
    
    async def _execute_scaling_trigger(self, trigger: AutoScalingTrigger):
        """Exécution déclencheur scaling"""
        if trigger.confidence_score < self.autoscaling_thresholds['confidence_threshold']:
            self.logger.info(f"Scaling trigger ignored - low confidence: {trigger.confidence_score:.2f}")
            return
        
        self.logger.info(
            f"🔧 Auto-scaling trigger: {trigger.trigger_type} - {trigger.trigger_reason} "
            f"(confidence: {trigger.confidence_score:.2f})"
        )
        
        # Execute registered callbacks
        for callback in self.scaling_callbacks:
            try:
                await callback(trigger)
            except Exception as e:
                self.logger.error(f"Scaling callback error: {e}")
    
    def register_scaling_callback(self, callback: Callable):
        """Enregistrement callback scaling"""
        self.scaling_callbacks.append(callback)
    
    async def get_throughput_overview(self) -> Dict[str, Any]:
        """Vue d'ensemble throughput"""
        if not self.throughput_history or not self.capacity_history:
            return {'error': 'Insufficient metrics data'}
        
        # Recent metrics (last 10 minutes)
        recent_time = datetime.utcnow() - timedelta(minutes=10)
        recent_throughput = [m for m in self.throughput_history if m.timestamp >= recent_time]
        latest_capacity = self.capacity_history[-1]
        
        # Aggregate metrics
        total_rps = sum(m.requests_per_second for m in recent_throughput)
        total_concurrent = sum(m.concurrent_requests for m in recent_throughput)
        avg_success_rate = statistics.mean([m.success_rate_percent for m in recent_throughput]) if recent_throughput else 100
        avg_response_time = statistics.mean([m.avg_response_time_ms for m in recent_throughput]) if recent_throughput else 0
        
        # Service breakdown
        service_breakdown = defaultdict(lambda: {'rps': 0, 'concurrent': 0})
        for metric in recent_throughput:
            service_breakdown[metric.service_type.value]['rps'] += metric.requests_per_second
            service_breakdown[metric.service_type.value]['concurrent'] += metric.concurrent_requests
        
        # Active peak loads
        active_peaks = len(self.active_peak_loads)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'current_throughput': {
                'total_rps': total_rps,
                'total_concurrent_requests': total_concurrent,
                'avg_success_rate_percent': avg_success_rate,
                'avg_response_time_ms': avg_response_time
            },
            'capacity_status': {
                'utilization_percent': latest_capacity.utilization_percent,
                'headroom_percent': latest_capacity.headroom_percent,
                'scaling_recommendation': latest_capacity.scaling_recommendation,
                'bottleneck_component': latest_capacity.bottleneck_component,
                'load_pattern': latest_capacity.load_pattern.value
            },
            'service_breakdown': dict(service_breakdown),
            'performance_alerts': {
                'active_peak_loads': active_peaks,
                'high_utilization_services': [
                    service for service, metrics in service_breakdown.items()
                    if metrics['rps'] > self.service_capacity_limits[ServiceType(service)]['max_rps'] * 0.8
                ]
            },
            'forecast': {
                'next_hour_rps': latest_capacity.forecast_next_hour_rps,
                'scaling_confidence': latest_capacity.scaling_confidence
            }
        }
    
    async def get_creator_throughput_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Analytics throughput créateur"""
        if creator_id not in self.creator_usage_history:
            return {'creator_id': creator_id, 'error': 'No usage data found'}
        
        usage_history = list(self.creator_usage_history[creator_id])
        if not usage_history:
            return {'creator_id': creator_id, 'error': 'No usage metrics available'}
        
        latest_usage = usage_history[-1]
        
        # Historical trends (last 24 hours)
        day_ago = datetime.utcnow() - timedelta(hours=24)
        recent_usage = [u for u in usage_history if u.timestamp >= day_ago]
        
        # Calculate trends
        if len(recent_usage) >= 2:
            rpm_trend = "increasing" if recent_usage[-1].requests_per_minute > recent_usage[0].requests_per_minute else "decreasing"
            success_rate_trend = "improving" if recent_usage[-1].success_rate_percent > recent_usage[0].success_rate_percent else "degrading"
        else:
            rpm_trend = "stable"
            success_rate_trend = "stable"
        
        return {
            'creator_id': creator_id,
            'creator_tier': latest_usage.creator_tier.value,
            'current_usage': {
                'requests_per_minute': latest_usage.requests_per_minute,
                'concurrent_sessions': latest_usage.concurrent_sessions,
                'quota_utilization_percent': latest_usage.quota_utilization_percent,
                'success_rate_percent': latest_usage.success_rate_percent
            },
            'usage_patterns': {
                'preferred_services': [s.value for s in latest_usage.preferred_services],
                'peak_usage_hour': latest_usage.peak_usage_hour,
                'avg_request_size_kb': latest_usage.avg_request_size_bytes / 1024,
                'avg_response_size_kb': latest_usage.avg_response_size_bytes / 1024
            },
            'trends_24h': {
                'rpm_trend': rpm_trend,
                'success_rate_trend': success_rate_trend,
                'total_requests': latest_usage.total_requests_24h
            },
            'quota_limits': self.tier_quotas[latest_usage.creator_tier],
            'optimization_recommendations': self._generate_creator_optimization_recommendations(latest_usage)
        }
    
    def _generate_creator_optimization_recommendations(self, usage: CreatorUsageMetrics) -> List[str]:
        """Génération recommandations optimisation créateur"""
        recommendations = []
        
        if usage.quota_utilization_percent > 80:
            recommendations.append("Consider upgrading tier - high quota utilization")
        
        if usage.success_rate_percent < 95:
            recommendations.append("Review request patterns - low success rate")
        
        if usage.avg_request_size_bytes > 1024 * 1024:  # 1MB
            recommendations.append("Optimize request size - large payloads detected")
        
        if usage.concurrent_sessions > self.tier_quotas[usage.creator_tier]['concurrent_limit'] * 0.8:
            recommendations.append("Optimize concurrency - approaching limits")
        
        return recommendations
    
    async def shutdown(self):
        """Arrêt propre monitoring throughput"""
        self.logger.info("⏹️ Arrêt Throughput Capacity Monitor...")
        
        # Arrêter monitoring
        self.monitoring_active = False
        
        if self.throughput_thread:
            self.throughput_thread.join(timeout=5)
        
        if self.capacity_thread:
            self.capacity_thread.join(timeout=5)
        
        # Arrêter executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("✅ Throughput Capacity Monitor arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_throughput_monitor():
        config = {"debug": True}
        monitor = ThroughputCapacityMonitor(config)
        
        await monitor.initialize()
        
        # Simulate some requests
        for i in range(10):
            request_id = f"req_{i}"
            await monitor.record_request_start(
                request_id=request_id,
                creator_id="creator_123",
                creator_tier=CreatorTier.PREMIUM,
                service_type=ServiceType.CONTENT_ANALYSIS,
                content_modality=ContentModality.VIDEO,
                request_size_bytes=1024 * 100
            )
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            await monitor.record_request_completion(
                request_id=request_id,
                success=True,
                response_size_bytes=1024 * 50,
                response_time_ms=150.0
            )
        
        # Wait for metrics collection
        await asyncio.sleep(15)
        
        # Get overview
        overview = await monitor.get_throughput_overview()
        print(f"Throughput Overview: {json.dumps(overview, indent=2)}")
        
        # Get creator analytics
        creator_analytics = await monitor.get_creator_throughput_analytics("creator_123")
        print(f"Creator Analytics: {json.dumps(creator_analytics, indent=2)}")
        
        print("✅ Throughput Capacity Monitor test passed")
        await monitor.shutdown()
    
    asyncio.run(test_throughput_monitor())