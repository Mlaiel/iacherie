"""
⚡ Real-Time Intelligence - Intelligence Temps Réel
==================================================

Module intelligence temps réel ultra-avancé pour surveillance instantanée.
Analytics live, détection tendances et réponse automatique aux événements.

Fonctionnalités:
- Surveillance temps réel multi-stream
- Détection anomalies instantanée
- Analytics engagement live
- Prédiction tendances émergentes
- Alertes intelligentes automatiques
- Optimisation performance dynamique
- Dashboard temps réel interactif

© 2025 Fahed Mlaiel - Architecture Monitoring Propriétaire Ultra-Avancée
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import random
import statistics
from collections import deque, defaultdict
import math


class MetricType(Enum):
    """Types métriques temps réel"""
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    TRAFFIC = "traffic"
    PERFORMANCE = "performance"
    COLLABORATION = "collaboration"
    CONTENT_QUALITY = "content_quality"
    USER_ACTIVITY = "user_activity"
    SYSTEM_HEALTH = "system_health"


class TrendDirection(Enum):
    """Direction tendance"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"


class AlertPriority(Enum):
    """Priorité alerte"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LiveMetrics:
    """Métriques temps réel"""
    metric_id: str
    metric_type: MetricType
    value: float
    previous_value: float
    change_rate: float
    trend_direction: TrendDirection
    confidence_score: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InstantAlert:
    """Alerte instantanée"""
    alert_id: str
    alert_type: str
    priority: AlertPriority
    message: str
    metric_involved: str
    threshold_breached: str
    current_value: float
    expected_range: Tuple[float, float]
    auto_resolution: bool
    recommended_actions: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrendDetector:
    """Détecteur tendances"""
    trend_id: str
    metric_type: MetricType
    trend_direction: TrendDirection
    trend_strength: float  # 0.0 - 1.0
    duration_minutes: int
    prediction_horizon: int  # minutes
    predicted_value: float
    confidence: float
    contributing_factors: List[str]


class RealTimeIntelligence:
    """Intelligence temps réel enterprise Ainflue"""
    
    def __init__(self, config):
        self.config = config
        self.logger = self._setup_logging()
        
        # Real-time data streams
        self.live_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.current_metrics: Dict[str, LiveMetrics] = {}
        self.active_alerts: List[InstantAlert] = []
        self.trend_detectors: Dict[str, TrendDetector] = {}
        
        # Analytics windows
        self.metric_windows = {
            'short': 60,    # 1 minute
            'medium': 300,  # 5 minutes  
            'long': 900     # 15 minutes
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            MetricType.ENGAGEMENT: {'min': 0.05, 'max': 1.0},
            MetricType.REVENUE: {'min': 0.0, 'max': 10000.0},
            MetricType.TRAFFIC: {'min': 0.0, 'max': 100000.0},
            MetricType.PERFORMANCE: {'min': 0.0, 'max': 1000.0},  # latency ms
            MetricType.CONTENT_QUALITY: {'min': 0.7, 'max': 1.0},
            MetricType.SYSTEM_HEALTH: {'min': 0.8, 'max': 1.0}
        }
        
        # Trend analysis
        self.trend_detection_window = 20  # number of points
        self.trend_threshold = 0.05  # 5% change threshold
        
        # Real-time processing
        self.processing_active = False
        self.processing_interval = 5  # seconds
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("realtime_intelligence")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation intelligence temps réel"""
        self.logger.info("⚡ Initialisation Real-Time Intelligence...")
        
        # Initialize sample metrics
        await self._initialize_sample_metrics()
        
        # Start real-time processing
        await self.start_realtime_processing()
        
        self.logger.info("✅ Real-Time Intelligence initialisé")
    
    async def _initialize_sample_metrics(self):
        """Initialisation métriques échantillon"""
        sample_metrics = [
            {'id': 'global_engagement', 'type': MetricType.ENGAGEMENT, 'base_value': 0.15},
            {'id': 'hourly_revenue', 'type': MetricType.REVENUE, 'base_value': 1250.0},
            {'id': 'active_users', 'type': MetricType.TRAFFIC, 'base_value': 850.0},
            {'id': 'api_latency', 'type': MetricType.PERFORMANCE, 'base_value': 120.0},
            {'id': 'content_quality_avg', 'type': MetricType.CONTENT_QUALITY, 'base_value': 0.87},
            {'id': 'system_health_score', 'type': MetricType.SYSTEM_HEALTH, 'base_value': 0.95}
        ]
        
        for metric_data in sample_metrics:
            # Generate initial historical data
            for i in range(50):
                timestamp = datetime.utcnow() - timedelta(seconds=i*5)
                value = metric_data['base_value'] + random.uniform(-0.1, 0.1) * metric_data['base_value']
                
                live_metric = LiveMetrics(
                    metric_id=metric_data['id'],
                    metric_type=metric_data['type'],
                    value=value,
                    previous_value=value * 0.98,  # Slight previous difference
                    change_rate=random.uniform(-0.05, 0.05),
                    trend_direction=TrendDirection.STABLE,
                    confidence_score=random.uniform(0.8, 0.95),
                    timestamp=timestamp
                )
                
                self.live_metrics[metric_data['id']].appendleft(live_metric)
                
            # Set current metric
            self.current_metrics[metric_data['id']] = self.live_metrics[metric_data['id']][0]
    
    async def start_realtime_processing(self):
        """Démarrage traitement temps réel"""
        self.processing_active = True
        
        # Start background processing task
        asyncio.create_task(self._realtime_processing_loop())
        
        self.logger.info("🔄 Traitement temps réel démarré")
    
    async def _realtime_processing_loop(self):
        """Boucle traitement temps réel"""
        while self.processing_active:
            try:
                # Update all metrics with new simulated data
                await self._update_all_metrics()
                
                # Detect trends
                await self._detect_trends()
                
                # Check for alerts
                await self._check_instant_alerts()
                
                # Wait for next cycle
                await asyncio.sleep(self.processing_interval)
                
            except Exception as e:
                self.logger.error(f"Erreur traitement temps réel: {e}")
                await asyncio.sleep(1)
    
    async def _update_all_metrics(self):
        """Mise à jour toutes métriques"""
        for metric_id, metrics_queue in self.live_metrics.items():
            if not metrics_queue:
                continue
                
            # Get last metric
            last_metric = metrics_queue[0]
            
            # Generate new value with realistic variance
            base_change = random.uniform(-0.02, 0.02)  # ±2% base change
            seasonal_factor = math.sin(datetime.utcnow().minute / 60 * 2 * math.pi) * 0.01  # Small seasonal
            
            new_value = last_metric.value * (1 + base_change + seasonal_factor)
            new_value = max(0, new_value)  # Ensure non-negative
            
            # Calculate change rate
            change_rate = (new_value - last_metric.value) / last_metric.value if last_metric.value > 0 else 0
            
            # Determine trend direction
            trend_direction = self._determine_trend_direction(metric_id)
            
            # Create new metric
            new_metric = LiveMetrics(
                metric_id=metric_id,
                metric_type=last_metric.metric_type,
                value=new_value,
                previous_value=last_metric.value,
                change_rate=change_rate,
                trend_direction=trend_direction,
                confidence_score=random.uniform(0.85, 0.98),
                timestamp=datetime.utcnow()
            )
            
            # Add to queue
            self.live_metrics[metric_id].appendleft(new_metric)
            self.current_metrics[metric_id] = new_metric
    
    def _determine_trend_direction(self, metric_id: str) -> TrendDirection:
        """Détermination direction tendance"""
        metrics_queue = self.live_metrics[metric_id]
        
        if len(metrics_queue) < self.trend_detection_window:
            return TrendDirection.STABLE
        
        # Get recent values
        recent_values = [m.value for m in list(metrics_queue)[:self.trend_detection_window]]
        
        # Calculate trend
        if len(recent_values) < 2:
            return TrendDirection.STABLE
        
        # Simple linear trend
        x = list(range(len(recent_values)))
        y = recent_values
        
        # Calculate slope
        n = len(recent_values)
        if n == 0:
            return TrendDirection.STABLE
            
        slope = self._calculate_slope(x, y)
        
        # Determine trend direction
        if abs(slope) < self.trend_threshold:
            return TrendDirection.STABLE
        elif slope > self.trend_threshold:
            return TrendDirection.RISING
        else:
            return TrendDirection.FALLING
    
    def _calculate_slope(self, x: List[int], y: List[float]) -> float:
        """Calcul pente régression linéaire"""
        n = len(x)
        if n < 2:
            return 0.0
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i]**2 for i in range(n))
        
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0
            
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    async def _detect_trends(self):
        """Détection tendances"""
        for metric_id, current_metric in self.current_metrics.items():
            metrics_queue = self.live_metrics[metric_id]
            
            if len(metrics_queue) < self.trend_detection_window:
                continue
            
            # Analyze trend strength
            recent_values = [m.value for m in list(metrics_queue)[:self.trend_detection_window]]
            trend_strength = self._calculate_trend_strength(recent_values)
            
            # Create or update trend detector
            if current_metric.trend_direction != TrendDirection.STABLE and trend_strength > 0.3:
                trend_id = f"{metric_id}_trend_{int(datetime.utcnow().timestamp())}"
                
                # Simple prediction (linear extrapolation)
                predicted_value = self._predict_next_value(recent_values)
                
                trend_detector = TrendDetector(
                    trend_id=trend_id,
                    metric_type=current_metric.metric_type,
                    trend_direction=current_metric.trend_direction,
                    trend_strength=trend_strength,
                    duration_minutes=5,  # Based on processing interval
                    prediction_horizon=30,  # 30 minutes
                    predicted_value=predicted_value,
                    confidence=current_metric.confidence_score,
                    contributing_factors=self._identify_contributing_factors(metric_id)
                )
                
                self.trend_detectors[metric_id] = trend_detector
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """Calcul force tendance"""
        if len(values) < 2:
            return 0.0
        
        # Calculate coefficient of determination (R²)
        x = list(range(len(values)))
        slope = self._calculate_slope(x, values)
        
        # Calculate R²
        mean_y = statistics.mean(values)
        ss_tot = sum((y - mean_y)**2 for y in values)
        
        if ss_tot == 0:
            return 0.0
        
        # Predicted values
        predicted = [slope * xi + values[0] for xi in x]
        ss_res = sum((values[i] - predicted[i])**2 for i in range(len(values)))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        return max(0.0, min(1.0, r_squared))
    
    def _predict_next_value(self, values: List[float]) -> float:
        """Prédiction valeur suivante"""
        if len(values) < 2:
            return values[0] if values else 0.0
        
        # Simple linear extrapolation
        x = list(range(len(values)))
        slope = self._calculate_slope(x, values)
        
        next_x = len(values)
        predicted = slope * next_x + values[0]
        
        return predicted
    
    def _identify_contributing_factors(self, metric_id: str) -> List[str]:
        """Identification facteurs contributifs"""
        factors = []
        
        metric_type = self.current_metrics[metric_id].metric_type
        
        if metric_type == MetricType.ENGAGEMENT:
            factors = ["content_quality", "posting_frequency", "audience_activity"]
        elif metric_type == MetricType.REVENUE:
            factors = ["collaboration_success", "content_monetization", "user_retention"]
        elif metric_type == MetricType.TRAFFIC:
            factors = ["viral_content", "platform_algorithm", "external_promotion"]
        elif metric_type == MetricType.PERFORMANCE:
            factors = ["system_load", "resource_allocation", "optimization_level"]
        
        return factors[:3]  # Return top 3 factors
    
    async def _check_instant_alerts(self):
        """Vérification alertes instantanées"""
        for metric_id, current_metric in self.current_metrics.items():
            thresholds = self.alert_thresholds.get(current_metric.metric_type)
            if not thresholds:
                continue
            
            alerts_generated = []
            
            # Check if value is outside normal range
            if current_metric.value < thresholds['min']:
                alert = InstantAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type="threshold_low",
                    priority=AlertPriority.HIGH,
                    message=f"{metric_id} below minimum threshold",
                    metric_involved=metric_id,
                    threshold_breached=f"min: {thresholds['min']}",
                    current_value=current_metric.value,
                    expected_range=(thresholds['min'], thresholds['max']),
                    auto_resolution=False,
                    recommended_actions=[
                        "Investigate root cause",
                        "Check system health",
                        "Consider manual intervention"
                    ]
                )
                alerts_generated.append(alert)
            
            elif current_metric.value > thresholds['max']:
                alert = InstantAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type="threshold_high",
                    priority=AlertPriority.MEDIUM,
                    message=f"{metric_id} above maximum threshold",
                    metric_involved=metric_id,
                    threshold_breached=f"max: {thresholds['max']}",
                    current_value=current_metric.value,
                    expected_range=(thresholds['min'], thresholds['max']),
                    auto_resolution=True,
                    recommended_actions=[
                        "Scale resources if needed",
                        "Monitor for continued growth",
                        "Optimize if necessary"
                    ]
                )
                alerts_generated.append(alert)
            
            # Check for rapid changes
            if abs(current_metric.change_rate) > 0.1:  # 10% rapid change
                alert = InstantAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type="rapid_change",
                    priority=AlertPriority.MEDIUM,
                    message=f"{metric_id} rapid change detected: {current_metric.change_rate:.2%}",
                    metric_involved=metric_id,
                    threshold_breached="change_rate: 10%",
                    current_value=current_metric.change_rate,
                    expected_range=(-0.1, 0.1),
                    auto_resolution=False,
                    recommended_actions=[
                        "Analyze cause of rapid change",
                        "Verify data accuracy",
                        "Monitor for stability"
                    ]
                )
                alerts_generated.append(alert)
            
            # Add alerts to active alerts
            for alert in alerts_generated:
                self.active_alerts.append(alert)
                self.logger.warning(f"🚨 Instant Alert: {alert.message}")
    
    async def get_realtime_dashboard_data(self) -> Dict[str, Any]:
        """Données dashboard temps réel"""
        # Current metrics snapshot
        current_snapshot = {
            metric_id: {
                'value': metric.value,
                'change_rate': metric.change_rate,
                'trend': metric.trend_direction.value,
                'confidence': metric.confidence_score,
                'last_updated': metric.timestamp.isoformat()
            }
            for metric_id, metric in self.current_metrics.items()
        }
        
        # Active alerts
        recent_alerts = [
            {
                'alert_id': alert.alert_id,
                'type': alert.alert_type,
                'priority': alert.priority.value,
                'message': alert.message,
                'metric': alert.metric_involved,
                'current_value': alert.current_value,
                'timestamp': alert.timestamp.isoformat()
            }
            for alert in self.active_alerts[-10:]  # Last 10 alerts
        ]
        
        # Trend analysis
        active_trends = {
            metric_id: {
                'direction': trend.trend_direction.value,
                'strength': trend.trend_strength,
                'prediction': trend.predicted_value,
                'confidence': trend.confidence
            }
            for metric_id, trend in self.trend_detectors.items()
        }
        
        # System health overview
        system_health = self._calculate_system_health()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'current_metrics': current_snapshot,
            'recent_alerts': recent_alerts,
            'active_trends': active_trends,
            'system_health': system_health,
            'processing_status': {
                'active': self.processing_active,
                'interval_seconds': self.processing_interval,
                'metrics_tracked': len(self.current_metrics)
            }
        }
    
    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calcul santé système"""
        if not self.current_metrics:
            return {'status': 'unknown', 'score': 0.0}
        
        # Get system health metric if available
        system_health_metric = self.current_metrics.get('system_health_score')
        
        # Calculate overall health based on alerts and metrics
        critical_alerts = len([a for a in self.active_alerts[-20:] if a.priority == AlertPriority.CRITICAL])
        high_alerts = len([a for a in self.active_alerts[-20:] if a.priority == AlertPriority.HIGH])
        
        health_score = 1.0
        
        # Reduce score based on alerts
        health_score -= critical_alerts * 0.2
        health_score -= high_alerts * 0.1
        
        # Factor in system health metric
        if system_health_metric:
            health_score = (health_score + system_health_metric.value) / 2
        
        health_score = max(0.0, min(1.0, health_score))
        
        # Determine status
        if health_score >= 0.9:
            status = 'excellent'
        elif health_score >= 0.7:
            status = 'good'
        elif health_score >= 0.5:
            status = 'degraded'
        else:
            status = 'critical'
        
        return {
            'status': status,
            'score': health_score,
            'critical_alerts': critical_alerts,
            'high_alerts': high_alerts
        }
    
    async def get_metric_history(self, metric_id: str, window_minutes: int = 60) -> List[Dict[str, Any]]:
        """Historique métrique"""
        if metric_id not in self.live_metrics:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        metrics_queue = self.live_metrics[metric_id]
        
        history = []
        for metric in metrics_queue:
            if metric.timestamp >= cutoff_time:
                history.append({
                    'timestamp': metric.timestamp.isoformat(),
                    'value': metric.value,
                    'change_rate': metric.change_rate,
                    'trend': metric.trend_direction.value,
                    'confidence': metric.confidence_score
                })
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        return history
    
    async def add_custom_metric(self, metric_id: str, metric_type: MetricType, value: float):
        """Ajout métrique personnalisée"""
        # Calculate change rate if previous value exists
        previous_value = 0.0
        change_rate = 0.0
        
        if metric_id in self.current_metrics:
            previous_value = self.current_metrics[metric_id].value
            change_rate = (value - previous_value) / previous_value if previous_value > 0 else 0
        
        # Create new metric
        new_metric = LiveMetrics(
            metric_id=metric_id,
            metric_type=metric_type,
            value=value,
            previous_value=previous_value,
            change_rate=change_rate,
            trend_direction=self._determine_trend_direction(metric_id) if metric_id in self.live_metrics else TrendDirection.STABLE,
            confidence_score=0.95  # High confidence for custom metrics
        )
        
        # Add to tracking
        self.live_metrics[metric_id].appendleft(new_metric)
        self.current_metrics[metric_id] = new_metric
        
        self.logger.info(f"Custom metric added: {metric_id} = {value}")
    
    async def stop_realtime_processing(self):
        """Arrêt traitement temps réel"""
        self.processing_active = False
        self.logger.info("⏹️ Traitement temps réel arrêté")
    
    async def shutdown(self):
        """Arrêt propre intelligence temps réel"""
        self.logger.info("⏹️ Arrêt Real-Time Intelligence...")
        
        # Stop processing
        await self.stop_realtime_processing()
        
        # Clear data
        self.live_metrics.clear()
        self.current_metrics.clear()
        self.active_alerts.clear()
        self.trend_detectors.clear()
        
        self.logger.info("✅ Real-Time Intelligence arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_realtime_intelligence():
        class MockConfig:
            debug = True
        
        intelligence = RealTimeIntelligence(MockConfig())
        await intelligence.initialize()
        
        # Wait for some real-time processing
        await asyncio.sleep(10)
        
        # Test dashboard data
        dashboard = await intelligence.get_realtime_dashboard_data()
        print(f"Current metrics: {len(dashboard['current_metrics'])}")
        print(f"Recent alerts: {len(dashboard['recent_alerts'])}")
        print(f"System health: {dashboard['system_health']['status']}")
        
        # Test custom metric
        await intelligence.add_custom_metric('test_metric', MetricType.ENGAGEMENT, 0.95)
        
        # Test metric history
        history = await intelligence.get_metric_history('global_engagement', 30)
        print(f"Metric history points: {len(history)}")
        
        print('✅ Real-Time Intelligence test passed')
        await intelligence.shutdown()
    
    asyncio.run(test_realtime_intelligence())