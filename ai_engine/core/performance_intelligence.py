"""Performance Intelligence & Auto-Optimization Module

Advanced AI system for real-time performance monitoring, intelligent optimization,
and autonomous content strategy refinement for maximum ROI and engagement.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This revolutionary performance intelligence system represents proprietary AI technology.
Unauthorized copying, reverse engineering, or use will result in immediate prosecution.

Business Logic: Performance Monitoring → Pattern Recognition → Intelligent Analysis → Auto-Optimization → Strategy Refinement → Continuous Learning
"""import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, deque
import math
import statistics
import numpy as np

# ML and optimization libraries
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    import scipy.optimize as optimize
    from scipy import stats
    ML_OPTIMIZATION_AVAILABLE = True
except ImportError:
    ML_OPTIMIZATION_AVAILABLE = False

# Time series analysis
try:
    import pandas as pd
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    TIME_SERIES_AVAILABLE = True
except ImportError:
    TIME_SERIES_AVAILABLE = False

from .exceptions import OptimizationError, ConfigurationError
from .metrics import metrics_collector
from .performance import performance_monitor
from .content_types import ContentType
from .multi_platform_intelligence import Platform, OptimizationStrategy

logger = logging.getLogger(__name__)


class PerformanceMetricType(Enum):
    """Types of performance metrics"""    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    SHARES = "shares"
    SAVES = "saves"
    COMMENTS = "comments"
    LIKES = "likes"
    CONVERSION_RATE = "conversion_rate"
    ROI = "roi"
    CPMD = "cost_per_mille"
    CTR = "click_through_rate"
    BOUNCE_RATE = "bounce_rate"
    TIME_SPENT = "time_spent"
    FOLLOWER_GROWTH = "follower_growth"
    BRAND_MENTION = "brand_mention"
    SENTIMENT_SCORE = "sentiment_score"
    VIDEO_COMPLETION_RATE = "video_completion_rate"
    AUDIENCE_RETENTION = "audience_retention"


class OptimizationDirection(Enum):
    """Direction of optimization"""    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    STABILIZE = "stabilize"
    TARGET = "target"


