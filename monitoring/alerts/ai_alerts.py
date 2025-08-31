"""
🚨 AI/ML Alerts Module - Model Drift & Accuracy Monitoring
==========================================================

Advanced AI/ML alert management for model performance monitoring, drift detection,
and machine learning pipeline health tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
import json

from .intelligent_alert_manager import (
    IntelligentAlertManager, AlertCategory, AlertSeverity, 
    AlertType, AlertRule, IntelligentAlert
)

logger = logging.getLogger(__name__)


class AIModelType(Enum):
    """AI model types"""
    CONTENT_FINGERPRINTING = "content_fingerprinting"
    SIMILARITY_DETECTION = "similarity_detection"
    COPYRIGHT_CLASSIFICATION = "copyright_classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    FRAUD_DETECTION = "fraud_detection"
    USER_BEHAVIOR_PREDICTION = "user_behavior_prediction"


class DriftType(Enum):
    """Types of model drift"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    LABEL_DRIFT = "label_drift"


class ModelHealth(Enum):
    """Model health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILING = "failing"


@dataclass
class ModelMetrics:
    """AI model performance metrics"""
    model_id: str
    model_name: str
    model_type: AIModelType
    timestamp: datetime
    
    # Performance metrics
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    
    # Operational metrics
    inference_latency_p50: float  # milliseconds
    inference_latency_p95: float  # milliseconds
    inference_latency_p99: float  # milliseconds
    throughput: float  # predictions per second
    error_rate: float  # percentage
    
    # Drift metrics
    data_drift_score: float  # 0-1 scale
    concept_drift_score: float  # 0-1 scale
    prediction_drift_score: float  # 0-1 scale
    
    # Resource metrics
    cpu_usage: float  # percentage
    memory_usage: float  # percentage
    gpu_utilization: float  # percentage
    
    # Data quality metrics
    data_quality_score: float  # 0-1 scale
    missing_values_ratio: float
    outlier_ratio: float
    
    # Business metrics
    prediction_confidence: float
    business_impact_score: float
    
    # Additional context
    environment: str = "production"
    version: str = "1.0.0"
    deployment_time: Optional[datetime] = None


@dataclass
class ModelBaseline:
    """Model baseline performance for comparison"""
    model_id: str
    baseline_accuracy: float
    baseline_precision: float
    baseline_recall: float
    baseline_f1_score: float
    baseline_latency: float
    baseline_throughput: float
    created_at: datetime
    sample_size: int


@dataclass
class DriftDetectionResult:
    """Drift detection analysis result"""
    model_id: str
    drift_type: DriftType
    drift_score: float
    confidence: float
    detected_at: datetime
    affected_features: List[str]
    recommendation: str
    severity: AlertSeverity


class AIAlertManager:
    """
    Advanced AI/ML alert management for model monitoring and health tracking
    
    Features:
    - Model performance degradation detection
    - Drift detection and analysis
    - Inference latency monitoring
    - Data quality monitoring
    - Model training failure detection
    - Resource utilization alerts
    - Business impact assessment
    """
    
    def __init__(self, alert_manager: IntelligentAlertManager):
        """Initialize AI alert manager"""
        self.alert_manager = alert_manager
        self.model_metrics_history: Dict[str, List[ModelMetrics]] = {}
        self.model_baselines: Dict[str, ModelBaseline] = {}
        self.drift_detection_results: List[DriftDetectionResult] = []
        
        # AI alert thresholds
        self.thresholds = {
            # Performance thresholds
            "accuracy_degradation_critical": 0.10,    # 10% drop
            "accuracy_degradation_warning": 0.05,     # 5% drop
            "latency_critical": 10000,                # 10 seconds
            "latency_warning": 5000,                  # 5 seconds
            "error_rate_critical": 0.10,              # 10%
            "error_rate_warning": 0.05,               # 5%
            
            # Drift thresholds
            "drift_score_critical": 0.8,
            "drift_score_warning": 0.6,
            "data_quality_critical": 0.7,
            "data_quality_warning": 0.8,
            
            # Resource thresholds
            "cpu_critical": 90.0,
            "memory_critical": 90.0,
            "gpu_critical": 95.0,
            
            # Business impact thresholds
            "business_impact_critical": 0.8,
            "confidence_drop_warning": 0.1,
        }
        
        self._initialize_ai_rules()
        logger.info("AIAlertManager initialized")
    
    def _initialize_ai_rules(self):
        """Initialize AI/ML specific alert rules"""
        
        # Model Drift Detection
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="ai_model_drift_critical",
            name="Critical Model Drift Detected",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.MODEL_DRIFT,
            severity=AlertSeverity.CRITICAL,
            expression="model_drift_score > 0.8",
            threshold={
                "drift_score": 0.8,
                "confidence_threshold": 0.95,
                "detection_window": "1h"
            },
            duration="30m",
            escalation_levels=[
                {"level": 1, "delay": "1h", "channels": ["email", "slack"]},
                {"level": 2, "delay": "4h", "channels": ["email", "slack", "phone"]}
            ],
            correlation_rules=["ai_accuracy_degradation", "ai_data_quality_issue"]
        ))
        
        # Accuracy Degradation
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="ai_accuracy_degradation_critical",
            name="Critical Model Accuracy Degradation",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            severity=AlertSeverity.CRITICAL,
            expression="accuracy_drop > 0.10",
            threshold={
                "accuracy_drop_percent": 10,
                "minimum_samples": 100,
                "baseline_comparison": True
            },
            duration="20m",
            escalation_levels=[
                {"level": 1, "delay": "30m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "2h", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        # Inference Latency High
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="ai_inference_latency_critical",
            name="Critical Inference Latency",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.INFERENCE_LATENCY,
            severity=AlertSeverity.CRITICAL,
            expression="inference_latency_p95 > 10000",
            threshold={
                "latency_ms": 10000,
                "percentile": 95,
                "impact_assessment": "high"
            },
            duration="15m",
            escalation_levels=[
                {"level": 1, "delay": "20m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "1h", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        # Training Failure
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="ai_training_failure",
            name="Model Training Failure",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.TRAINING_FAILURE,
            severity=AlertSeverity.CRITICAL,
            expression="training_failed == true",
            threshold={
                "failure_type": "any",
                "retry_attempts": 3,
                "immediate_notification": True
            },
            duration="1m",
            auto_resolve=False,
            escalation_levels=[
                {"level": 1, "delay": "5m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "30m", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        # Data Quality Issues
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="ai_data_quality_critical",
            name="Critical Data Quality Issue",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.DATA_QUALITY_ISSUE,
            severity=AlertSeverity.WARNING,
            expression="data_quality_score < 0.7",
            threshold={
                "quality_score": 0.7,
                "missing_values_threshold": 0.2,
                "outlier_threshold": 0.1
            },
            duration="45m",
            escalation_levels=[
                {"level": 1, "delay": "1h", "channels": ["email", "slack"]},
                {"level": 2, "delay": "4h", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        logger.info("AI/ML alert rules initialized")
    
    async def evaluate_model_metrics(self, metrics: ModelMetrics) -> List[IntelligentAlert]:
        """Evaluate AI model metrics and trigger alerts"""
        triggered_alerts = []
        
        # Store metrics for trend analysis
        if metrics.model_id not in self.model_metrics_history:
            self.model_metrics_history[metrics.model_id] = []
        
        self.model_metrics_history[metrics.model_id].append(metrics)
        
        # Keep only last 7 days of history per model
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        self.model_metrics_history[metrics.model_id] = [
            m for m in self.model_metrics_history[metrics.model_id]
            if m.timestamp >= cutoff_time
        ]
        
        try:
            # Evaluate model performance alerts
            performance_alerts = await self._evaluate_model_performance_alerts(metrics)
            triggered_alerts.extend(performance_alerts)
            
            # Evaluate drift detection alerts
            drift_alerts = await self._evaluate_drift_alerts(metrics)
            triggered_alerts.extend(drift_alerts)
            
            # Evaluate operational alerts
            operational_alerts = await self._evaluate_operational_alerts(metrics)
            triggered_alerts.extend(operational_alerts)
            
            # Evaluate data quality alerts
            quality_alerts = await self._evaluate_data_quality_alerts(metrics)
            triggered_alerts.extend(quality_alerts)
            
            # Update model baselines if needed
            await self._update_model_baseline(metrics)
            
            logger.debug(f"Evaluated AI model metrics for {metrics.model_id}, triggered {len(triggered_alerts)} alerts")
            
        except Exception as e:
            logger.error(f"Error evaluating AI model metrics: {e}")
        
        return triggered_alerts
    
    async def _evaluate_model_performance_alerts(self, metrics: ModelMetrics) -> List[IntelligentAlert]:
        """Evaluate model performance degradation alerts"""
        alerts = []
        
        try:
            # Get baseline for comparison
            baseline = await self._get_model_baseline(metrics.model_id)
            
            if baseline:
                # Calculate accuracy degradation
                accuracy_drop = (baseline.baseline_accuracy - metrics.accuracy) / baseline.baseline_accuracy
                
                if accuracy_drop >= self.thresholds["accuracy_degradation_critical"]:
                    alert_metrics = {
                        "model_id": metrics.model_id,
                        "model_name": metrics.model_name,
                        "current_accuracy": metrics.accuracy,
                        "baseline_accuracy": baseline.baseline_accuracy,
                        "accuracy_drop": accuracy_drop,
                        "degradation_percentage": accuracy_drop * 100,
                        "performance_impact": await self._assess_performance_impact(metrics, baseline)
                    }
                    
                    alert = await self.alert_manager._create_alert(
                        self.alert_manager.alert_rules["ai_accuracy_degradation_critical"],
                        alert_metrics
                    )
                    alerts.append(alert)
                
                # Check other performance metrics
                f1_drop = (baseline.baseline_f1_score - metrics.f1_score) / baseline.baseline_f1_score if baseline.baseline_f1_score > 0 else 0
                if f1_drop >= 0.15:  # 15% F1 score drop
                    logger.warning(f"F1 score degradation for model {metrics.model_id}: {f1_drop:.3f}")
            
        except Exception as e:
            logger.error(f"Error evaluating model performance alerts: {e}")
        
        return alerts
    
    async def _evaluate_drift_alerts(self, metrics: ModelMetrics) -> List[IntelligentAlert]:
        """Evaluate model drift alerts"""
        alerts = []
        
        try:
            # Evaluate different types of drift
            drift_types = [
                ("data_drift", metrics.data_drift_score),
                ("concept_drift", metrics.concept_drift_score),
                ("prediction_drift", metrics.prediction_drift_score)
            ]
            
            for drift_type, drift_score in drift_types:
                if drift_score >= self.thresholds["drift_score_critical"]:
                    # Perform detailed drift analysis
                    drift_analysis = await self._analyze_drift_details(metrics, drift_type, drift_score)
                    
                    alert_metrics = {
                        "model_id": metrics.model_id,
                        "model_name": metrics.model_name,
                        "model_drift_score": drift_score,
                        "drift_type": drift_type,
                        "drift_analysis": drift_analysis,
                        "confidence": drift_analysis.get("confidence", 0.95),
                        "affected_features": drift_analysis.get("affected_features", []),
                        "recommendation": drift_analysis.get("recommendation", "Review model and retrain if necessary")
                    }
                    
                    alert = await self.alert_manager._create_alert(
                        self.alert_manager.alert_rules["ai_model_drift_critical"],
                        alert_metrics
                    )
                    alerts.append(alert)
                    
                    # Store drift detection result
                    drift_result = DriftDetectionResult(
                        model_id=metrics.model_id,
                        drift_type=DriftType(drift_type),
                        drift_score=drift_score,
                        confidence=drift_analysis.get("confidence", 0.95),
                        detected_at=metrics.timestamp,
                        affected_features=drift_analysis.get("affected_features", []),
                        recommendation=drift_analysis.get("recommendation", "Review and retrain"),
                        severity=AlertSeverity.CRITICAL if drift_score > 0.8 else AlertSeverity.WARNING
                    )
                    self.drift_detection_results.append(drift_result)
            
        except Exception as e:
            logger.error(f"Error evaluating drift alerts: {e}")
        
        return alerts
    
    async def _evaluate_operational_alerts(self, metrics: ModelMetrics) -> List[IntelligentAlert]:
        """Evaluate operational performance alerts"""
        alerts = []
        
        try:
            # Inference Latency Alert
            if metrics.inference_latency_p95 >= self.thresholds["latency_critical"]:
                alert_metrics = {
                    "model_id": metrics.model_id,
                    "model_name": metrics.model_name,
                    "inference_latency_p95": metrics.inference_latency_p95,
                    "threshold": self.thresholds["latency_critical"],
                    "latency_trend": await self._calculate_latency_trend(metrics.model_id),
                    "resource_usage": {
                        "cpu": metrics.cpu_usage,
                        "memory": metrics.memory_usage,
                        "gpu": metrics.gpu_utilization
                    }
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["ai_inference_latency_critical"],
                    alert_metrics
                )
                alerts.append(alert)
            
            # Error Rate Alert
            if metrics.error_rate >= self.thresholds["error_rate_critical"]:
                logger.warning(f"High error rate for model {metrics.model_id}: {metrics.error_rate:.3f}")
            
            # Resource Utilization Alert
            if (metrics.cpu_usage >= self.thresholds["cpu_critical"] or 
                metrics.memory_usage >= self.thresholds["memory_critical"] or
                metrics.gpu_utilization >= self.thresholds["gpu_critical"]):
                
                logger.warning(f"High resource usage for model {metrics.model_id}")
            
        except Exception as e:
            logger.error(f"Error evaluating operational alerts: {e}")
        
        return alerts
    
    async def _evaluate_data_quality_alerts(self, metrics: ModelMetrics) -> List[IntelligentAlert]:
        """Evaluate data quality alerts"""
        alerts = []
        
        try:
            if metrics.data_quality_score < self.thresholds["data_quality_critical"]:
                alert_metrics = {
                    "model_id": metrics.model_id,
                    "model_name": metrics.model_name,
                    "data_quality_score": metrics.data_quality_score,
                    "threshold": self.thresholds["data_quality_critical"],
                    "missing_values_ratio": metrics.missing_values_ratio,
                    "outlier_ratio": metrics.outlier_ratio,
                    "quality_issues": await self._identify_quality_issues(metrics)
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["ai_data_quality_critical"],
                    alert_metrics
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error evaluating data quality alerts: {e}")
        
        return alerts
    
    async def process_training_failure(self, model_id: str, model_name: str, 
                                     failure_details: Dict[str, Any]) -> List[IntelligentAlert]:
        """Process model training failure and trigger alerts"""
        alerts = []
        
        try:
            alert_metrics = {
                "model_id": model_id,
                "model_name": model_name,
                "training_failed": True,
                "failure_details": failure_details,
                "timestamp": datetime.utcnow().isoformat(),
                "immediate_action_required": True
            }
            
            alert = await self.alert_manager._create_alert(
                self.alert_manager.alert_rules["ai_training_failure"],
                alert_metrics
            )
            alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error processing training failure: {e}")
        
        return alerts
    
    async def _analyze_drift_details(self, metrics: ModelMetrics, drift_type: str, 
                                   drift_score: float) -> Dict[str, Any]:
        """Analyze drift details and provide recommendations"""
        try:
            analysis = {
                "drift_type": drift_type,
                "drift_score": drift_score,
                "confidence": 0.95,
                "severity": "critical" if drift_score > 0.8 else "warning",
                "affected_features": [],
                "recommendation": ""
            }
            
            if drift_type == "data_drift":
                analysis["affected_features"] = ["feature_distribution", "input_statistics"]
                analysis["recommendation"] = "Review input data distribution and consider retraining with recent data"
            elif drift_type == "concept_drift":
                analysis["affected_features"] = ["target_relationship", "concept_definition"]
                analysis["recommendation"] = "Analyze target concept changes and update model accordingly"
            elif drift_type == "prediction_drift":
                analysis["affected_features"] = ["prediction_distribution", "output_patterns"]
                analysis["recommendation"] = "Review prediction patterns and validate model outputs"
            
            # Add historical context if available
            if metrics.model_id in self.model_metrics_history:
                history = self.model_metrics_history[metrics.model_id]
                if len(history) > 1:
                    analysis["drift_trend"] = await self._calculate_drift_trend(history, drift_type)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing drift details: {e}")
            return {"error": str(e)}
    
    async def _assess_performance_impact(self, metrics: ModelMetrics, 
                                       baseline: ModelBaseline) -> Dict[str, Any]:
        """Assess the business impact of performance degradation"""
        try:
            impact_assessment = {
                "accuracy_impact": "high" if metrics.accuracy < baseline.baseline_accuracy * 0.9 else "medium",
                "latency_impact": "high" if metrics.inference_latency_p95 > baseline.baseline_latency * 2 else "low",
                "business_impact_score": metrics.business_impact_score,
                "confidence_impact": "high" if metrics.prediction_confidence < 0.7 else "medium",
                "overall_impact": "critical"
            }
            
            # Calculate overall impact score
            impact_factors = [
                metrics.accuracy / baseline.baseline_accuracy,
                baseline.baseline_latency / metrics.inference_latency_p95,
                metrics.business_impact_score,
                metrics.prediction_confidence
            ]
            
            overall_score = sum(impact_factors) / len(impact_factors)
            
            if overall_score < 0.7:
                impact_assessment["overall_impact"] = "critical"
            elif overall_score < 0.85:
                impact_assessment["overall_impact"] = "high"
            else:
                impact_assessment["overall_impact"] = "medium"
            
            return impact_assessment
            
        except Exception as e:
            logger.error(f"Error assessing performance impact: {e}")
            return {"overall_impact": "unknown"}
    
    async def _identify_quality_issues(self, metrics: ModelMetrics) -> List[str]:
        """Identify specific data quality issues"""
        issues = []
        
        try:
            if metrics.missing_values_ratio > 0.15:
                issues.append(f"High missing values ratio: {metrics.missing_values_ratio:.3f}")
            
            if metrics.outlier_ratio > 0.1:
                issues.append(f"High outlier ratio: {metrics.outlier_ratio:.3f}")
            
            if metrics.data_quality_score < 0.8:
                issues.append(f"Low overall data quality score: {metrics.data_quality_score:.3f}")
            
            return issues
            
        except Exception as e:
            logger.error(f"Error identifying quality issues: {e}")
            return ["Error analyzing data quality"]
    
    async def _get_model_baseline(self, model_id: str) -> Optional[ModelBaseline]:
        """Get baseline metrics for a model"""
        return self.model_baselines.get(model_id)
    
    async def _update_model_baseline(self, metrics: ModelMetrics):
        """Update model baseline if performance is good"""
        try:
            # Only update baseline if model is performing well
            if (metrics.accuracy > 0.85 and 
                metrics.error_rate < 0.05 and 
                metrics.data_quality_score > 0.9):
                
                baseline = ModelBaseline(
                    model_id=metrics.model_id,
                    baseline_accuracy=metrics.accuracy,
                    baseline_precision=metrics.precision,
                    baseline_recall=metrics.recall,
                    baseline_f1_score=metrics.f1_score,
                    baseline_latency=metrics.inference_latency_p95,
                    baseline_throughput=metrics.throughput,
                    created_at=metrics.timestamp,
                    sample_size=1000  # Assumed sample size
                )
                
                self.model_baselines[metrics.model_id] = baseline
                logger.info(f"Updated baseline for model {metrics.model_id}")
            
        except Exception as e:
            logger.error(f"Error updating model baseline: {e}")
    
    async def _calculate_latency_trend(self, model_id: str) -> str:
        """Calculate latency trend for a model"""
        try:
            if model_id not in self.model_metrics_history:
                return "insufficient_data"
            
            history = self.model_metrics_history[model_id]
            if len(history) < 3:
                return "insufficient_data"
            
            recent_latencies = [m.inference_latency_p95 for m in history[-3:]]
            
            if recent_latencies[2] > recent_latencies[1] > recent_latencies[0]:
                return "increasing"
            elif recent_latencies[2] < recent_latencies[1] < recent_latencies[0]:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating latency trend: {e}")
            return "unknown"
    
    async def _calculate_drift_trend(self, history: List[ModelMetrics], drift_type: str) -> str:
        """Calculate drift trend over time"""
        try:
            if len(history) < 3:
                return "insufficient_data"
            
            if drift_type == "data_drift":
                drift_scores = [m.data_drift_score for m in history[-3:]]
            elif drift_type == "concept_drift":
                drift_scores = [m.concept_drift_score for m in history[-3:]]
            elif drift_type == "prediction_drift":
                drift_scores = [m.prediction_drift_score for m in history[-3:]]
            else:
                return "unknown_type"
            
            if drift_scores[2] > drift_scores[1] > drift_scores[0]:
                return "increasing"
            elif drift_scores[2] < drift_scores[1] < drift_scores[0]:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating drift trend: {e}")
            return "unknown"
    
    async def get_ai_alert_summary(self) -> Dict[str, Any]:
        """Get AI/ML alert summary and model health overview"""
        try:
            model_statuses = {}
            overall_health = ModelHealth.HEALTHY
            
            # Analyze each model
            for model_id, history in self.model_metrics_history.items():
                if not history:
                    continue
                
                latest_metrics = history[-1]
                model_health = await self._calculate_model_health(latest_metrics)
                model_statuses[model_id] = {
                    "model_name": latest_metrics.model_name,
                    "model_type": latest_metrics.model_type.value,
                    "health": model_health.value,
                    "accuracy": latest_metrics.accuracy,
                    "drift_score": max(
                        latest_metrics.data_drift_score,
                        latest_metrics.concept_drift_score,
                        latest_metrics.prediction_drift_score
                    ),
                    "last_updated": latest_metrics.timestamp.isoformat()
                }
                
                # Update overall health
                if model_health == ModelHealth.FAILING:
                    overall_health = ModelHealth.FAILING
                elif model_health == ModelHealth.CRITICAL and overall_health != ModelHealth.FAILING:
                    overall_health = ModelHealth.CRITICAL
                elif model_health == ModelHealth.WARNING and overall_health == ModelHealth.HEALTHY:
                    overall_health = ModelHealth.WARNING
            
            # Recent drift detections
            recent_drifts = [
                drift for drift in self.drift_detection_results
                if drift.detected_at >= datetime.utcnow() - timedelta(hours=24)
            ]
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_health": overall_health.value,
                "total_models": len(model_statuses),
                "model_statuses": model_statuses,
                "recent_drift_detections": len(recent_drifts),
                "drift_summary": [
                    {
                        "model_id": drift.model_id,
                        "drift_type": drift.drift_type.value,
                        "drift_score": drift.drift_score,
                        "severity": drift.severity.value
                    }
                    for drift in recent_drifts
                ],
                "alert_thresholds": self.thresholds,
                "baselines_available": len(self.model_baselines)
            }
            
        except Exception as e:
            logger.error(f"Error generating AI alert summary: {e}")
            return {"error": str(e)}
    
    async def _calculate_model_health(self, metrics: ModelMetrics) -> ModelHealth:
        """Calculate overall model health status"""
        try:
            health_factors = []
            
            # Performance factors
            baseline = await self._get_model_baseline(metrics.model_id)
            if baseline:
                accuracy_ratio = metrics.accuracy / baseline.baseline_accuracy
                health_factors.append(accuracy_ratio)
            else:
                health_factors.append(metrics.accuracy)  # Use absolute accuracy
            
            # Drift factors
            max_drift = max(
                metrics.data_drift_score,
                metrics.concept_drift_score,
                metrics.prediction_drift_score
            )
            drift_health = 1.0 - max_drift
            health_factors.append(drift_health)
            
            # Operational factors
            latency_health = min(1.0, 5000 / metrics.inference_latency_p95)  # 5s baseline
            error_health = 1.0 - metrics.error_rate
            health_factors.extend([latency_health, error_health])
            
            # Data quality factor
            health_factors.append(metrics.data_quality_score)
            
            # Calculate overall health score
            overall_health_score = sum(health_factors) / len(health_factors)
            
            if overall_health_score >= 0.9:
                return ModelHealth.HEALTHY
            elif overall_health_score >= 0.75:
                return ModelHealth.WARNING
            elif overall_health_score >= 0.6:
                return ModelHealth.CRITICAL
            else:
                return ModelHealth.FAILING
                
        except Exception as e:
            logger.error(f"Error calculating model health: {e}")
            return ModelHealth.WARNING


# Export the main classes
__all__ = [
    "AIAlertManager",
    "ModelMetrics", 
    "ModelBaseline",
    "DriftDetectionResult",
    "AIModelType",
    "DriftType",
    "ModelHealth"
]