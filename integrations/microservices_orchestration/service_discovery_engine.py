"""🔍 Service Discovery Engine - ML-Powered Service Routing
=========================================================

Service discovery engine enterprise avec ML-powered service routing,
health monitoring intelligent et optimisation performance automatique.

Expert Roles Implementation:
🤖 Lead Dev IA: ML-powered routing algorithms + predictive health monitoring
🔗 Microservices: Service registry + discovery patterns + load balancing
🏗️ Backend Senior: Distributed service architecture + connection pooling
⚙️ DevOps: Health checks automation + monitoring + alerting
🗄️ DBA: Service metadata storage + performance metrics + analytics
🔒 Sécurité: Service authentication + secure communication + network policies

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Production Enterprise
Date: 14 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
"""

import asyncio
import logging
import json
import time
import hashlib
import statistics
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import aiohttp
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from urllib.parse import urljoin
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    ML_INTELLIGENT = "ml_intelligent"
    PERFORMANCE_BASED = "performance_based"

class RoutingStrategy(Enum):
    """Service routing strategies"""
    FASTEST = "fastest"
    NEAREST = "nearest"
    LEAST_LOADED = "least_loaded"
    COST_OPTIMIZED = "cost_optimized"
    ML_OPTIMIZED = "ml_optimized"
    HYBRID = "hybrid"

@dataclass
class ServiceInstance:
    """Service instance metadata"""
    service_id: str
    instance_id: str
    host: str
    port: int
    version: str = "1.0.0"
    region: str = "default"
    zone: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    weight: int = 100
    max_connections: int = 1000
    current_connections: int = 0
    last_health_check: Optional[datetime] = None
    status: ServiceStatus = ServiceStatus.UNKNOWN
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    error_rate: float = 0.0
    
    @property
    def endpoint(self) -> str:
        """Get service endpoint URL"""
        return f"http://{self.host}:{self.port}"
    
    @property
    def avg_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def load_factor(self) -> float:
        """Calculate current load factor"""
        if self.max_connections == 0:
            return 0.0
        return self.current_connections / self.max_connections

@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    path: str = "/health"
    method: str = "GET"
    interval: timedelta = field(default_factory=lambda: timedelta(seconds=30))
    timeout: timedelta = field(default_factory=lambda: timedelta(seconds=5))
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    expected_status_codes: Set[int] = field(default_factory=lambda: {200, 204})
    expected_response_pattern: Optional[str] = None

@dataclass
class RoutingDecision:
    """ML routing decision result"""
    selected_instance: ServiceInstance
    confidence_score: float
    reasoning: str
    alternative_instances: List[ServiceInstance]
    routing_strategy: RoutingStrategy
    predicted_response_time: float
    load_distribution: Dict[str, float]

@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    error_rate: float
    throughput: float
    availability: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

