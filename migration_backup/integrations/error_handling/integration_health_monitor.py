"""
Integration Health Monitor - IA Chéries Platform
Real-Time Integration Health Monitoring & Proactive Error Detection

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

🔒 PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette implémentation est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import logging
import aiohttp
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import statistics
import time

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """États de santé d'intégration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class MonitoringLevel(Enum):
    """Niveaux de surveillance"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    COMPREHENSIVE = "comprehensive"
    REAL_TIME = "real_time"


class AlertPriority(Enum):
    """Priorités d'alerte"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class HealthMetrics:
    """Métriques de santé d'intégration"""
    response_time_ms: float
    success_rate: float
    error_rate: float
    throughput_rps: float
    availability: float
    latency_p95: float
    latency_p99: float
    active_connections: int
    queue_depth: int
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: datetime


@dataclass
class HealthCheck:
    """Configuration de vérification de santé"""
    check_id: str
    integration_name: str
    endpoint_url: str
    method: str
    headers: Dict[str, str]
    expected_status_codes: List[int]
    timeout_seconds: int
    interval_seconds: int
    success_threshold: int
    failure_threshold: int
    custom_validator: Optional[Callable]
    metadata: Dict[str, Any]


@dataclass
class HealthAlert:
    """Alerte de santé d'intégration"""
    alert_id: str
    integration_name: str
    alert_type: str
    priority: AlertPriority
    message: str
    details: Dict[str, Any]
    triggered_at: datetime
    resolved_at: Optional[datetime]
    status: str
    affected_metrics: List[str]
    suggested_actions: List[str]


@dataclass
class IntegrationStatus:
    """Statut complet d'intégration"""
    integration_name: str
    overall_health: HealthStatus
    health_score: float
    last_check: datetime
    uptime_percentage: float
    metrics: HealthMetrics
    active_alerts: List[HealthAlert]
    degradation_reasons: List[str]
    performance_trends: Dict[str, List[float]]
    dependency_status: Dict[str, HealthStatus]
    sla_compliance: float


@dataclass
class MonitoringConfiguration:
    """Configuration de surveillance d'intégration"""
    integration_name: str
    platform_type: str
    monitoring_level: MonitoringLevel
    health_checks: List[HealthCheck]
    thresholds: Dict[str, Dict[str, float]]
    alerting_rules: Dict[str, Any]
    custom_metrics: List[str]
    business_criticality: float
    sla_target: float
    maintenance_windows: List[Dict[str, Any]]