class AlertSeverity(Enum):
    """Alert severity levels"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AutoOptimizationAction(Enum):
    """Types of automatic optimization actions"""    ADJUST_POSTING_TIME = "adjust_posting_time"
    MODIFY_HASHTAGS = "modify_hashtags"
    CHANGE_CONTENT_FORMAT = "change_content_format"
    UPDATE_CAPTIONS = "update_captions"
    REALLOCATE_BUDGET = "reallocate_budget"
    PAUSE_UNDERPERFORMING = "pause_underperforming"
    AMPLIFY_HIGH_PERFORMING = "amplify_high_performing"
    ADJUST_TARGET_AUDIENCE = "adjust_target_audience"
    MODIFY_POSTING_FREQUENCY = "modify_posting_frequency"
    UPDATE_CREATIVE_ELEMENTS = "update_creative_elements"


@dataclass
class PerformanceMetric:
    """Individual performance metric data point"""    metric_id: str
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    platform: Optional[Platform] = None
    content_id: Optional[str] = None
    campaign_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "platform": self.platform.value if self.platform else None,
            "content_id": self.content_id,
            "campaign_id": self.campaign_id,
            "metadata": self.metadata,
            "confidence": self.confidence
        }


@dataclass
class PerformanceAlert:
    """Performance alert for anomalies or thresholds"""    alert_id: str
    severity: AlertSeverity
    metric_type: PerformanceMetricType
    alert_type: str
    message: str
    current_value: float
    expected_range: Tuple[float, float]
    platform: Optional[Platform] = None
    content_id: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)
    auto_resolved: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "metric_type": self.metric_type.value,
            "alert_type": self.alert_type,
            "message": self.message,
            "current_value": self.current_value,
            "expected_range": list(self.expected_range),
            "platform": self.platform.value if self.platform else None,
            "content_id": self.content_id,
            "suggested_actions": self.suggested_actions,
            "auto_resolved": self.auto_resolved,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


@dataclass
class OptimizationRecommendation:
    """AI-generated optimization recommendation"""    recommendation_id: str
    action_type: AutoOptimizationAction
    target_metric: PerformanceMetricType
    expected_improvement: float
    confidence: float
    priority: str
    description: str
    implementation_details: Dict[str, Any]
    estimated_impact: Dict[str, float]
    resource_requirements: Dict[str, Any]
    risk_assessment: Dict[str, float]
    A_B_test_candidate: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "action_type": self.action_type.value,
            "target_metric": self.target_metric.value,
            "expected_improvement": self.expected_improvement,
            "confidence": self.confidence,
            "priority": self.priority,
            "description": self.description,
            "implementation_details": self.implementation_details,
            "estimated_impact": self.estimated_impact,
            "resource_requirements": self.resource_requirements,
            "risk_assessment": self.risk_assessment,
            "A_B_test_candidate": self.A_B_test_candidate,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }


@dataclass
class AutoOptimizationResult:
    """Result of automatic optimization action"""    optimization_id: str
    action_taken: AutoOptimizationAction
    target_metrics: List[PerformanceMetricType]
    before_values: Dict[str, float]
    after_values: Dict[str, float] = field(default_factory=dict)
    improvement_achieved: Dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.0
    side_effects: List[str] = field(default_factory=list)
    rollback_available: bool = True
    execution_time: datetime = field(default_factory=datetime.utcnow)
    monitoring_period: timedelta = field(default=timedelta(hours=24))
    status: str = "executed"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "optimization_id": self.optimization_id,
            "action_taken": self.action_taken.value,
            "target_metrics": [m.value for m in self.target_metrics],
            "before_values": self.before_values,
            "after_values": self.after_values,
            "improvement_achieved": self.improvement_achieved,
            "success_rate": self.success_rate,
            "side_effects": self.side_effects,
            "rollback_available": self.rollback_available,
            "execution_time": self.execution_time.isoformat(),
            "monitoring_period_hours": self.monitoring_period.total_seconds() / 3600,
            "status": self.status
        }


@dataclass
class PerformanceInsight:
    """AI-generated performance insight"""    insight_id: str
    insight_type: str
    title: str
    description: str
    significance_score: float
    supporting_data: Dict[str, Any]
    actionable_recommendations: List[str]
    related_metrics: List[PerformanceMetricType]
    platforms_affected: List[Platform]
    time_relevance: str  # "immediate", "short_term", "long_term"
    confidence_level: float
    business_impact: str  # "high", "medium", "low"
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "insight_type": self.insight_type,
            "title": self.title,
            "description": self.description,
            "significance_score": self.significance_score,
            "supporting_data": self.supporting_data,
            "actionable_recommendations": self.actionable_recommendations,
            "related_metrics": [m.value for m in self.related_metrics],
            "platforms_affected": [p.value for p in self.platforms_affected],
            "time_relevance": self.time_relevance,
            "confidence_level": self.confidence_level,
            "business_impact": self.business_impact,
            "created_at": self.created_at.isoformat()
        }


class RealTimePerformanceMonitor:
    """Real-time performance monitoring and analysis system"""    
    def __init__(self):
        self.metrics_buffer = deque(maxlen=10000)  # Keep last 10k metrics
        self.alerts_active = {}
        self.baseline_metrics = {}
        self.anomaly_detectors = {}
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize anomaly detection models"""        if ML_OPTIMIZATION_AVAILABLE:
            try:
                for metric_type in PerformanceMetricType:
                    self.anomaly_detectors[metric_type] = IsolationForest(
                        contamination=0.1,
                        random_state=42
                    )
                logger.info("Anomaly detectors initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize anomaly detectors: {e}")
    
    async def ingest_metric(self, metric: PerformanceMetric):
        """Ingest new performance metric"""        try:
            # Add to buffer
            self.metrics_buffer.append(metric)
            
            # Update baseline if needed
            await self._update_baseline(metric)
            
            # Check for anomalies
            anomalies = await self._detect_anomalies(metric)
            
            # Generate alerts if needed
            for anomaly in anomalies:
                await self._generate_alert(anomaly, metric)
            
            # Update anomaly detector
            await self._update_anomaly_detector(metric)
            
            # Log metric ingestion
            logger.debug(f"Ingested metric: {metric.metric_type.value} = {metric.value}")
            
        except Exception as e:
            logger.error(f"Metric ingestion failed: {e}")
    
    async def _update_baseline(self, metric: PerformanceMetric):
        """Update baseline metrics for comparison"""        try:
            key = (metric.metric_type, metric.platform, metric.content_id)
            
            if key not in self.baseline_metrics:
                self.baseline_metrics[key] = {
                    "values": deque(maxlen=100),
                    "mean": 0.0,
                    "std": 0.0,
                    "min": float('inf'),
                    "max": float('-inf'),
                    "last_updated": datetime.utcnow()
                }
            
            baseline = self.baseline_metrics[key]
            baseline["values"].append(metric.value)
            
            # Recalculate statistics
            values = list(baseline["values"])
            if len(values) > 1:
                baseline["mean"] = statistics.mean(values)
                baseline["std"] = statistics.stdev(values) if len(values) > 1 else 0.0
                baseline["min"] = min(values)
                baseline["max"] = max(values)
            else:
                baseline["mean"] = values[0]
                baseline["std"] = 0.0
                baseline["min"] = values[0]
                baseline["max"] = values[0]
            
            baseline["last_updated"] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Baseline update failed: {e}")
    
    async def _detect_anomalies(self, metric: PerformanceMetric) -> List[Dict[str, Any]]:
        """Detect anomalies in incoming metrics"""        anomalies = []
        
        try:
            key = (metric.metric_type, metric.platform, metric.content_id)
            baseline = self.baseline_metrics.get(key)
            
            if not baseline or len(baseline["values"]) < 5:
                return anomalies  # Need more data
            
            # Statistical anomaly detection
            z_score = 0
            if baseline["std"] > 0:
                z_score = abs(metric.value - baseline["mean"]) / baseline["std"]
            
            # Z-score threshold anomaly
            if z_score > 2.5:  # 2.5 standard deviations
                anomalies.append({
                    "type": "statistical_outlier",
                    "severity": AlertSeverity.HIGH if z_score > 3 else AlertSeverity.MEDIUM,
                    "z_score": z_score,
                    "baseline_mean": baseline["mean"],
                    "baseline_std": baseline["std"]
                })
            
            # Range-based anomaly
            if metric.value < baseline["min"] * 0.5 or metric.value > baseline["max"] * 2:
                anomalies.append({
                    "type": "range_anomaly",
                    "severity": AlertSeverity.CRITICAL,
                    "expected_range": (baseline["min"], baseline["max"])
                })
            
            # ML-based anomaly detection
            if (ML_OPTIMIZATION_AVAILABLE and 
                metric.metric_type in self.anomaly_detectors and
                len(baseline["values"]) >= 10):
                
                detector = self.anomaly_detectors[metric.metric_type]
                values_array = np.array(list(baseline["values"])).reshape(-1, 1)
                
                try:
                    # Fit if not fitted
                    if not hasattr(detector, 'offset_'):
                        detector.fit(values_array)
                    
                    # Predict anomaly
                    prediction = detector.predict([[metric.value]])
                    if prediction[0] == -1:  # Anomaly detected
                        anomaly_score = detector.decision_function([[metric.value]])[0]
                        anomalies.append({
                            "type": "ml_anomaly",
                            "severity": AlertSeverity.MEDIUM,
                            "anomaly_score": anomaly_score
                        })
                except Exception as e:
                    logger.warning(f"ML anomaly detection failed: {e}")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    async def _generate_alert(self, anomaly: Dict[str, Any], metric: PerformanceMetric):
        """Generate performance alert for anomaly"""        try:
            alert_id = str(uuid.uuid4())
            
            # Determine alert message
            if anomaly["type"] == "statistical_outlier":
                message = f"{metric.metric_type.value} value {metric.value:.2f} is {anomaly['z_score']:.1f} standard deviations from normal"
            elif anomaly["type"] == "range_anomaly":
                message = f"{metric.metric_type.value} value {metric.value:.2f} is outside expected range"
            elif anomaly["type"] == "ml_anomaly":
                message = f"ML model detected anomaly in {metric.metric_type.value}"
            else:
                message = f"Anomaly detected in {metric.metric_type.value}"
            
            # Generate suggested actions
            suggested_actions = self._generate_alert_actions(metric.metric_type, anomaly)
            
            # Create alert
            alert = PerformanceAlert(
                alert_id=alert_id,
                severity=anomaly["severity"],
                metric_type=metric.metric_type,
                alert_type=anomaly["type"],
                message=message,
                current_value=metric.value,
                expected_range=anomaly.get("expected_range", (0, 0)),
                platform=metric.platform,
                content_id=metric.content_id,
                suggested_actions=suggested_actions
            )
            
            # Store alert
            self.alerts_active[alert_id] = alert
            
            # Log alert
            logger.warning(f"Performance alert generated: {message}")
            
        except Exception as e:
            logger.error(f"Alert generation failed: {e}")
    
    def _generate_alert_actions(self, 
                              metric_type: PerformanceMetricType,
                              anomaly: Dict[str, Any]) -> List[str]:
        """Generate suggested actions for alert"""        actions = []
        
        try:
            if metric_type == PerformanceMetricType.ENGAGEMENT_RATE:
                actions.extend([
                    "Review content quality and relevance",
                    "Analyze audience demographics",
                    "Check posting times optimization",
                    "Review hashtag strategy"
                ])
            
            elif metric_type == PerformanceMetricType.REACH:
                actions.extend([
                    "Increase posting frequency",
                    "Optimize hashtag usage",
                    "Consider paid promotion",
                    "Cross-promote on other platforms"
                ])
            
            elif metric_type == PerformanceMetricType.CONVERSION_RATE:
                actions.extend([
                    "Review call-to-action effectiveness",
                    "Analyze landing page performance",
                    "Check audience targeting",
                    "Test different creative formats"
                ])
            
            elif metric_type == PerformanceMetricType.ROI:
                actions.extend([
                    "Review budget allocation",
                    "Pause underperforming campaigns",
                    "Increase budget for top performers",
                    "Optimize audience targeting"
                ])
            
            # Add severity-specific actions
            if anomaly["severity"] == AlertSeverity.CRITICAL:
                actions.insert(0, "Immediate attention required - investigate urgently")
            elif anomaly["severity"] == AlertSeverity.HIGH:
                actions.insert(0, "High priority - review within 2 hours")
            
            return actions[:5]  # Return top 5 actions
            
        except Exception as e:
            logger.error(f"Alert actions generation failed: {e}")
            return ["Review metric performance manually"]
    
    async def _update_anomaly_detector(self, metric: PerformanceMetric):
        """Update ML anomaly detector with new data"""        try:
            if not ML_OPTIMIZATION_AVAILABLE:
                return
            
            key = (metric.metric_type, metric.platform, metric.content_id)
            baseline = self.baseline_metrics.get(key)
            
            if baseline and len(baseline["values"]) >= 20:  # Need sufficient data
                detector = self.anomaly_detectors.get(metric.metric_type)
                if detector:
                    values_array = np.array(list(baseline["values"])).reshape(-1, 1)
                    detector.fit(values_array)
            
        except Exception as e:
            logger.warning(f"Anomaly detector update failed: {e}")
    
    async def get_active_alerts(self, 
                              severity_filter: Optional[AlertSeverity] = None,
                              platform_filter: Optional[Platform] = None) -> List[PerformanceAlert]:
        """Get active performance alerts"""        try:
            alerts = list(self.alerts_active.values())
            
            # Apply filters
            if severity_filter:
                alerts = [a for a in alerts if a.severity == severity_filter]
            
            if platform_filter:
                alerts = [a for a in alerts if a.platform == platform_filter]
            
            # Sort by severity and creation time
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.HIGH: 1,
                AlertSeverity.MEDIUM: 2,
                AlertSeverity.LOW: 3,
                AlertSeverity.INFO: 4
            }
            
            alerts.sort(key=lambda x: (severity_order[x.severity], x.created_at), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def resolve_alert(self, alert_id: str, auto_resolved: bool = False):
        """Resolve a performance alert"""        try:
            if alert_id in self.alerts_active:
                alert = self.alerts_active[alert_id]
                alert.resolved_at = datetime.utcnow()
                alert.auto_resolved = auto_resolved
                
                # Remove from active alerts
                del self.alerts_active[alert_id]
                
                logger.info(f"Alert {alert_id} resolved")
            
        except Exception as e:
            logger.error(f"Alert resolution failed: {e}")


class IntelligentOptimizationEngine:
    """Intelligent optimization engine with ML-powered recommendations"""    
    def __init__(self):
        self.optimization_history = deque(maxlen=1000)
        self.success_patterns = {}
        self.A_B_tests = {}
        self.optimization_models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize optimization models"""        if ML_OPTIMIZATION_AVAILABLE:
            try:
                # Different models for different optimization types
                for action in AutoOptimizationAction:
                    self.optimization_models[action] = RandomForestRegressor(
                        n_estimators=100,
                        random_state=42
                    )
                logger.info("Optimization models initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize optimization models: {e}")
    
    async def generate_optimization_recommendations(self, 
                                                  metrics_data: List[PerformanceMetric],
                                                  target_improvements: Dict[PerformanceMetricType, float],
                                                  constraints: Dict[str, Any] = None) -> List[OptimizationRecommendation]:
        """Generate intelligent optimization recommendations"""        try:
            constraints = constraints or {}
            recommendations = []
            
            # Analyze current performance
            performance_analysis = await self._analyze_current_performance(metrics_data)
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(
                performance_analysis, target_improvements
            )
            
            # Generate recommendations for each opportunity
            for opportunity in opportunities:
                recommendation = await self._create_optimization_recommendation(
                    opportunity, performance_analysis, constraints
                )
                if recommendation:
                    recommendations.append(recommendation)
            
            # Rank recommendations by impact and feasibility
            recommendations = self._rank_recommendations(recommendations)
            
            return recommendations[:10]  # Return top 10 recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendations generation failed: {e}")
            return []
    
    async def _analyze_current_performance(self, 
                                         metrics_data: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analyze current performance patterns"""        try:
            analysis = {
                "metric_trends": {},
                "platform_performance": {},
                "content_performance": {},
                "time_patterns": {},
                "correlation_patterns": {}
            }
            
            # Group metrics by type, platform, content
            metrics_by_type = defaultdict(list)
            metrics_by_platform = defaultdict(list)
            metrics_by_content = defaultdict(list)
            
            for metric in metrics_data:
                metrics_by_type[metric.metric_type].append(metric)
                if metric.platform:
                    metrics_by_platform[metric.platform].append(metric)
                if metric.content_id:
                    metrics_by_content[metric.content_id].append(metric)
            
            # Analyze trends for each metric type
            for metric_type, metrics in metrics_by_type.items():
                if len(metrics) >= 5:
                    values = [m.value for m in sorted(metrics, key=lambda x: x.timestamp)]
                    trend = self._calculate_trend(values)
                    analysis["metric_trends"][metric_type] = trend
            
            # Analyze platform performance
            for platform, metrics in metrics_by_platform.items():
                platform_stats = self._calculate_performance_stats(metrics)
                analysis["platform_performance"][platform] = platform_stats
            
            # Analyze content performance
            for content_id, metrics in metrics_by_content.items():
                content_stats = self._calculate_performance_stats(metrics)
                analysis["content_performance"][content_id] = content_stats
            
            # Analyze time patterns
            analysis["time_patterns"] = self._analyze_time_patterns(metrics_data)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {}
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, float]:
        """Calculate trend statistics for values"""        try:
            if len(values) < 2:
                return {"slope": 0, "r_squared": 0, "direction": "stable"}
            
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Determine trend direction
            if abs(r_value) < 0.3:
                direction = "stable"
            elif slope > 0:
                direction = "rising" if r_value > 0.6 else "slightly_rising"
            else:
                direction = "declining" if r_value < -0.6 else "slightly_declining"
            
            return {
                "slope": slope,
                "r_squared": r_value ** 2,
                "direction": direction,
                "strength": abs(r_value),
                "p_value": p_value
            }
            
        except Exception as e:
            logger.error(f"Trend calculation failed: {e}")
            return {"slope": 0, "r_squared": 0, "direction": "stable"}
    
    def _calculate_performance_stats(self, metrics: List[PerformanceMetric]) -> Dict[str, float]:
        """Calculate performance statistics for metrics"""        try:
            if not metrics:
                return {}
            
            values = [m.value for m in metrics]
            
            return {
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "min": min(values),
                "max": max(values),
                "count": len(values),
                "recent_avg": statistics.mean(values[-5:]) if len(values) >= 5 else statistics.mean(values),
                "improvement": (values[-1] - values[0]) / values[0] if len(values) > 1 and values[0] != 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Performance stats calculation failed: {e}")
            return {}
    
    def _analyze_time_patterns(self, metrics_data: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analyze time-based performance patterns"""        try:
            patterns = {
                "hourly_performance": defaultdict(list),
                "daily_performance": defaultdict(list),
                "weekly_performance": defaultdict(list),
                "best_posting_times": [],
                "seasonal_trends": {}
            }
            
            for metric in metrics_data:
                hour = metric.timestamp.hour
                day = metric.timestamp.strftime("%A")
                week = metric.timestamp.isocalendar()[1]
                
                patterns["hourly_performance"][hour].append(metric.value)
                patterns["daily_performance"][day].append(metric.value)
                patterns["weekly_performance"][week].append(metric.value)
            
            # Find best performing hours
            hour_averages = {}
            for hour, values in patterns["hourly_performance"].items():
                if len(values) >= 3:  # Need sufficient data
                    hour_averages[hour] = statistics.mean(values)
            
            if hour_averages:
                best_hours = sorted(hour_averages.items(), key=lambda x: x[1], reverse=True)[:3]
                patterns["best_posting_times"] = [f"{hour:02d}:00" for hour, _ in best_hours]
            
            return patterns
            
        except Exception as e:
            logger.error(f"Time patterns analysis failed: {e}")
            return {}
    
    async def _identify_optimization_opportunities(self, 
                                                 analysis: Dict[str, Any],
                                                 targets: Dict[PerformanceMetricType, float]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""        opportunities = []
        
        try:
            # Check metric trends for improvement opportunities
            trends = analysis.get("metric_trends", {})
            for metric_type, trend_data in trends.items():
                if metric_type in targets:
                    target_improvement = targets[metric_type]
                    current_trend = trend_data.get("slope", 0)
                    
                    # If not meeting target improvement
                    if current_trend < target_improvement:
                        opportunities.append({
                            "type": "trend_improvement",
                            "metric": metric_type,
                            "current_trend": current_trend,
                            "target_improvement": target_improvement,
                            "gap": target_improvement - current_trend,
                            "priority": "high" if target_improvement - current_trend > 0.5 else "medium"
                        })
            
            # Check platform performance for optimization
            platform_perf = analysis.get("platform_performance", {})
            if len(platform_perf) > 1:
                # Find underperforming platforms
                platform_scores = {}
                for platform, stats in platform_perf.items():
                    platform_scores[platform] = stats.get("recent_avg", 0)
                
                if platform_scores:
                    avg_score = statistics.mean(platform_scores.values())
                    for platform, score in platform_scores.items():
                        if score < avg_score * 0.8:  # 20% below average
                            opportunities.append({
                                "type": "platform_optimization",
                                "platform": platform,
                                "current_score": score,
                                "benchmark": avg_score,
                                "improvement_potential": avg_score - score,
                                "priority": "high" if score < avg_score * 0.6 else "medium"
                            })
            
            # Check time patterns for optimization
            time_patterns = analysis.get("time_patterns", {})
            hourly_perf = time_patterns.get("hourly_performance", {})
            if len(hourly_perf) > 5:
                hour_averages = {h: statistics.mean(v) for h, v in hourly_perf.items() if len(v) >= 3}
                if hour_averages:
                    max_performance = max(hour_averages.values())
                    current_avg = statistics.mean(hour_averages.values())
                    
                    if max_performance > current_avg * 1.2:  # 20% improvement possible
                        opportunities.append({
                            "type": "timing_optimization",
                            "optimization_type": "posting_schedule",
                            "improvement_potential": (max_performance - current_avg) / current_avg,
                            "best_hours": time_patterns.get("best_posting_times", []),
                            "priority": "medium"
                        })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Opportunity identification failed: {e}")
            return []
    
    async def _create_optimization_recommendation(self, 
                                                opportunity: Dict[str, Any],
                                                analysis: Dict[str, Any],
                                                constraints: Dict[str, Any]) -> Optional[OptimizationRecommendation]:
        """Create specific optimization recommendation"""        try:
            rec_id = str(uuid.uuid4())
            
            if opportunity["type"] == "trend_improvement":
                # Trend improvement recommendation
                metric = opportunity["metric"]
                gap = opportunity["gap"]
                
                # Determine best action for this metric
                if metric == PerformanceMetricType.ENGAGEMENT_RATE:
                    action = AutoOptimizationAction.UPDATE_CREATIVE_ELEMENTS
                    description = f"Improve {metric.value} by updating creative elements and content format"
                elif metric == PerformanceMetricType.REACH:
                    action = AutoOptimizationAction.MODIFY_HASHTAGS
                    description = f"Expand reach by optimizing hashtag strategy"
                elif metric == PerformanceMetricType.CONVERSION_RATE:
                    action = AutoOptimizationAction.UPDATE_CAPTIONS
                    description = f"Improve conversion rate through better call-to-action in captions"
                else:
                    action = AutoOptimizationAction.ADJUST_POSTING_TIME
                    description = f"Optimize {metric.value} through better timing"
                
                return OptimizationRecommendation(
                    recommendation_id=rec_id,
                    action_type=action,
                    target_metric=metric,
                    expected_improvement=min(gap * 0.7, 0.5),  # Conservative estimate
                    confidence=0.75,
                    priority=opportunity["priority"],
                    description=description,
                    implementation_details=self._get_implementation_details(action, opportunity, analysis),
                    estimated_impact={"primary_metric": gap * 0.7},
                    resource_requirements=self._get_resource_requirements(action),
                    risk_assessment=self._assess_optimization_risk(action),
                    A_B_test_candidate=True
                )
            
            elif opportunity["type"] == "platform_optimization":
                # Platform-specific optimization
                platform = opportunity["platform"]
                improvement_potential = opportunity["improvement_potential"]
                
                return OptimizationRecommendation(
                    recommendation_id=rec_id,
                    action_type=AutoOptimizationAction.ADJUST_TARGET_AUDIENCE,
                    target_metric=PerformanceMetricType.ENGAGEMENT_RATE,
                    expected_improvement=improvement_potential * 0.6,
                    confidence=0.65,
                    priority=opportunity["priority"],
                    description=f"Optimize {platform.value} performance through audience targeting",
                    implementation_details={
                        "platform": platform.value,
                        "focus_areas": ["audience_demographics", "content_format", "posting_frequency"],
                        "benchmark_platform": "best_performing"
                    },
                    estimated_impact={"engagement_rate": improvement_potential * 0.6},
                    resource_requirements={"time_hours": 4, "complexity": "medium"},
                    risk_assessment={"performance_risk": 0.2, "resource_risk": 0.1},
                    A_B_test_candidate=True
                )
            
            elif opportunity["type"] == "timing_optimization":
                # Timing optimization
                improvement_potential = opportunity["improvement_potential"]
                best_hours = opportunity.get("best_hours", [])
                
                return OptimizationRecommendation(
                    recommendation_id=rec_id,
                    action_type=AutoOptimizationAction.ADJUST_POSTING_TIME,
                    target_metric=PerformanceMetricType.ENGAGEMENT_RATE,
                    expected_improvement=improvement_potential * 0.8,
                    confidence=0.8,
                    priority=opportunity["priority"],
                    description="Optimize posting schedule based on audience activity patterns",
                    implementation_details={
                        "recommended_hours": best_hours,
                        "schedule_type": "dynamic",
                        "frequency": "maintain_current"
                    },
                    estimated_impact={"engagement_rate": improvement_potential * 0.8},
                    resource_requirements={"time_hours": 1, "complexity": "low"},
                    risk_assessment={"performance_risk": 0.1, "resource_risk": 0.05},
                    A_B_test_candidate=False
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Recommendation creation failed: {e}")
            return None
    
    def _get_implementation_details(self, 
                                  action: AutoOptimizationAction,
                                  opportunity: Dict[str, Any],
                                  analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get implementation details for optimization action"""        details = {"action": action.value}
        
        try:
            if action == AutoOptimizationAction.MODIFY_HASHTAGS:
                details.update({
                    "strategy": "expand_reach",
                    "target_hashtags": 15,
                    "include_trending": True,
                    "niche_focus": True
                })
            
            elif action == AutoOptimizationAction.UPDATE_CREATIVE_ELEMENTS:
                details.update({
                    "elements_to_update": ["thumbnails", "captions", "visual_style"],
                    "A_B_test_variants": 2,
                    "focus": "engagement_improvement"
                })
            
            elif action == AutoOptimizationAction.ADJUST_POSTING_TIME:
                best_times = analysis.get("time_patterns", {}).get("best_posting_times", ["14:00", "18:00"])
                details.update({
                    "new_schedule": best_times,
                    "frequency": "maintain",
                    "timezone": "user_local"
                })
            
            elif action == AutoOptimizationAction.UPDATE_CAPTIONS:
                details.update({
                    "focus": "call_to_action",
                    "include_questions": True,
                    "length_optimization": True,
                    "engagement_triggers": True
                })
            
            return details
            
        except Exception as e:
            logger.error(f"Implementation details generation failed: {e}")
            return details
    
    def _get_resource_requirements(self, action: AutoOptimizationAction) -> Dict[str, Any]:
        """Get resource requirements for optimization action"""        requirements = {
            AutoOptimizationAction.ADJUST_POSTING_TIME: {"time_hours": 0.5, "complexity": "low", "automation": True},
            AutoOptimizationAction.MODIFY_HASHTAGS: {"time_hours": 1, "complexity": "low", "automation": True},
            AutoOptimizationAction.UPDATE_CAPTIONS: {"time_hours": 2, "complexity": "medium", "automation": False},
            AutoOptimizationAction.UPDATE_CREATIVE_ELEMENTS: {"time_hours": 4, "complexity": "high", "automation": False},
            AutoOptimizationAction.ADJUST_TARGET_AUDIENCE: {"time_hours": 3, "complexity": "medium", "automation": True},
            AutoOptimizationAction.MODIFY_POSTING_FREQUENCY: {"time_hours": 1, "complexity": "low", "automation": True}
        }
        
        return requirements.get(action, {"time_hours": 2, "complexity": "medium", "automation": False})
    
    def _assess_optimization_risk(self, action: AutoOptimizationAction) -> Dict[str, float]:
        """Assess risk for optimization action"""        risk_profiles = {
            AutoOptimizationAction.ADJUST_POSTING_TIME: {"performance_risk": 0.1, "resource_risk": 0.05},
            AutoOptimizationAction.MODIFY_HASHTAGS: {"performance_risk": 0.15, "resource_risk": 0.1},
            AutoOptimizationAction.UPDATE_CAPTIONS: {"performance_risk": 0.2, "resource_risk": 0.15},
            AutoOptimizationAction.UPDATE_CREATIVE_ELEMENTS: {"performance_risk": 0.3, "resource_risk": 0.25},
            AutoOptimizationAction.ADJUST_TARGET_AUDIENCE: {"performance_risk": 0.25, "resource_risk": 0.2},
            AutoOptimizationAction.MODIFY_POSTING_FREQUENCY: {"performance_risk": 0.2, "resource_risk": 0.1}
        }
        
        return risk_profiles.get(action, {"performance_risk": 0.2, "resource_risk": 0.15})
    
    def _rank_recommendations(self, 
                            recommendations: List[OptimizationRecommendation]) -> List[OptimizationRecommendation]:
        """Rank recommendations by impact and feasibility"""        try:
            def score_recommendation(rec):
                # Impact score (0-1)
                impact_score = rec.expected_improvement * rec.confidence
                
                # Feasibility score (0-1)
                resource_req = rec.resource_requirements
                complexity_penalty = {"low": 0, "medium": 0.1, "high": 0.2}.get(
                    resource_req.get("complexity", "medium"), 0.1
                )
                feasibility_score = 1 - complexity_penalty - rec.risk_assessment.get("performance_risk", 0.2)
                
                # Priority bonus
                priority_bonus = {"high": 0.3, "medium": 0.1, "low": 0}.get(rec.priority, 0)
                
                return impact_score * feasibility_score + priority_bonus
            
            recommendations.sort(key=score_recommendation, reverse=True)
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation ranking failed: {e}")
            return recommendations


class AutoOptimizationExecutor:
    """Executes automatic optimizations based on recommendations"""    
    def __init__(self):
        self.execution_queue = asyncio.Queue()
        self.active_optimizations = {}
        self.execution_history = deque(maxlen=500)
    
    async def execute_optimization(self, 
                                 recommendation: OptimizationRecommendation) -> AutoOptimizationResult:
        """Execute an optimization recommendation"""        try:
            optimization_id = str(uuid.uuid4())
            
            # Create result record
            result = AutoOptimizationResult(
                optimization_id=optimization_id,
                action_taken=recommendation.action_type,
                target_metrics=[recommendation.target_metric],
                before_values={recommendation.target_metric.value: 0.0},  # Will be updated with actual values
                status="executing"
            )
            
            self.active_optimizations[optimization_id] = result
            
            # Execute based on action type
            success = await self._execute_specific_action(
                recommendation.action_type,
                recommendation.implementation_details,
                result
            )
            
            if success:
                result.status = "completed"
                result.success_rate = 0.8  # Initial estimate
                logger.info(f"Optimization {optimization_id} executed successfully")
            else:
                result.status = "failed"
                result.success_rate = 0.0
                logger.error(f"Optimization {optimization_id} failed")
            
            # Add to history
            self.execution_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Optimization execution failed: {e}")
            raise OptimizationError(f"Execution failed: {str(e)}")
    
    async def _execute_specific_action(self, 
                                     action: AutoOptimizationAction,
                                     details: Dict[str, Any],
                                     result: AutoOptimizationResult) -> bool:
        """Execute specific optimization action"""        try:
            if action == AutoOptimizationAction.ADJUST_POSTING_TIME:
                return await self._adjust_posting_schedule(details, result)
            
            elif action == AutoOptimizationAction.MODIFY_HASHTAGS:
                return await self._optimize_hashtags(details, result)
            
            elif action == AutoOptimizationAction.UPDATE_CAPTIONS:
                return await self._update_captions(details, result)
            
            elif action == AutoOptimizationAction.UPDATE_CREATIVE_ELEMENTS:
                return await self._update_creative_elements(details, result)
            
            elif action == AutoOptimizationAction.ADJUST_TARGET_AUDIENCE:
                return await self._adjust_audience_targeting(details, result)
            
            elif action == AutoOptimizationAction.MODIFY_POSTING_FREQUENCY:
                return await self._modify_posting_frequency(details, result)
            
            else:
                logger.warning(f"Unknown optimization action: {action}")
                return False
            
        except Exception as e:
            logger.error(f"Specific action execution failed: {e}")
            return False
    
    async def _adjust_posting_schedule(self, 
                                     details: Dict[str, Any],
                                     result: AutoOptimizationResult) -> bool:
        """Adjust posting schedule optimization"""        try:
            new_schedule = details.get("new_schedule", [])
            
            # Simulate schedule adjustment
            # In real implementation, this would update the scheduling system
            logger.info(f"Adjusting posting schedule to: {new_schedule}")
            
            # Record changes
            result.implementation_details = {
                "old_schedule": ["10:00", "16:00"],  # Mock old schedule
                "new_schedule": new_schedule,
                "change_type": "optimization"
            }
            
            await asyncio.sleep(0.1)  # Simulate processing time
            return True
            
        except Exception as e:
            logger.error(f"Posting schedule adjustment failed: {e}")
            return False
    
    async def _optimize_hashtags(self, 
                               details: Dict[str, Any],
                               result: AutoOptimizationResult) -> bool:
        """Optimize hashtags for content"""        try:
            target_count = details.get("target_hashtags", 15)
            include_trending = details.get("include_trending", True)
            
            # Simulate hashtag optimization
            # In real implementation, this would analyze trending hashtags and optimize
            logger.info(f"Optimizing hashtags: target={target_count}, trending={include_trending}")
            
            result.implementation_details = {
                "old_hashtag_count": 8,
                "new_hashtag_count": target_count,
                "trending_included": include_trending,
                "optimization_method": "ai_analysis"
            }
            
            await asyncio.sleep(0.2)
            return True
            
        except Exception as e:
            logger.error(f"Hashtag optimization failed: {e}")
            return False
    
    async def _update_captions(self, 
                             details: Dict[str, Any],
                             result: AutoOptimizationResult) -> bool:
        """Update captions for better engagement"""        try:
            focus = details.get("focus", "engagement")
            include_questions = details.get("include_questions", True)
            
            # Simulate caption updates
            logger.info(f"Updating captions: focus={focus}, questions={include_questions}")
            
            result.implementation_details = {
                "update_type": "engagement_optimization",
                "focus_area": focus,
                "questions_added": include_questions,
                "cta_enhanced": True
            }
            
            await asyncio.sleep(0.3)
            return True
            
        except Exception as e:
            logger.error(f"Caption updates failed: {e}")
            return False
    
    async def _update_creative_elements(self, 
                                      details: Dict[str, Any],
                                      result: AutoOptimizationResult) -> bool:
        """Update creative elements"""        try:
            elements = details.get("elements_to_update", [])
            
            # Simulate creative updates
            logger.info(f"Updating creative elements: {elements}")
            
            result.implementation_details = {
                "elements_updated": elements,
                "update_method": "ai_enhancement",
                "variants_created": details.get("A_B_test_variants", 2)
            }
            
            await asyncio.sleep(0.5)
            return True
            
        except Exception as e:
            logger.error(f"Creative elements update failed: {e}")
            return False
    
    async def _adjust_audience_targeting(self, 
                                       details: Dict[str, Any],
                                       result: AutoOptimizationResult) -> bool:
        """Adjust audience targeting"""        try:
            platform = details.get("platform")
            focus_areas = details.get("focus_areas", [])
            
            # Simulate audience targeting adjustments
            logger.info(f"Adjusting audience targeting for {platform}: {focus_areas}")
            
            result.implementation_details = {
                "platform": platform,
                "targeting_updates": focus_areas,
                "optimization_type": "performance_based"
            }
            
            await asyncio.sleep(0.4)
            return True
            
        except Exception as e:
            logger.error(f"Audience targeting adjustment failed: {e}")
            return False
    
    async def _modify_posting_frequency(self, 
                                      details: Dict[str, Any],
                                      result: AutoOptimizationResult) -> bool:
        """Modify posting frequency"""        try:
            # Simulate frequency modification
            logger.info("Modifying posting frequency based on performance data")
            
            result.implementation_details = {
                "old_frequency": "daily",
                "new_frequency": "optimized_schedule",
                "adjustment_type": "performance_driven"
            }
            
            await asyncio.sleep(0.2)
            return True
            
        except Exception as e:
            logger.error(f"Posting frequency modification failed: {e}")
            return False
    
    async def monitor_optimization_results(self, 
                                         optimization_id: str,
                                         monitoring_period: timedelta = timedelta(hours=24)) -> AutoOptimizationResult:
        """Monitor results of executed optimization"""        try:
            if optimization_id not in self.active_optimizations:
                raise OptimizationError("Optimization not found")
            
            result = self.active_optimizations[optimization_id]
            
            # Simulate monitoring period
            await asyncio.sleep(1)  # Simulate monitoring
            
            # Update with mock results
            result.after_values = {
                result.target_metrics[0].value: result.before_values.get(result.target_metrics[0].value, 0) * 1.15
            }
            
            # Calculate improvement
            for metric in result.target_metrics:
                metric_key = metric.value
                before = result.before_values.get(metric_key, 0)
                after = result.after_values.get(metric_key, 0)
                
                if before > 0:
                    improvement = (after - before) / before
                    result.improvement_achieved[metric_key] = improvement
            
            # Update success rate
            avg_improvement = statistics.mean(result.improvement_achieved.values()) if result.improvement_achieved else 0
            result.success_rate = min(1.0, max(0.0, avg_improvement * 2 + 0.5))
            
            result.status = "monitored"
            
            return result
            
        except Exception as e:
            logger.error(f"Optimization monitoring failed: {e}")
            raise OptimizationError(f"Monitoring failed: {str(e)}")


# Global performance intelligence system
performance_monitor_system = RealTimePerformanceMonitor()
optimization_engine = IntelligentOptimizationEngine()
auto_optimizer = AutoOptimizationExecutor()