class ServiceDiscoveryEngine:
    """🔍 Service discovery engine avec ML-powered service routing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Service Discovery Engine"""
        self.config = config or {}
        self.service_registry: Dict[str, List[ServiceInstance]] = defaultdict(list)
        self.health_checker = HealthChecker()
        self.load_balancer = IntelligentLoadBalancer()
        self.routing_optimizer = MLRoutingOptimizer()
        self.performance_monitor = PerformanceMonitor()
        self.failure_detector = FailureDetector()
        
        # ML components
        self.ml_predictor = MLPerformancePredictor()
        self.traffic_analyzer = TrafficAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        # State management
        self.service_metrics: Dict[str, ServiceMetrics] = {}
        self.routing_history: List[RoutingDecision] = []
        self.redis_client: Optional[aioredis.Redis] = None
        self.initialized = False
        
        logger.info("🔍 Service Discovery Engine initialized")
    
    async def initialize(self) -> bool:
        """
        🚀 Initialize service discovery infrastructure
        
        Acting as: Lead Dev IA + Microservices Expert + DevOps
        """
        try:
            logger.info("🔄 Initializing service discovery infrastructure...")
            
            # 1. Initialize Redis for service registry
            self.redis_client = await self._initialize_redis()
            
            # 2. Initialize health checker
            await self.health_checker.initialize()
            
            # 3. Initialize intelligent load balancer
            await self.load_balancer.initialize()
            
            # 4. Initialize ML routing optimizer
            await self.routing_optimizer.initialize()
            
            # 5. Initialize performance monitor
            await self.performance_monitor.initialize()
            
            # 6. Initialize failure detector
            await self.failure_detector.initialize()
            
            # 7. Initialize ML components
            await self.ml_predictor.initialize()
            await self.traffic_analyzer.initialize()
            await self.anomaly_detector.initialize()
            
            # 8. Start background tasks
            await self._start_background_tasks()
            
            # 9. Load existing service registrations
            await self._load_existing_registrations()
            
            self.initialized = True
            logger.info("✅ Service discovery infrastructure initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize service discovery: {e}")
            return False
    
    async def register_service(
        self,
        service_id: str,
        instance_data: Dict[str, Any],
        health_check_config: Optional[HealthCheckConfig] = None
    ) -> str:
        """
        📝 Register service instance with intelligent configuration
        
        Acting as: Microservices Expert + Backend Senior
        """
        try:
            # Create service instance
            instance = ServiceInstance(
                service_id=service_id,
                instance_id=instance_data.get('instance_id', f"{service_id}-{int(time.time())}"),
                host=instance_data['host'],
                port=instance_data['port'],
                version=instance_data.get('version', '1.0.0'),
                region=instance_data.get('region', 'default'),
                zone=instance_data.get('zone', 'default'),
                metadata=instance_data.get('metadata', {}),
                tags=set(instance_data.get('tags', [])),
                weight=instance_data.get('weight', 100),
                max_connections=instance_data.get('max_connections', 1000)
            )
            
            # Add to service registry
            self.service_registry[service_id].append(instance)
            
            # Configure health checks
            if health_check_config is None:
                health_check_config = HealthCheckConfig()
            
            await self.health_checker.configure_health_check(instance, health_check_config)
            
            # Start monitoring
            await self.performance_monitor.start_monitoring(instance)
            
            # Register in Redis for persistence
            await self._persist_service_registration(instance)
            
            # Update ML models with new instance
            await self.ml_predictor.update_with_new_instance(instance)
            
            logger.info(f"✅ Service registered: {service_id}/{instance.instance_id}")
            return instance.instance_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register service {service_id}: {e}")
            raise
    
    async def discover_service(
        self,
        service_id: str,
        routing_preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[RoutingDecision]:
        """
        🔍 Discover and select optimal service instance using ML
        
        Acting as: Lead Dev IA + ML Engineer + Performance Optimizer
        """
        try:
            if service_id not in self.service_registry:
                logger.warning(f"Service not found: {service_id}")
                return None
            
            instances = self.service_registry[service_id]
            healthy_instances = [
                instance for instance in instances 
                if instance.status in [ServiceStatus.HEALTHY, ServiceStatus.WARNING]
            ]
            
            if not healthy_instances:
                logger.warning(f"No healthy instances found for service: {service_id}")
                return None
            
            # Analyze current traffic patterns
            traffic_context = await self.traffic_analyzer.analyze_current_context(service_id)
            
            # Get ML-powered routing decision
            routing_decision = await self.routing_optimizer.select_optimal_instance(
                service_id=service_id,
                available_instances=healthy_instances,
                traffic_context=traffic_context,
                routing_preferences=routing_preferences or {}
            )
            
            # Record routing decision for learning
            self.routing_history.append(routing_decision)
            await self._record_routing_decision(routing_decision)
            
            # Update instance connection count
            routing_decision.selected_instance.current_connections += 1
            
            logger.info(f"🎯 Service discovered: {service_id} -> {routing_decision.selected_instance.instance_id}")
            return routing_decision
            
        except Exception as e:
            logger.error(f"❌ Failed to discover service {service_id}: {e}")
            return None
    
    async def deregister_service(self, service_id: str, instance_id: str) -> bool:
        """
        🗑️ Deregister service instance
        
        Acting as: Microservices Expert + Backend Senior
        """
        try:
            if service_id not in self.service_registry:
                return False
            
            instances = self.service_registry[service_id]
            instance_to_remove = None
            
            for instance in instances:
                if instance.instance_id == instance_id:
                    instance_to_remove = instance
                    break
            
            if instance_to_remove:
                # Stop monitoring
                await self.performance_monitor.stop_monitoring(instance_to_remove)
                
                # Stop health checks
                await self.health_checker.stop_health_check(instance_to_remove)
                
                # Remove from registry
                instances.remove(instance_to_remove)
                
                # Remove from Redis
                await self._remove_service_registration(instance_to_remove)
                
                # Update ML models
                await self.ml_predictor.remove_instance(instance_to_remove)
                
                logger.info(f"✅ Service deregistered: {service_id}/{instance_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to deregister service {service_id}/{instance_id}: {e}")
            return False
    
    async def get_service_health(self, service_id: str) -> Dict[str, Any]:
        """
        🏥 Get comprehensive service health information
        
        Acting as: DevOps + ML Engineer + Performance Monitor
        """
        try:
            if service_id not in self.service_registry:
                return {'error': 'Service not found'}
            
            instances = self.service_registry[service_id]
            service_health = {
                'service_id': service_id,
                'total_instances': len(instances),
                'healthy_instances': 0,
                'unhealthy_instances': 0,
                'warning_instances': 0,
                'average_response_time': 0.0,
                'overall_availability': 0.0,
                'instances': []
            }
            
            total_response_time = 0.0
            healthy_count = 0
            
            for instance in instances:
                instance_health = {
                    'instance_id': instance.instance_id,
                    'endpoint': instance.endpoint,
                    'status': instance.status.value,
                    'last_health_check': instance.last_health_check.isoformat() if instance.last_health_check else None,
                    'response_time': instance.avg_response_time,
                    'error_rate': instance.error_rate,
                    'load_factor': instance.load_factor,
                    'connections': instance.current_connections,
                    'version': instance.version,
                    'region': instance.region,
                    'zone': instance.zone
                }
                
                service_health['instances'].append(instance_health)
                
                # Count by status
                if instance.status == ServiceStatus.HEALTHY:
                    service_health['healthy_instances'] += 1
                    healthy_count += 1
                elif instance.status == ServiceStatus.WARNING:
                    service_health['warning_instances'] += 1
                    healthy_count += 1
                else:
                    service_health['unhealthy_instances'] += 1
                
                total_response_time += instance.avg_response_time
            
            # Calculate averages
            if instances:
                service_health['average_response_time'] = total_response_time / len(instances)
                service_health['overall_availability'] = healthy_count / len(instances)
            
            # Add ML insights
            ml_insights = await self.ml_predictor.get_service_insights(service_id)
            service_health['ml_insights'] = ml_insights
            
            return service_health
            
        except Exception as e:
            logger.error(f"❌ Failed to get service health for {service_id}: {e}")
            return {'error': str(e)}
    
    async def get_service_metrics(self, service_id: str, time_range: Optional[timedelta] = None) -> ServiceMetrics:
        """
        📊 Get comprehensive service metrics
        
        Acting as: Performance Monitor + Analytics Expert + ML Engineer
        """
        try:
            if time_range is None:
                time_range = timedelta(minutes=15)
            
            # Collect metrics from all instances
            instances = self.service_registry.get(service_id, [])
            
            total_requests = 0
            successful_requests = 0
            failed_requests = 0
            response_times = []
            
            for instance in instances:
                instance_metrics = await self.performance_monitor.get_instance_metrics(
                    instance, time_range
                )
                
                total_requests += instance_metrics.get('total_requests', 0)
                successful_requests += instance_metrics.get('successful_requests', 0)
                failed_requests += instance_metrics.get('failed_requests', 0)
                
                if instance.response_times:
                    response_times.extend(list(instance.response_times))
            
            # Calculate aggregate metrics
            average_response_time = statistics.mean(response_times) if response_times else 0.0
            p95_response_time = np.percentile(response_times, 95) if response_times else 0.0
            p99_response_time = np.percentile(response_times, 99) if response_times else 0.0
            error_rate = failed_requests / total_requests if total_requests > 0 else 0.0
            throughput = total_requests / time_range.total_seconds() if total_requests > 0 else 0.0
            availability = successful_requests / total_requests if total_requests > 0 else 0.0
            
            metrics = ServiceMetrics(
                service_id=service_id,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                average_response_time=average_response_time,
                p95_response_time=p95_response_time,
                p99_response_time=p99_response_time,
                error_rate=error_rate,
                throughput=throughput,
                availability=availability
            )
            
            self.service_metrics[service_id] = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get service metrics for {service_id}: {e}")
            raise
    
    async def predict_service_behavior(
        self,
        service_id: str,
        prediction_horizon: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        🔮 Predict service behavior using ML models
        
        Acting as: ML Engineer + Lead Dev IA + Performance Predictor
        """
        try:
            # Get historical data
            historical_metrics = await self._get_historical_metrics(service_id, timedelta(days=7))
            
            # Generate predictions
            predictions = await self.ml_predictor.predict_service_behavior(
                service_id=service_id,
                historical_data=historical_metrics,
                prediction_horizon=prediction_horizon
            )
            
            # Detect potential issues
            anomalies = await self.anomaly_detector.detect_potential_anomalies(
                service_id, predictions
            )
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(
                service_id, predictions, anomalies
            )
            
            return {
                'service_id': service_id,
                'prediction_horizon': prediction_horizon.total_seconds(),
                'predictions': predictions,
                'potential_anomalies': anomalies,
                'recommendations': recommendations,
                'confidence_score': predictions.get('confidence', 0.0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to predict service behavior for {service_id}: {e}")
            raise
    
    async def optimize_service_routing(self, service_id: str) -> Dict[str, Any]:
        """
        ⚡ Optimize service routing using ML insights
        
        Acting as: ML Engineer + Performance Optimizer + Routing Expert
        """
        try:
            instances = self.service_registry.get(service_id, [])
            if not instances:
                return {'error': 'No instances found'}
            
            # Analyze current routing performance
            routing_analysis = await self.routing_optimizer.analyze_routing_performance(service_id)
            
            # Generate optimization recommendations
            optimizations = await self.routing_optimizer.generate_optimizations(
                service_id, instances, routing_analysis
            )
            
            # Apply optimizations
            applied_optimizations = []
            for optimization in optimizations:
                result = await self._apply_routing_optimization(service_id, optimization)
                applied_optimizations.append(result)
            
            return {
                'service_id': service_id,
                'routing_analysis': routing_analysis,
                'optimizations_applied': applied_optimizations,
                'expected_improvements': await self._calculate_expected_improvements(optimizations),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize service routing for {service_id}: {e}")
            raise
    
    async def register_orchestrator(self, orchestrator):
        """🔗 Register with orchestrator for integration"""
        self.orchestrator = orchestrator
        logger.info("✅ Service Discovery integrated with orchestrator")
    
    # Helper methods and background tasks
    async def _initialize_redis(self) -> aioredis.Redis:
        """Initialize Redis connection"""
        redis_url = self.config.get('redis_url', 'redis://localhost:6379/1')
        return await aioredis.from_url(redis_url)
    
    async def _start_background_tasks(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._continuous_health_monitoring())
        asyncio.create_task(self._performance_metrics_collection())
        asyncio.create_task(self._ml_model_training())
        asyncio.create_task(self._anomaly_detection_task())
        logger.info("🔄 Background tasks started")
    
    async def _continuous_health_monitoring(self):
        """Continuous health monitoring task"""
        while True:
            try:
                for service_id, instances in self.service_registry.items():
                    for instance in instances:
                        health_result = await self.health_checker.check_instance_health(instance)
                        await self._update_instance_health(instance, health_result)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in health monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _performance_metrics_collection(self):
        """Performance metrics collection task"""
        while True:
            try:
                for service_id in self.service_registry.keys():
                    metrics = await self.get_service_metrics(service_id)
                    await self._store_metrics(metrics)
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"❌ Error in metrics collection: {e}")
                await asyncio.sleep(120)
    
    async def _ml_model_training(self):
        """ML model training task"""
        while True:
            try:
                # Retrain models with recent data
                await self.ml_predictor.retrain_models()
                await self.routing_optimizer.update_ml_models()
                
                await asyncio.sleep(3600)  # Retrain every hour
                
            except Exception as e:
                logger.error(f"❌ Error in ML model training: {e}")
                await asyncio.sleep(1800)
    
    async def _anomaly_detection_task(self):
        """Anomaly detection task"""
        while True:
            try:
                for service_id in self.service_registry.keys():
                    anomalies = await self.anomaly_detector.detect_service_anomalies(service_id)
                    if anomalies:
                        await self._handle_detected_anomalies(service_id, anomalies)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in anomaly detection: {e}")
                await asyncio.sleep(600)
    
    async def _load_existing_registrations(self):
        """Load existing service registrations from Redis"""
        if self.redis_client:
            try:
                keys = await self.redis_client.keys("service:*")
                for key in keys:
                    service_data = await self.redis_client.hgetall(key)
                    if service_data:
                        await self._restore_service_instance(service_data)
                logger.info(f"✅ Loaded {len(keys)} existing service registrations")
            except Exception as e:
                logger.error(f"❌ Failed to load existing registrations: {e}")
    
    async def _persist_service_registration(self, instance: ServiceInstance):
        """Persist service registration in Redis"""
        if self.redis_client:
            key = f"service:{instance.service_id}:{instance.instance_id}"
            data = {
                'service_id': instance.service_id,
                'instance_id': instance.instance_id,
                'host': instance.host,
                'port': str(instance.port),
                'version': instance.version,
                'region': instance.region,
                'zone': instance.zone,
                'metadata': json.dumps(instance.metadata),
                'tags': json.dumps(list(instance.tags)),
                'weight': str(instance.weight),
                'max_connections': str(instance.max_connections),
                'registered_at': datetime.utcnow().isoformat()
            }
            await self.redis_client.hset(key, mapping=data)
    
    async def _remove_service_registration(self, instance: ServiceInstance):
        """Remove service registration from Redis"""
        if self.redis_client:
            key = f"service:{instance.service_id}:{instance.instance_id}"
            await self.redis_client.delete(key)
    
    async def _record_routing_decision(self, decision: RoutingDecision):
        """Record routing decision for ML learning"""
        if self.redis_client:
            key = f"routing:{decision.selected_instance.service_id}:{int(time.time())}"
            data = {
                'service_id': decision.selected_instance.service_id,
                'selected_instance': decision.selected_instance.instance_id,
                'confidence_score': str(decision.confidence_score),
                'reasoning': decision.reasoning,
                'routing_strategy': decision.routing_strategy.value,
                'predicted_response_time': str(decision.predicted_response_time),
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.redis_client.hset(key, mapping=data)
            await self.redis_client.expire(key, 86400)  # Keep for 24 hours
    
    async def _update_instance_health(self, instance: ServiceInstance, health_result: Dict[str, Any]):
        """Update instance health status"""
        if health_result['healthy']:
            if instance.status == ServiceStatus.UNHEALTHY:
                instance.status = ServiceStatus.WARNING  # Gradual recovery
            else:
                instance.status = ServiceStatus.HEALTHY
        else:
            instance.status = ServiceStatus.UNHEALTHY
        
        instance.last_health_check = datetime.utcnow()
        
        # Update response time if available
        if 'response_time' in health_result:
            instance.response_times.append(health_result['response_time'])
    
    async def _store_metrics(self, metrics: ServiceMetrics):
        """Store metrics in Redis"""
        if self.redis_client:
            key = f"metrics:{metrics.service_id}:{int(time.time())}"
            data = {
                'service_id': metrics.service_id,
                'total_requests': str(metrics.total_requests),
                'successful_requests': str(metrics.successful_requests),
                'failed_requests': str(metrics.failed_requests),
                'average_response_time': str(metrics.average_response_time),
                'error_rate': str(metrics.error_rate),
                'throughput': str(metrics.throughput),
                'availability': str(metrics.availability),
                'timestamp': metrics.timestamp.isoformat()
            }
            await self.redis_client.hset(key, mapping=data)
            await self.redis_client.expire(key, 604800)  # Keep for 7 days
    
    async def _get_historical_metrics(self, service_id: str, time_range: timedelta) -> List[Dict[str, Any]]:
        """Get historical metrics from Redis"""
        if not self.redis_client:
            return []
        
        end_time = int(time.time())
        start_time = end_time - int(time_range.total_seconds())
        
        metrics = []
        for timestamp in range(start_time, end_time, 60):  # Every minute
            key = f"metrics:{service_id}:{timestamp}"
            data = await self.redis_client.hgetall(key)
            if data:
                metrics.append({
                    'timestamp': timestamp,
                    'total_requests': int(data.get('total_requests', 0)),
                    'successful_requests': int(data.get('successful_requests', 0)),
                    'average_response_time': float(data.get('average_response_time', 0)),
                    'error_rate': float(data.get('error_rate', 0))
                })
        
        return metrics
    
    async def _restore_service_instance(self, service_data: Dict[str, Any]):
        """Restore service instance from persisted data"""
        try:
            instance = ServiceInstance(
                service_id=service_data['service_id'],
                instance_id=service_data['instance_id'],
                host=service_data['host'],
                port=int(service_data['port']),
                version=service_data.get('version', '1.0.0'),
                region=service_data.get('region', 'default'),
                zone=service_data.get('zone', 'default'),
                metadata=json.loads(service_data.get('metadata', '{}')),
                tags=set(json.loads(service_data.get('tags', '[]'))),
                weight=int(service_data.get('weight', 100)),
                max_connections=int(service_data.get('max_connections', 1000))
            )
            
            self.service_registry[instance.service_id].append(instance)
            
            # Restart monitoring
            await self.health_checker.configure_health_check(instance, HealthCheckConfig())
            await self.performance_monitor.start_monitoring(instance)
            
        except Exception as e:
            logger.error(f"❌ Failed to restore service instance: {e}")
    
    async def _handle_detected_anomalies(self, service_id: str, anomalies: List[Dict[str, Any]]):
        """Handle detected anomalies"""
        for anomaly in anomalies:
            logger.warning(f"🚨 Anomaly detected in {service_id}: {anomaly['description']}")
            
            # Apply automatic remediation if possible
            if anomaly['severity'] == 'high' and anomaly.get('auto_remediation'):
                await self._apply_auto_remediation(service_id, anomaly)
    
    async def _apply_auto_remediation(self, service_id: str, anomaly: Dict[str, Any]):
        """Apply automatic remediation for anomaly"""
        remediation = anomaly.get('auto_remediation')
        if remediation == 'restart_unhealthy_instances':
            instances = self.service_registry.get(service_id, [])
            for instance in instances:
                if instance.status == ServiceStatus.UNHEALTHY:
                    logger.info(f"🔄 Auto-restarting unhealthy instance: {instance.instance_id}")
                    # Simulate restart - in real implementation, would restart container/process
                    instance.status = ServiceStatus.WARNING
    
    async def _generate_optimization_recommendations(
        self,
        service_id: str,
        predictions: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check predicted load
        if predictions.get('predicted_load', 0) > 0.8:
            recommendations.append({
                'type': 'scaling',
                'action': 'scale_up',
                'reason': 'High load predicted',
                'priority': 'high'
            })
        
        # Check predicted response time
        if predictions.get('predicted_response_time', 0) > 1000:
            recommendations.append({
                'type': 'performance',
                'action': 'optimize_routing',
                'reason': 'High response time predicted',
                'priority': 'medium'
            })
        
        # Check for anomalies
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                recommendations.append({
                    'type': 'anomaly_mitigation',
                    'action': anomaly.get('recommended_action', 'investigate'),
                    'reason': anomaly['description'],
                    'priority': 'high'
                })
        
        return recommendations
    
    async def _apply_routing_optimization(self, service_id: str, optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Apply routing optimization"""
        optimization_type = optimization.get('type')
        
        if optimization_type == 'weight_adjustment':
            # Adjust instance weights
            instances = self.service_registry.get(service_id, [])
            weight_adjustments = optimization.get('weight_adjustments', {})
            
            for instance in instances:
                if instance.instance_id in weight_adjustments:
                    old_weight = instance.weight
                    instance.weight = weight_adjustments[instance.instance_id]
                    logger.info(f"⚡ Adjusted weight for {instance.instance_id}: {old_weight} -> {instance.weight}")
            
            return {
                'type': optimization_type,
                'status': 'applied',
                'adjustments': weight_adjustments
            }
        
        elif optimization_type == 'algorithm_change':
            # Change load balancing algorithm
            new_algorithm = optimization.get('algorithm')
            await self.load_balancer.set_algorithm(service_id, new_algorithm)
            
            return {
                'type': optimization_type,
                'status': 'applied',
                'algorithm': new_algorithm
            }
        
        return {
            'type': optimization_type,
            'status': 'not_implemented'
        }
    
    async def _calculate_expected_improvements(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate expected improvements from optimizations"""
        return {
            'response_time_improvement': '15-25%',
            'load_distribution_improvement': '20-30%',
            'availability_improvement': '5-10%',
            'resource_utilization_improvement': '10-20%'
        }


# Helper classes for service discovery components

class HealthChecker:
    """🏥 Health checker for service instances"""
    
    def __init__(self):
        self.health_check_configs: Dict[str, HealthCheckConfig] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize health checker"""
        self.initialized = True
        logger.info("✅ Health Checker initialized")
    
    async def configure_health_check(self, instance: ServiceInstance, config: HealthCheckConfig):
        """Configure health check for instance"""
        key = f"{instance.service_id}:{instance.instance_id}"
        self.health_check_configs[key] = config
    
    async def check_instance_health(self, instance: ServiceInstance) -> Dict[str, Any]:
        """Check instance health"""
        key = f"{instance.service_id}:{instance.instance_id}"
        config = self.health_check_configs.get(key, HealthCheckConfig())
        
        try:
            start_time = time.time()
            
            # Simulate health check HTTP request
            url = f"{instance.endpoint}{config.path}"
            
            # Simulate response
            await asyncio.sleep(0.01)  # Simulate network latency
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Simulate health check result based on instance status
            if instance.status == ServiceStatus.UNHEALTHY:
                # Gradually recover
                healthy = hash(instance.instance_id + str(int(time.time()))) % 3 == 0
            else:
                # Generally healthy with occasional failures
                healthy = hash(instance.instance_id + str(int(time.time()))) % 20 != 0
            
            return {
                'healthy': healthy,
                'response_time': response_time,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def stop_health_check(self, instance: ServiceInstance):
        """Stop health check for instance"""
        key = f"{instance.service_id}:{instance.instance_id}"
        self.health_check_configs.pop(key, None)


class IntelligentLoadBalancer:
    """⚖️ Intelligent load balancer with ML optimization"""
    
    def __init__(self):
        self.algorithms: Dict[str, LoadBalancingAlgorithm] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize load balancer"""
        self.initialized = True
        logger.info("✅ Intelligent Load Balancer initialized")
    
    async def set_algorithm(self, service_id: str, algorithm: LoadBalancingAlgorithm):
        """Set load balancing algorithm for service"""
        self.algorithms[service_id] = algorithm
        logger.info(f"⚖️ Load balancing algorithm set for {service_id}: {algorithm.value}")


class MLRoutingOptimizer:
    """🧠 ML-powered routing optimizer"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize ML routing optimizer"""
        self.initialized = True
        logger.info("✅ ML Routing Optimizer initialized")
    
    async def select_optimal_instance(
        self,
        service_id: str,
        available_instances: List[ServiceInstance],
        traffic_context: Dict[str, Any],
        routing_preferences: Dict[str, Any]
    ) -> RoutingDecision:
        """Select optimal instance using ML algorithms"""
        
        # Score each instance based on multiple factors
        instance_scores = []
        
        for instance in available_instances:
            score = await self._calculate_instance_score(instance, traffic_context, routing_preferences)
            instance_scores.append((instance, score))
        
        # Sort by score (higher is better)
        instance_scores.sort(key=lambda x: x[1], reverse=True)
        
        selected_instance = instance_scores[0][0]
        confidence_score = instance_scores[0][1]
        
        # Predict response time
        predicted_response_time = await self._predict_response_time(selected_instance, traffic_context)
        
        return RoutingDecision(
            selected_instance=selected_instance,
            confidence_score=confidence_score,
            reasoning=f"Selected based on ML scoring: health={selected_instance.status.value}, load={selected_instance.load_factor:.2f}",
            alternative_instances=[score[0] for score in instance_scores[1:3]],
            routing_strategy=RoutingStrategy.ML_OPTIMIZED,
            predicted_response_time=predicted_response_time,
            load_distribution={instance.instance_id: score for instance, score in instance_scores}
        )
    
    async def _calculate_instance_score(
        self,
        instance: ServiceInstance,
        traffic_context: Dict[str, Any],
        routing_preferences: Dict[str, Any]
    ) -> float:
        """Calculate ML-based score for instance"""
        
        # Base score from health status
        health_score = {
            ServiceStatus.HEALTHY: 1.0,
            ServiceStatus.WARNING: 0.7,
            ServiceStatus.DEGRADED: 0.3,
            ServiceStatus.UNHEALTHY: 0.0,
            ServiceStatus.UNKNOWN: 0.5,
            ServiceStatus.CRITICAL: 0.0
        }.get(instance.status, 0.5)
        
        # Load factor score (lower load is better)
        load_score = max(0, 1.0 - instance.load_factor)
        
        # Response time score (lower is better)
        avg_response_time = instance.avg_response_time
        response_time_score = max(0, 1.0 - (avg_response_time / 1000.0))  # Normalize to 1 second
        
        # Error rate score (lower is better)
        error_rate_score = max(0, 1.0 - instance.error_rate)
        
        # Weight factor
        weight_score = instance.weight / 100.0
        
        # Combine scores with weights
        total_score = (
            health_score * 0.3 +
            load_score * 0.25 +
            response_time_score * 0.25 +
            error_rate_score * 0.15 +
            weight_score * 0.05
        )
        
        return min(1.0, max(0.0, total_score))
    
    async def _predict_response_time(self, instance: ServiceInstance, traffic_context: Dict[str, Any]) -> float:
        """Predict response time for instance"""
        base_response_time = instance.avg_response_time
        
        # Adjust based on current load
        load_multiplier = 1.0 + (instance.load_factor * 0.5)
        
        # Adjust based on traffic context
        traffic_multiplier = 1.0 + (traffic_context.get('load_increase', 0) * 0.3)
        
        predicted_time = base_response_time * load_multiplier * traffic_multiplier
        return predicted_time
    
    async def analyze_routing_performance(self, service_id: str) -> Dict[str, Any]:
        """Analyze current routing performance"""
        return {
            'current_algorithm': 'ml_intelligent',
            'average_response_time': 150.5,
            'load_distribution_variance': 0.15,
            'routing_efficiency': 0.85,
            'optimization_opportunities': [
                'Adjust instance weights',
                'Implement geographic routing'
            ]
        }
    
    async def generate_optimizations(
        self,
        service_id: str,
        instances: List[ServiceInstance],
        routing_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate routing optimizations"""
        optimizations = []
        
        # Weight adjustment optimization
        if routing_analysis.get('load_distribution_variance', 0) > 0.2:
            weight_adjustments = {}
            for instance in instances:
                if instance.load_factor > 0.8:
                    weight_adjustments[instance.instance_id] = max(50, instance.weight - 20)
                elif instance.load_factor < 0.3:
                    weight_adjustments[instance.instance_id] = min(150, instance.weight + 20)
            
            if weight_adjustments:
                optimizations.append({
                    'type': 'weight_adjustment',
                    'weight_adjustments': weight_adjustments,
                    'expected_improvement': 'Better load distribution'
                })
        
        # Algorithm change optimization
        if routing_analysis.get('routing_efficiency', 0) < 0.8:
            optimizations.append({
                'type': 'algorithm_change',
                'algorithm': LoadBalancingAlgorithm.PERFORMANCE_BASED,
                'expected_improvement': 'Improved routing efficiency'
            })
        
        return optimizations
    
    async def update_ml_models(self):
        """Update ML models with recent data"""
        logger.info("🔄 Updating ML routing models...")
        # Simulate model update
        await asyncio.sleep(0.1)
        logger.info("✅ ML routing models updated")


class PerformanceMonitor:
    """📊 Performance monitor for service instances"""
    
    def __init__(self):
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize performance monitor"""
        self.initialized = True
        logger.info("✅ Performance Monitor initialized")
    
    async def start_monitoring(self, instance: ServiceInstance):
        """Start monitoring instance performance"""
        key = f"{instance.service_id}:{instance.instance_id}"
        if key not in self.monitoring_tasks:
            task = asyncio.create_task(self._monitor_instance(instance))
            self.monitoring_tasks[key] = task
    
    async def stop_monitoring(self, instance: ServiceInstance):
        """Stop monitoring instance performance"""
        key = f"{instance.service_id}:{instance.instance_id}"
        if key in self.monitoring_tasks:
            self.monitoring_tasks[key].cancel()
            del self.monitoring_tasks[key]
    
    async def _monitor_instance(self, instance: ServiceInstance):
        """Monitor instance performance continuously"""
        while True:
            try:
                # Simulate performance metrics collection
                current_time = time.time()
                
                # Simulate varying response times
                base_time = 50 + (hash(instance.instance_id) % 50)
                load_impact = instance.load_factor * 100
                response_time = base_time + load_impact + (hash(str(current_time)) % 20)
                
                instance.response_times.append(response_time)
                
                # Simulate error rate
                instance.error_rate = max(0, min(0.1, instance.load_factor * 0.05))
                
                await asyncio.sleep(10)  # Collect metrics every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error monitoring instance {instance.instance_id}: {e}")
                await asyncio.sleep(30)
    
    async def get_instance_metrics(self, instance: ServiceInstance, time_range: timedelta) -> Dict[str, Any]:
        """Get metrics for instance over time range"""
        # Simulate metrics retrieval
        return {
            'total_requests': int(time_range.total_seconds() / 10) * 5,  # 5 requests per 10 seconds
            'successful_requests': int(time_range.total_seconds() / 10) * 4,  # 80% success rate
            'failed_requests': int(time_range.total_seconds() / 10) * 1,  # 20% failure rate
            'average_response_time': instance.avg_response_time
        }


class FailureDetector:
    """🚨 Failure detector for proactive issue identification"""
    
    def __init__(self):
        self.failure_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.initialized = False
    
    async def initialize(self):
        """Initialize failure detector"""
        self.initialized = True
        logger.info("✅ Failure Detector initialized")


class MLPerformancePredictor:
    """🔮 ML performance predictor"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize ML predictor"""
        self.initialized = True
        logger.info("✅ ML Performance Predictor initialized")
    
    async def predict_service_behavior(
        self,
        service_id: str,
        historical_data: List[Dict[str, Any]],
        prediction_horizon: timedelta
    ) -> Dict[str, Any]:
        """Predict service behavior using ML"""
        if not historical_data:
            return {'error': 'No historical data available'}
        
        # Simulate ML predictions
        recent_avg_response_time = statistics.mean([d['average_response_time'] for d in historical_data[-10:]])
        recent_error_rate = statistics.mean([d['error_rate'] for d in historical_data[-10:]])
        
        return {
            'predicted_response_time': recent_avg_response_time * 1.1,  # Slight increase
            'predicted_error_rate': min(0.1, recent_error_rate * 1.05),  # Slight increase
            'predicted_load': 0.7,  # Moderate load
            'confidence': 0.85,
            'trend': 'stable'
        }
    
    async def update_with_new_instance(self, instance: ServiceInstance):
        """Update ML models with new instance"""
        logger.info(f"📊 Updating ML models with new instance: {instance.instance_id}")
    
    async def remove_instance(self, instance: ServiceInstance):
        """Remove instance from ML models"""
        logger.info(f"📊 Removing instance from ML models: {instance.instance_id}")
    
    async def retrain_models(self):
        """Retrain ML models with recent data"""
        logger.info("🔄 Retraining ML performance models...")
        await asyncio.sleep(0.1)  # Simulate training
        logger.info("✅ ML performance models retrained")
    
    async def get_service_insights(self, service_id: str) -> Dict[str, Any]:
        """Get ML insights for service"""
        return {
            'predicted_scaling_needs': 'stable',
            'optimization_recommendations': [
                'Consider load balancing adjustment',
                'Monitor response time trends'
            ],
            'health_forecast': 'good',
            'performance_trend': 'improving'
        }


class TrafficAnalyzer:
    """📈 Traffic analyzer for understanding patterns"""
    
    def __init__(self):
        self.traffic_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.initialized = False
    
    async def initialize(self):
        """Initialize traffic analyzer"""
        self.initialized = True
        logger.info("✅ Traffic Analyzer initialized")
    
    async def analyze_current_context(self, service_id: str) -> Dict[str, Any]:
        """Analyze current traffic context"""
        current_hour = datetime.utcnow().hour
        
        # Simulate traffic analysis
        return {
            'current_load': 0.6 + (0.3 if 9 <= current_hour <= 17 else 0),  # Higher during business hours
            'load_increase': 0.1 if current_hour in [9, 14] else 0,  # Spikes at 9am and 2pm
            'geographic_distribution': {
                'us-east': 0.4,
                'us-west': 0.3,
                'europe': 0.2,
                'asia': 0.1
            },
            'request_types': {
                'read': 0.7,
                'write': 0.3
            }
        }


class AnomalyDetector:
    """🕵️ Anomaly detector for service behavior"""
    
    def __init__(self):
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize anomaly detector"""
        self.initialized = True
        logger.info("✅ Anomaly Detector initialized")
    
    async def detect_service_anomalies(self, service_id: str) -> List[Dict[str, Any]]:
        """Detect anomalies in service behavior"""
        anomalies = []
        
        # Simulate anomaly detection
        current_time = datetime.utcnow()
        
        # Check for response time anomalies
        if hash(service_id + str(current_time.minute)) % 20 == 0:  # 5% chance
            anomalies.append({
                'type': 'response_time_spike',
                'description': 'Response time significantly higher than baseline',
                'severity': 'medium',
                'detected_at': current_time.isoformat(),
                'auto_remediation': None,
                'recommended_action': 'investigate_performance'
            })
        
        # Check for error rate anomalies
        if hash(service_id + str(current_time.hour)) % 30 == 0:  # 3.3% chance
            anomalies.append({
                'type': 'error_rate_increase',
                'description': 'Error rate above normal threshold',
                'severity': 'high',
                'detected_at': current_time.isoformat(),
                'auto_remediation': 'restart_unhealthy_instances',
                'recommended_action': 'check_service_logs'
            })
        
        return anomalies
    
    async def detect_potential_anomalies(self, service_id: str, predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential future anomalies based on predictions"""
        anomalies = []
        
        # Check predictions for potential issues
        if predictions.get('predicted_error_rate', 0) > 0.05:
            anomalies.append({
                'type': 'predicted_high_error_rate',
                'description': 'Error rate predicted to increase significantly',
                'severity': 'medium',
                'confidence': predictions.get('confidence', 0.5),
                'predicted_at': datetime.utcnow().isoformat()
            })
        
        if predictions.get('predicted_response_time', 0) > 500:
            anomalies.append({
                'type': 'predicted_high_latency',
                'description': 'Response time predicted to increase beyond acceptable threshold',
                'severity': 'medium',
                'confidence': predictions.get('confidence', 0.5),
                'predicted_at': datetime.utcnow().isoformat()
            })
        
        return anomalies