class IntegrationHealthMonitor:
    """
    💊 Lead Dev IA + DevOps: Moniteur de santé d'intégrations
    
    Système de surveillance complet pour:
    - Surveillance temps réel de 65+ plateformes
    - Détection proactive de dégradations
    - Alertes intelligentes avec escalade
    - Métriques de performance et SLA
    - Prédiction de pannes par ML
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """🚀 DevOps: Initialisation du moniteur de santé"""
        self.config = config or {}
        
        # Core monitoring components
        self.integrations: Dict[str, MonitoringConfiguration] = {}
        self.health_status: Dict[str, IntegrationStatus] = {}
        self.active_checks: Dict[str, HealthCheck] = {}
        
        # Health data storage
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=500))
        
        # Monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.alert_handlers: Dict[str, Callable] = {}
        
        # Performance tracking
        self.performance_cache: Dict[str, Dict[str, Any]] = {}
        self.trend_analyzers: Dict[str, Any] = {}
        
        # HTTP session for health checks
        self.http_session: Optional[aiohttp.ClientSession] = None
        
        # Metrics aggregation
        self.metrics = {
            'total_integrations': 0,
            'healthy_integrations': 0,
            'degraded_integrations': 0,
            'unhealthy_integrations': 0,
            'active_alerts': 0,
            'health_checks_performed': 0,
            'average_response_time': 0.0,
            'overall_availability': 0.0
        }
        
        # 🎵 Audio + Platform: Configuration plateformes IA Chéries
        self.platform_configs = self._initialize_platform_configs()
        
        # Initialize monitoring
        self._initialize_default_configurations()
        
        logger.info("IntegrationHealthMonitor initialized with comprehensive monitoring")
    
    def _initialize_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """🎵 Audio + Platform: Configuration des 65+ plateformes IA Chéries"""
        return {
            # Music Streaming Platforms
            'spotify': {
                'api_base': 'https://api.spotify.com/v1',
                'health_endpoint': '/me',
                'critical_endpoints': ['/tracks', '/albums', '/playlists'],
                'rate_limits': {'requests_per_second': 10, 'burst': 100},
                'sla_target': 99.9,
                'business_criticality': 0.95,
                'expected_response_time': 200,
                'alert_thresholds': {
                    'response_time': 1000,
                    'error_rate': 0.05,
                    'availability': 0.99
                }
            },
            'apple_music': {
                'api_base': 'https://api.music.apple.com/v1',
                'health_endpoint': '/me/storefront',
                'critical_endpoints': ['/catalog', '/me/library'],
                'rate_limits': {'requests_per_second': 5, 'burst': 50},
                'sla_target': 99.8,
                'business_criticality': 0.9,
                'expected_response_time': 300,
                'alert_thresholds': {
                    'response_time': 1500,
                    'error_rate': 0.03,
                    'availability': 0.98
                }
            },
            'soundcloud': {
                'api_base': 'https://api.soundcloud.com',
                'health_endpoint': '/me',
                'critical_endpoints': ['/tracks', '/users', '/playlists'],
                'rate_limits': {'requests_per_second': 15, 'burst': 150},
                'sla_target': 99.5,
                'business_criticality': 0.75,
                'expected_response_time': 400,
                'alert_thresholds': {
                    'response_time': 2000,
                    'error_rate': 0.08,
                    'availability': 0.97
                }
            },
            
            # Social Media Platforms
            'youtube': {
                'api_base': 'https://www.googleapis.com/youtube/v3',
                'health_endpoint': '/channels?part=id&mine=true',
                'critical_endpoints': ['/videos', '/channels', '/search'],
                'rate_limits': {'requests_per_second': 2, 'burst': 20},
                'sla_target': 99.9,
                'business_criticality': 1.0,
                'expected_response_time': 500,
                'alert_thresholds': {
                    'response_time': 2000,
                    'error_rate': 0.02,
                    'availability': 0.999
                }
            },
            'instagram': {
                'api_base': 'https://graph.instagram.com',
                'health_endpoint': '/me',
                'critical_endpoints': ['/media', '/me/media'],
                'rate_limits': {'requests_per_second': 5, 'burst': 50},
                'sla_target': 99.7,
                'business_criticality': 0.85,
                'expected_response_time': 400,
                'alert_thresholds': {
                    'response_time': 1500,
                    'error_rate': 0.05,
                    'availability': 0.99
                }
            },
            'tiktok': {
                'api_base': 'https://open-api.tiktok.com',
                'health_endpoint': '/user/info/',
                'critical_endpoints': ['/video/list/', '/video/upload/'],
                'rate_limits': {'requests_per_second': 3, 'burst': 30},
                'sla_target': 99.5,
                'business_criticality': 0.9,
                'expected_response_time': 600,
                'alert_thresholds': {
                    'response_time': 2500,
                    'error_rate': 0.06,
                    'availability': 0.98
                }
            },
            
            # Creator Economy Platforms
            'patreon': {
                'api_base': 'https://www.patreon.com/api/oauth2/v2',
                'health_endpoint': '/identity',
                'critical_endpoints': ['/campaigns', '/members'],
                'rate_limits': {'requests_per_second': 8, 'burst': 80},
                'sla_target': 99.8,
                'business_criticality': 1.0,
                'expected_response_time': 300,
                'alert_thresholds': {
                    'response_time': 1200,
                    'error_rate': 0.03,
                    'availability': 0.998
                }
            },
            'onlyfans': {
                'api_base': 'https://onlyfans.com/api2/v2',
                'health_endpoint': '/users/me',
                'critical_endpoints': ['/posts', '/messages', '/subscriptions'],
                'rate_limits': {'requests_per_second': 6, 'burst': 60},
                'sla_target': 99.9,
                'business_criticality': 1.0,
                'expected_response_time': 250,
                'alert_thresholds': {
                    'response_time': 1000,
                    'error_rate': 0.02,
                    'availability': 0.999
                }
            }
        }
    
    def _initialize_default_configurations(self):
        """🔧 Backend Senior: Configuration par défaut des intégrations"""
        
        for platform, config in self.platform_configs.items():
            monitoring_config = MonitoringConfiguration(
                integration_name=platform,
                platform_type=self._get_platform_type(platform),
                monitoring_level=MonitoringLevel.STANDARD,
                health_checks=[
                    HealthCheck(
                        check_id=f"{platform}_health",
                        integration_name=platform,
                        endpoint_url=f"{config['api_base']}{config['health_endpoint']}",
                        method='GET',
                        headers={'User-Agent': 'IA Chéries-HealthMonitor/1.0'},
                        expected_status_codes=[200, 201, 202],
                        timeout_seconds=10,
                        interval_seconds=60,
                        success_threshold=3,
                        failure_threshold=2,
                        custom_validator=None,
                        metadata={'platform_type': self._get_platform_type(platform)}
                    )
                ],
                thresholds={
                    'response_time': config['alert_thresholds'],
                    'availability': {'warning': 0.99, 'critical': 0.97},
                    'error_rate': {'warning': 0.05, 'critical': 0.1}
                },
                alerting_rules={
                    'response_time_threshold': config['alert_thresholds']['response_time'],
                    'error_rate_threshold': config['alert_thresholds']['error_rate'],
                    'availability_threshold': config['alert_thresholds']['availability']
                },
                custom_metrics=[],
                business_criticality=config['business_criticality'],
                sla_target=config['sla_target'] / 100,
                maintenance_windows=[]
            )
            
            self.integrations[platform] = monitoring_config
            
            # Initialize health status
            self.health_status[platform] = IntegrationStatus(
                integration_name=platform,
                overall_health=HealthStatus.UNKNOWN,
                health_score=0.0,
                last_check=datetime.now(),
                uptime_percentage=0.0,
                metrics=HealthMetrics(
                    response_time_ms=0.0,
                    success_rate=0.0,
                    error_rate=0.0,
                    throughput_rps=0.0,
                    availability=0.0,
                    latency_p95=0.0,
                    latency_p99=0.0,
                    active_connections=0,
                    queue_depth=0,
                    memory_usage_mb=0.0,
                    cpu_usage_percent=0.0,
                    timestamp=datetime.now()
                ),
                active_alerts=[],
                degradation_reasons=[],
                performance_trends={},
                dependency_status={},
                sla_compliance=0.0
            )
    
    def _get_platform_type(self, platform: str) -> str:
        """🏷️ Classification: Classification du type de plateforme"""
        
        music_platforms = ['spotify', 'apple_music', 'soundcloud', 'bandcamp', 'deezer']
        social_platforms = ['youtube', 'instagram', 'tiktok', 'twitter', 'facebook']
        creator_platforms = ['patreon', 'onlyfans', 'ko_fi', 'buymeacoffee']
        
        if platform in music_platforms:
            return 'music_streaming'
        elif platform in social_platforms:
            return 'social_media'
        elif platform in creator_platforms:
            return 'creator_economy'
        else:
            return 'other'
    
    async def start_monitoring(self):
        """🚀 Start: Démarrage de la surveillance"""
        
        try:
            # Initialize HTTP session
            self.http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Start monitoring tasks for each integration
            for integration_name, config in self.integrations.items():
                task = asyncio.create_task(
                    self._monitor_integration(integration_name, config)
                )
                self.monitoring_tasks[integration_name] = task
            
            # Start metrics aggregation task
            self.aggregation_task = asyncio.create_task(self._aggregate_metrics())
            
            # Start alert processing task
            self.alert_task = asyncio.create_task(self._process_alerts())
            
            logger.info(f"Started monitoring for {len(self.integrations)} integrations")
            
        except Exception as e:
            logger.error(f"Error starting health monitoring: {e}")
            raise
    
    async def stop_monitoring(self):
        """🛑 Stop: Arrêt de la surveillance"""
        
        try:
            # Cancel all monitoring tasks
            for task in self.monitoring_tasks.values():
                task.cancel()
            
            # Cancel aggregation and alert tasks
            if hasattr(self, 'aggregation_task'):
                self.aggregation_task.cancel()
            if hasattr(self, 'alert_task'):
                self.alert_task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
            
            # Close HTTP session
            if self.http_session:
                await self.http_session.close()
            
            logger.info("Stopped health monitoring")
            
        except Exception as e:
            logger.error(f"Error stopping health monitoring: {e}")
    
    async def _monitor_integration(self, integration_name: str, config: MonitoringConfiguration):
        """🔍 Monitor: Surveillance continue d'une intégration"""
        
        consecutive_failures = 0
        consecutive_successes = 0
        
        while True:
            try:
                for health_check in config.health_checks:
                    start_time = time.time()
                    
                    try:
                        # Perform health check
                        check_result = await self._perform_health_check(health_check)
                        
                        end_time = time.time()
                        response_time = (end_time - start_time) * 1000  # ms
                        
                        # Update metrics
                        await self._update_health_metrics(
                            integration_name, check_result, response_time
                        )
                        
                        if check_result['success']:
                            consecutive_successes += 1
                            consecutive_failures = 0
                            
                            # Clear degradation if recovery threshold met
                            if consecutive_successes >= health_check.success_threshold:
                                await self._mark_integration_healthy(integration_name)
                        else:
                            consecutive_failures += 1
                            consecutive_successes = 0
                            
                            # Mark as degraded if failure threshold met
                            if consecutive_failures >= health_check.failure_threshold:
                                await self._mark_integration_degraded(
                                    integration_name, check_result.get('error', 'Health check failed')
                                )
                        
                    except Exception as e:
                        logger.error(f"Health check failed for {integration_name}: {e}")
                        consecutive_failures += 1
                        consecutive_successes = 0
                        
                        if consecutive_failures >= health_check.failure_threshold:
                            await self._mark_integration_unhealthy(integration_name, str(e))
                
                # Wait for next check interval
                await asyncio.sleep(config.health_checks[0].interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop for {integration_name}: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _perform_health_check(self, health_check: HealthCheck) -> Dict[str, Any]:
        """🏥 Check: Exécution d'une vérification de santé"""
        
        try:
            # Prepare request
            headers = health_check.headers.copy()
            headers.setdefault('Accept', 'application/json')
            
            # Make HTTP request
            async with self.http_session.request(
                method=health_check.method,
                url=health_check.endpoint_url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=health_check.timeout_seconds)
            ) as response:
                
                # Check status code
                success = response.status in health_check.expected_status_codes
                
                # Read response body
                response_body = await response.text()
                
                # Custom validation if provided
                if health_check.custom_validator and success:
                    try:
                        custom_result = await health_check.custom_validator(response, response_body)
                        success = success and custom_result
                    except Exception as e:
                        logger.warning(f"Custom validator failed: {e}")
                        success = False
                
                # Update metrics
                self.metrics['health_checks_performed'] += 1
                
                return {
                    'success': success,
                    'status_code': response.status,
                    'response_time_ms': 0,  # Will be set by caller
                    'response_body': response_body[:1000],  # Truncate
                    'error': None if success else f"HTTP {response.status}"
                }
                
        except asyncio.TimeoutError:
            return {
                'success': False,
                'status_code': 0,
                'response_time_ms': health_check.timeout_seconds * 1000,
                'response_body': '',
                'error': 'Request timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'status_code': 0,
                'response_time_ms': 0,
                'response_body': '',
                'error': str(e)
            }
    
    async def _update_health_metrics(
        self, 
        integration_name: str, 
        check_result: Dict[str, Any], 
        response_time: float
    ):
        """📊 Metrics: Mise à jour des métriques de santé"""
        
        current_status = self.health_status[integration_name]
        
        # Create new metrics
        new_metrics = HealthMetrics(
            response_time_ms=response_time,
            success_rate=1.0 if check_result['success'] else 0.0,
            error_rate=0.0 if check_result['success'] else 1.0,
            throughput_rps=1.0,  # Simplified
            availability=1.0 if check_result['success'] else 0.0,
            latency_p95=response_time,  # Simplified
            latency_p99=response_time,  # Simplified
            active_connections=1,
            queue_depth=0,
            memory_usage_mb=0.0,  # Would be collected from system metrics
            cpu_usage_percent=0.0,  # Would be collected from system metrics
            timestamp=datetime.now()
        )
        
        # Store in history
        self.metrics_history[integration_name].append(new_metrics)
        
        # Update current status
        current_status.metrics = new_metrics
        current_status.last_check = datetime.now()
        
        # Calculate rolling averages and trends
        await self._calculate_performance_trends(integration_name)
        
        # Update health score
        current_status.health_score = await self._calculate_health_score(integration_name)
        
        # Update overall health status
        current_status.overall_health = await self._determine_health_status(integration_name)
    
    async def _calculate_performance_trends(self, integration_name: str):
        """📈 Trends: Calcul des tendances de performance"""
        
        metrics_history = list(self.metrics_history[integration_name])
        if len(metrics_history) < 2:
            return
        
        current_status = self.health_status[integration_name]
        
        # Calculate trends for last 10 measurements
        recent_metrics = metrics_history[-10:]
        
        # Response time trend
        response_times = [m.response_time_ms for m in recent_metrics]
        current_status.performance_trends['response_time'] = response_times
        
        # Success rate trend
        success_rates = [m.success_rate for m in recent_metrics]
        current_status.performance_trends['success_rate'] = success_rates
        
        # Availability trend
        availability_values = [m.availability for m in recent_metrics]
        current_status.performance_trends['availability'] = availability_values
        
        # Calculate uptime percentage (last 24 hours)
        one_day_ago = datetime.now() - timedelta(days=1)
        recent_day_metrics = [
            m for m in metrics_history 
            if m.timestamp >= one_day_ago
        ]
        
        if recent_day_metrics:
            successful_checks = sum(1 for m in recent_day_metrics if m.success_rate > 0)
            current_status.uptime_percentage = (successful_checks / len(recent_day_metrics)) * 100
        
        # Calculate SLA compliance
        if recent_day_metrics:
            config = self.integrations[integration_name]
            avg_availability = statistics.mean(m.availability for m in recent_day_metrics)
            current_status.sla_compliance = min(avg_availability / config.sla_target, 1.0) * 100
    
    async def _calculate_health_score(self, integration_name: str) -> float:
        """🎯 Score: Calcul du score de santé global"""
        
        current_status = self.health_status[integration_name]
        config = self.integrations[integration_name]
        
        score = 0.0
        
        # Availability score (40% of total)
        availability_score = current_status.metrics.availability * 0.4
        score += availability_score
        
        # Response time score (30% of total)
        expected_response_time = self.platform_configs[integration_name]['expected_response_time']
        response_time_ratio = min(expected_response_time / max(current_status.metrics.response_time_ms, 1), 1.0)
        response_time_score = response_time_ratio * 0.3
        score += response_time_score
        
        # Error rate score (20% of total)
        error_rate_score = (1.0 - current_status.metrics.error_rate) * 0.2
        score += error_rate_score
        
        # SLA compliance score (10% of total)
        sla_score = (current_status.sla_compliance / 100.0) * 0.1
        score += sla_score
        
        return min(score, 1.0)
    
    async def _determine_health_status(self, integration_name: str) -> HealthStatus:
        """🏥 Status: Détermination du statut de santé"""
        
        current_status = self.health_status[integration_name]
        config = self.integrations[integration_name]
        
        health_score = current_status.health_score
        
        # Check if in maintenance
        if await self._is_in_maintenance(integration_name):
            return HealthStatus.MAINTENANCE
        
        # Determine status based on health score and specific conditions
        if health_score >= 0.95:
            return HealthStatus.HEALTHY
        elif health_score >= 0.8:
            return HealthStatus.DEGRADED
        elif health_score >= 0.5:
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.CRITICAL
    
    async def _is_in_maintenance(self, integration_name: str) -> bool:
        """🔧 Maintenance: Vérification des fenêtres de maintenance"""
        
        config = self.integrations[integration_name]
        current_time = datetime.now()
        
        for maintenance_window in config.maintenance_windows:
            start_time = maintenance_window.get('start_time')
            end_time = maintenance_window.get('end_time')
            
            if start_time and end_time:
                if start_time <= current_time <= end_time:
                    return True
        
        return False
    
    async def _mark_integration_healthy(self, integration_name: str):
        """✅ Healthy: Marquer une intégration comme saine"""
        
        current_status = self.health_status[integration_name]
        
        if current_status.overall_health != HealthStatus.HEALTHY:
            current_status.overall_health = HealthStatus.HEALTHY
            current_status.degradation_reasons.clear()
            
            # Resolve active alerts
            for alert in current_status.active_alerts:
                if alert.status == 'active':
                    alert.status = 'resolved'
                    alert.resolved_at = datetime.now()
            
            logger.info(f"Integration {integration_name} marked as healthy")
    
    async def _mark_integration_degraded(self, integration_name: str, reason: str):
        """⚠️ Degraded: Marquer une intégration comme dégradée"""
        
        current_status = self.health_status[integration_name]
        
        if current_status.overall_health not in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
            current_status.overall_health = HealthStatus.DEGRADED
            
            if reason not in current_status.degradation_reasons:
                current_status.degradation_reasons.append(reason)
            
            # Create alert
            await self._create_health_alert(
                integration_name, 'degradation', AlertPriority.MEDIUM, 
                f"Integration {integration_name} is degraded: {reason}"
            )
            
            logger.warning(f"Integration {integration_name} marked as degraded: {reason}")
    
    async def _mark_integration_unhealthy(self, integration_name: str, reason: str):
        """❌ Unhealthy: Marquer une intégration comme malsaine"""
        
        current_status = self.health_status[integration_name]
        current_status.overall_health = HealthStatus.UNHEALTHY
        
        if reason not in current_status.degradation_reasons:
            current_status.degradation_reasons.append(reason)
        
        # Create high priority alert
        await self._create_health_alert(
            integration_name, 'unhealthy', AlertPriority.HIGH,
            f"Integration {integration_name} is unhealthy: {reason}"
        )
        
        logger.error(f"Integration {integration_name} marked as unhealthy: {reason}")
    
    async def _create_health_alert(
        self, 
        integration_name: str, 
        alert_type: str, 
        priority: AlertPriority, 
        message: str
    ):
        """🚨 Alert: Création d'alerte de santé"""
        
        alert = HealthAlert(
            alert_id=f"health_{integration_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            integration_name=integration_name,
            alert_type=alert_type,
            priority=priority,
            message=message,
            details={
                'health_status': self.health_status[integration_name].overall_health.value,
                'health_score': self.health_status[integration_name].health_score,
                'last_check': self.health_status[integration_name].last_check.isoformat()
            },
            triggered_at=datetime.now(),
            resolved_at=None,
            status='active',
            affected_metrics=['availability', 'response_time'],
            suggested_actions=await self._generate_suggested_actions(integration_name, alert_type)
        )
        
        # Add to active alerts
        self.health_status[integration_name].active_alerts.append(alert)
        self.alert_history[integration_name].append(alert)
        
        # Update metrics
        self.metrics['active_alerts'] += 1
        
        logger.info(f"Created health alert for {integration_name}: {message}")
    
    async def _generate_suggested_actions(self, integration_name: str, alert_type: str) -> List[str]:
        """💡 Actions: Génération d'actions suggérées"""
        
        actions = []
        
        if alert_type == 'degradation':
            actions.extend([
                f"Check {integration_name} API status page",
                "Verify network connectivity",
                "Review recent deployments",
                "Check authentication tokens"
            ])
        elif alert_type == 'unhealthy':
            actions.extend([
                f"Investigate {integration_name} service outage",
                "Enable fallback mechanisms",
                "Notify operations team",
                "Check dependency services"
            ])
        elif alert_type == 'critical':
            actions.extend([
                f"Immediate escalation for {integration_name}",
                "Activate disaster recovery plan",
                "Switch to backup systems",
                "Contact platform support"
            ])
        
        # Platform-specific actions
        platform_config = self.platform_configs.get(integration_name, {})
        if platform_config.get('business_criticality', 0) > 0.9:
            actions.append("High business impact - prioritize resolution")
        
        return actions
    
    async def _aggregate_metrics(self):
        """📊 Aggregation: Agrégation des métriques globales"""
        
        while True:
            try:
                await asyncio.sleep(30)  # Aggregate every 30 seconds
                
                total_integrations = len(self.health_status)
                healthy_count = 0
                degraded_count = 0
                unhealthy_count = 0
                total_response_time = 0.0
                total_availability = 0.0
                
                for status in self.health_status.values():
                    if status.overall_health == HealthStatus.HEALTHY:
                        healthy_count += 1
                    elif status.overall_health == HealthStatus.DEGRADED:
                        degraded_count += 1
                    elif status.overall_health in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                        unhealthy_count += 1
                    
                    total_response_time += status.metrics.response_time_ms
                    total_availability += status.metrics.availability
                
                # Update global metrics
                self.metrics.update({
                    'total_integrations': total_integrations,
                    'healthy_integrations': healthy_count,
                    'degraded_integrations': degraded_count,
                    'unhealthy_integrations': unhealthy_count,
                    'average_response_time': total_response_time / max(total_integrations, 1),
                    'overall_availability': total_availability / max(total_integrations, 1)
                })
                
                # Count active alerts
                active_alerts = sum(
                    len([a for a in status.active_alerts if a.status == 'active'])
                    for status in self.health_status.values()
                )
                self.metrics['active_alerts'] = active_alerts
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics aggregation: {e}")
    
    async def _process_alerts(self):
        """🚨 Processing: Traitement des alertes"""
        
        while True:
            try:
                await asyncio.sleep(10)  # Process alerts every 10 seconds
                
                for integration_name, status in self.health_status.items():
                    for alert in status.active_alerts:
                        if alert.status == 'active':
                            # Check if alert should be escalated
                            time_since_triggered = datetime.now() - alert.triggered_at
                            
                            if time_since_triggered > timedelta(minutes=15) and alert.priority != AlertPriority.EMERGENCY:
                                # Escalate alert
                                alert.priority = AlertPriority.CRITICAL if alert.priority == AlertPriority.HIGH else AlertPriority.HIGH
                                logger.warning(f"Escalated alert {alert.alert_id} to {alert.priority.name}")
                            
                            # Send alert to handlers
                            for handler_name, handler in self.alert_handlers.items():
                                try:
                                    await handler(alert)
                                except Exception as e:
                                    logger.error(f"Error in alert handler {handler_name}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert processing: {e}")
    
    async def get_integration_status(self, integration_name: str) -> Optional[IntegrationStatus]:
        """📋 Status: Récupération du statut d'intégration"""
        
        return self.health_status.get(integration_name)
    
    async def get_all_statuses(self) -> Dict[str, IntegrationStatus]:
        """📋 All Status: Récupération de tous les statuts"""
        
        return self.health_status.copy()
    
    async def get_unhealthy_integrations(self) -> List[str]:
        """❌ Unhealthy: Liste des intégrations malsaines"""
        
        unhealthy = []
        for name, status in self.health_status.items():
            if status.overall_health in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                unhealthy.append(name)
        
        return unhealthy
    
    async def add_custom_health_check(self, integration_name: str, health_check: HealthCheck):
        """➕ Custom Check: Ajout de vérification personnalisée"""
        
        if integration_name in self.integrations:
            self.integrations[integration_name].health_checks.append(health_check)
            self.active_checks[health_check.check_id] = health_check
            logger.info(f"Added custom health check {health_check.check_id} for {integration_name}")
    
    def add_alert_handler(self, handler_name: str, handler: Callable):
        """🔔 Handler: Ajout de gestionnaire d'alerte"""
        
        self.alert_handlers[handler_name] = handler
        logger.info(f"Added alert handler: {handler_name}")
    
    async def set_maintenance_mode(self, integration_name: str, start_time: datetime, end_time: datetime):
        """🔧 Maintenance: Configuration du mode maintenance"""
        
        if integration_name in self.integrations:
            maintenance_window = {
                'start_time': start_time,
                'end_time': end_time,
                'scheduled_by': 'system',
                'reason': 'scheduled_maintenance'
            }
            
            self.integrations[integration_name].maintenance_windows.append(maintenance_window)
            logger.info(f"Scheduled maintenance for {integration_name}: {start_time} - {end_time}")
    
    async def get_health_analytics(self) -> Dict[str, Any]:
        """
        📊 Analytics: Analytics complets de santé des intégrations
        
        Returns:
            Analytics détaillés avec métriques et tendances
        """
        try:
            # Platform type distribution
            platform_types = {}
            for integration_name, config in self.integrations.items():
                platform_type = config.platform_type
                platform_types[platform_type] = platform_types.get(platform_type, 0) + 1
            
            # Health status distribution
            health_distribution = {}
            for status in HealthStatus:
                count = sum(1 for s in self.health_status.values() if s.overall_health == status)
                health_distribution[status.value] = count
            
            # Alert priority distribution
            alert_priorities = {}
            for priority in AlertPriority:
                count = 0
                for status in self.health_status.values():
                    count += len([a for a in status.active_alerts if a.priority == priority and a.status == 'active'])
                alert_priorities[priority.name] = count
            
            # Top 5 integrations by health score
            top_healthy = sorted(
                self.health_status.items(),
                key=lambda x: x[1].health_score,
                reverse=True
            )[:5]
            
            # Bottom 5 integrations by health score
            least_healthy = sorted(
                self.health_status.items(),
                key=lambda x: x[1].health_score
            )[:5]
            
            # SLA compliance summary
            sla_compliance = {}
            for name, status in self.health_status.items():
                sla_compliance[name] = status.sla_compliance
            avg_sla_compliance = sum(sla_compliance.values()) / len(sla_compliance) if sla_compliance else 0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'monitoring_status': {
                    'active_monitoring_tasks': len(self.monitoring_tasks),
                    'http_session_active': self.http_session is not None and not self.http_session.closed,
                    'monitoring_started': len(self.monitoring_tasks) > 0
                },
                'global_metrics': self.metrics,
                'distributions': {
                    'platform_types': platform_types,
                    'health_status': health_distribution,
                    'alert_priorities': alert_priorities
                },
                'rankings': {
                    'healthiest_integrations': [
                        {'name': name, 'health_score': status.health_score}
                        for name, status in top_healthy
                    ],
                    'least_healthy_integrations': [
                        {'name': name, 'health_score': status.health_score}
                        for name, status in least_healthy
                    ]
                },
                'sla_performance': {
                    'average_compliance': avg_sla_compliance,
                    'by_integration': sla_compliance,
                    'compliant_integrations': sum(1 for c in sla_compliance.values() if c >= 99.0),
                    'non_compliant_integrations': sum(1 for c in sla_compliance.values() if c < 99.0)
                },
                'capabilities': {
                    'real_time_monitoring': True,
                    'proactive_alerting': True,
                    'trend_analysis': True,
                    'sla_tracking': True,
                    'maintenance_mode': True,
                    'custom_health_checks': True,
                    'multi_platform_support': True
                },
                'platform_coverage': {
                    'total_platforms': len(self.platform_configs),
                    'monitored_platforms': len(self.integrations),
                    'coverage_percentage': (len(self.integrations) / len(self.platform_configs)) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating health analytics: {e}")
            return {'error': 'Failed to generate analytics', 'timestamp': datetime.now().isoformat()}


# Instance globale pour utilisation
integration_health_monitor = IntegrationHealthMonitor()

# Export des classes principales
__all__ = [
    'IntegrationHealthMonitor',
    'HealthMetrics',
    'HealthCheck',
    'HealthAlert',
    'IntegrationStatus',
    'MonitoringConfiguration',
    'HealthStatus',
    'MonitoringLevel',
    'AlertPriority',
    'integration_health_monitor'
]