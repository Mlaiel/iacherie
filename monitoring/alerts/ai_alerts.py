"""🚨 AI/ML Alerts Module - Model Drift & Accuracy Monitoring
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
    """
AI model types"""

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
    """
Drift detection analysis result"""
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
        """
Initialize AI alert manager"""
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
                    await self.alert_manager._process_new_alert(alert)
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
                    await self.alert_manager._process_new_alert(alert)
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
                await self.alert_manager._process_new_alert(alert)
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
                await self.alert_manager._process_new_alert(alert)
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
            await self.alert_manager._process_new_alert(alert)
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
        """
Update model baseline if performance is good"""
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


# ===============================================================================
# CREATOR ECONOMY AI MONITORING ENHANCEMENTS
# ===============================================================================
# Enhanced AI monitoring specifically designed for Creator Economy business logic
# Added by: Fahed Mlaiel (mlaiel@live.de) - Creator Economy AI Intelligence
# ===============================================================================

class CreatorAIModelType(Enum):
    """Creator Economy specific AI model types"""
    
    # Content Analysis Models
    CONTENT_QUALITY_SCORER = "content_quality_scorer"
    CREATOR_CONTENT_CLASSIFIER = "creator_content_classifier"
    MULTI_FORMAT_CONTENT_ANALYZER = "multi_format_content_analyzer"
    
    # Creator Intelligence Models
    CREATOR_TIER_PREDICTOR = "creator_tier_predictor"
    CREATOR_ENGAGEMENT_PREDICTOR = "creator_engagement_predictor"
    CREATOR_REVENUE_FORECASTER = "creator_revenue_forecaster"
    CREATOR_CHURN_PREDICTOR = "creator_churn_predictor"
    
    # Content Protection Models
    COPYRIGHT_INFRINGEMENT_DETECTOR = "copyright_infringement_detector"
    WATERMARK_INTEGRITY_CHECKER = "watermark_integrity_checker"
    CONTENT_AUTHENTICITY_VERIFIER = "content_authenticity_verifier"
    DEEPFAKE_DETECTOR = "deepfake_detector"
    
    # Collaboration Models
    CREATOR_MATCHING_ENGINE = "creator_matching_engine"
    COLLABORATION_SUCCESS_PREDICTOR = "collaboration_success_predictor"
    CREATOR_COMPATIBILITY_SCORER = "creator_compatibility_scorer"
    
    # Monetization Models
    REVENUE_OPTIMIZATION_ENGINE = "revenue_optimization_engine"
    PRICING_RECOMMENDATION_MODEL = "pricing_recommendation_model"
    MONETIZATION_OPPORTUNITY_DETECTOR = "monetization_opportunity_detector"
    
    # SEO & Distribution Models
    SEO_PERFORMANCE_PREDICTOR = "seo_performance_predictor"
    CONTENT_VIRALITY_PREDICTOR = "content_virality_predictor"
    PLATFORM_PERFORMANCE_OPTIMIZER = "platform_performance_optimizer"
    
    # Gamification Models
    CREATOR_ACHIEVEMENT_TRACKER = "creator_achievement_tracker"
    GAMIFICATION_ENGAGEMENT_OPTIMIZER = "gamification_engagement_optimizer"


@dataclass
class CreatorAIMetrics:
    """Extended AI metrics for Creator Economy specific models"""
    model_id: str
    model_type: CreatorAIModelType
    creator_id: Optional[str]
    creator_type: Optional[str]
    timestamp: datetime
    
    # Creator-specific performance metrics
    creator_satisfaction_score: float = 0.0
    content_format_accuracy: Dict[str, float] = field(default_factory=dict)
    cross_creator_correlation: float = 0.0
    business_value_generated: float = 0.0
    creator_tier_prediction_accuracy: float = 0.0
    
    # Content protection metrics
    copyright_detection_precision: float = 0.0
    false_positive_rate: float = 0.0
    content_authenticity_score: float = 0.0
    watermark_detection_rate: float = 0.0
    
    # Collaboration metrics
    matching_success_rate: float = 0.0
    collaboration_outcome_accuracy: float = 0.0
    creator_compatibility_precision: float = 0.0
    
    # Monetization metrics
    revenue_prediction_accuracy: float = 0.0
    pricing_optimization_impact: float = 0.0
    monetization_conversion_rate: float = 0.0
    
    # Multi-format content metrics
    audio_processing_accuracy: float = 0.0
    video_analysis_precision: float = 0.0
    image_classification_accuracy: float = 0.0
    text_sentiment_accuracy: float = 0.0
    
    # Platform-specific metrics
    platform_performance_scores: Dict[str, float] = field(default_factory=dict)
    cross_platform_consistency: float = 0.0
    seo_optimization_effectiveness: float = 0.0


class CreatorAIAlertManager:
    """
    Enhanced AI Alert Manager with Creator Economy specific monitoring
    
    Extends the base AI monitoring with Creator-focused intelligence including:
    - Creator-specific model performance tracking
    - Multi-format content analysis monitoring
    - Creator tier prediction accuracy
    - Content protection AI effectiveness
    - Collaboration algorithm performance
    - Monetization model optimization
    """
    
    def __init__(self, ai_alert_manager: AIAlertManager):
        self.base_manager = ai_alert_manager
        self.creator_metrics_history: Dict[str, List[CreatorAIMetrics]] = {}
        self.creator_model_baselines: Dict[str, Dict[str, float]] = {}
        
        # Creator Economy specific thresholds
        self.creator_thresholds = {
            # Creator satisfaction thresholds
            "creator_satisfaction_critical": 6.0,  # Below 6/10
            "creator_satisfaction_warning": 7.5,   # Below 7.5/10
            
            # Content format accuracy thresholds
            "audio_accuracy_critical": 0.85,
            "video_accuracy_critical": 0.80,
            "image_accuracy_critical": 0.90,
            "text_accuracy_critical": 0.92,
            
            # Business impact thresholds
            "business_value_drop_critical": 0.20,    # 20% drop
            "revenue_prediction_accuracy_warning": 0.80,
            "tier_prediction_accuracy_warning": 0.85,
            
            # Content protection thresholds
            "copyright_detection_precision_critical": 0.95,
            "false_positive_rate_critical": 0.05,    # 5% max
            "authenticity_score_critical": 0.90,
            
            # Collaboration thresholds
            "matching_success_rate_warning": 0.70,
            "compatibility_precision_warning": 0.75,
            
            # Multi-platform thresholds
            "cross_platform_consistency_warning": 0.80,
            "seo_effectiveness_warning": 0.75
        }
        
        self._initialize_creator_ai_rules()
        logger.info("CreatorAIAlertManager initialized with Creator Economy enhancements")
    
    def _initialize_creator_ai_rules(self):
        """Initialize Creator Economy specific AI alert rules"""
        
        # Creator Satisfaction AI Model Performance
        self.base_manager.alert_manager.add_alert_rule(AlertRule(
            rule_id="creator_ai_satisfaction_critical",
            name="Creator Satisfaction AI Model Underperforming",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            severity=AlertSeverity.CRITICAL,
            expression="creator_satisfaction_score < 6.0",
            threshold={
                "satisfaction_threshold": 6.0,
                "creator_sample_size": 50,
                "evaluation_window": "24h"
            },
            duration="2h",
            escalation_levels=[
                {"level": 1, "delay": "1h", "channels": ["email", "slack"]},
                {"level": 2, "delay": "4h", "channels": ["email", "slack", "phone"]}
            ],
            custom_metadata={
                "creator_economy_specific": True,
                "business_impact": "high",
                "affected_creators": "all_tiers"
            }
        ))
        
        # Multi-Format Content Analysis Performance
        self.base_manager.alert_manager.add_alert_rule(AlertRule(
            rule_id="creator_ai_multiformat_degradation",
            name="Multi-Format Content Analysis Degradation",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            severity=AlertSeverity.WARNING,
            expression="min(audio_accuracy, video_accuracy, image_accuracy) < 0.85",
            threshold={
                "min_format_accuracy": 0.85,
                "affected_formats_threshold": 2,
                "content_volume_minimum": 100
            },
            duration="1h",
            escalation_levels=[
                {"level": 1, "delay": "2h", "channels": ["email", "slack"]}
            ],
            custom_metadata={
                "creator_economy_specific": True,
                "content_formats": ["audio", "video", "image", "text"],
                "creator_impact": "content_quality"
            }
        ))
        
        # Creator Tier Prediction Accuracy
        self.base_manager.alert_manager.add_alert_rule(AlertRule(
            rule_id="creator_ai_tier_prediction_warning",
            name="Creator Tier Prediction Accuracy Drop",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            severity=AlertSeverity.WARNING,
            expression="creator_tier_prediction_accuracy < 0.85",
            threshold={
                "tier_accuracy_threshold": 0.85,
                "business_impact_threshold": "medium",
                "creator_count_minimum": 200
            },
            duration="3h",
            escalation_levels=[
                {"level": 1, "delay": "4h", "channels": ["email", "slack"]}
            ],
            custom_metadata={
                "creator_economy_specific": True,
                "business_function": "tier_management",
                "sla_impact": "creator_experience"
            }
        ))
        
        # Content Protection AI Performance
        self.base_manager.alert_manager.add_alert_rule(AlertRule(
            rule_id="creator_ai_content_protection_critical",
            name="Critical Content Protection AI Performance",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            severity=AlertSeverity.CRITICAL,
            expression="copyright_detection_precision < 0.95 OR false_positive_rate > 0.05",
            threshold={
                "copyright_precision_min": 0.95,
                "false_positive_max": 0.05,
                "creator_ip_risk": "high"
            },
            duration="30m",
            escalation_levels=[
                {"level": 1, "delay": "15m", "channels": ["email", "slack", "phone"]},
                {"level": 2, "delay": "1h", "channels": ["email", "slack", "phone", "legal"]}
            ],
            custom_metadata={
                "creator_economy_specific": True,
                "legal_impact": "high",
                "creator_protection": "ip_rights"
            }
        ))
        
        # Collaboration Algorithm Performance
        self.base_manager.alert_manager.add_alert_rule(AlertRule(
            rule_id="creator_ai_collaboration_warning",
            name="Creator Collaboration AI Performance Warning",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            severity=AlertSeverity.WARNING,
            expression="matching_success_rate < 0.70 OR compatibility_precision < 0.75",
            threshold={
                "matching_success_min": 0.70,
                "compatibility_precision_min": 0.75,
                "collaboration_volume_min": 50
            },
            duration="4h",
            escalation_levels=[
                {"level": 1, "delay": "6h", "channels": ["email", "slack"]}
            ],
            custom_metadata={
                "creator_economy_specific": True,
                "business_function": "creator_collaboration",
                "community_impact": "partnership_success"
            }
        ))
        
        # Revenue Prediction Model Performance
        self.base_manager.alert_manager.add_alert_rule(AlertRule(
            rule_id="creator_ai_revenue_prediction_warning",
            name="Creator Revenue Prediction Accuracy Warning",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            severity=AlertSeverity.WARNING,
            expression="revenue_prediction_accuracy < 0.80",
            threshold={
                "revenue_accuracy_min": 0.80,
                "business_impact_assessment": "medium",
                "creator_tier_affected": "all"
            },
            duration="6h",
            escalation_levels=[
                {"level": 1, "delay": "8h", "channels": ["email", "slack"]}
            ],
            custom_metadata={
                "creator_economy_specific": True,
                "business_function": "monetization",
                "financial_impact": "revenue_forecasting"
            }
        ))
        
        logger.info("Creator Economy AI alert rules initialized")
    
    async def evaluate_creator_ai_metrics(self, metrics: CreatorAIMetrics) -> List[IntelligentAlert]:
        """Evaluate Creator Economy specific AI metrics and trigger alerts"""
        triggered_alerts = []
        
        # Store metrics for trend analysis
        if metrics.model_id not in self.creator_metrics_history:
            self.creator_metrics_history[metrics.model_id] = []
        
        self.creator_metrics_history[metrics.model_id].append(metrics)
        
        # Keep only recent metrics (last 1000 entries per model)
        if len(self.creator_metrics_history[metrics.model_id]) > 1000:
            self.creator_metrics_history[metrics.model_id] = \
                self.creator_metrics_history[metrics.model_id][-1000:]
        
        try:
            # Check Creator Satisfaction Score
            if metrics.creator_satisfaction_score < self.creator_thresholds["creator_satisfaction_critical"]:
                alert = await self._create_creator_satisfaction_alert(metrics, "critical")
                triggered_alerts.append(alert)
            elif metrics.creator_satisfaction_score < self.creator_thresholds["creator_satisfaction_warning"]:
                alert = await self._create_creator_satisfaction_alert(metrics, "warning")
                triggered_alerts.append(alert)
            
            # Check Multi-Format Content Analysis
            format_accuracies = [
                metrics.audio_processing_accuracy,
                metrics.video_analysis_precision,
                metrics.image_classification_accuracy,
                metrics.text_sentiment_accuracy
            ]
            min_format_accuracy = min(f for f in format_accuracies if f > 0)
            
            if min_format_accuracy < 0.85:
                alert = await self._create_multiformat_degradation_alert(metrics)
                triggered_alerts.append(alert)
            
            # Check Content Protection Performance
            if (metrics.copyright_detection_precision < self.creator_thresholds["copyright_detection_precision_critical"] or
                metrics.false_positive_rate > self.creator_thresholds["false_positive_rate_critical"]):
                alert = await self._create_content_protection_alert(metrics)
                triggered_alerts.append(alert)
            
            # Check Collaboration Algorithm Performance
            if (metrics.matching_success_rate < self.creator_thresholds["matching_success_rate_warning"] or
                metrics.creator_compatibility_precision < self.creator_thresholds["compatibility_precision_warning"]):
                alert = await self._create_collaboration_performance_alert(metrics)
                triggered_alerts.append(alert)
            
            # Check Revenue Prediction Accuracy
            if metrics.revenue_prediction_accuracy < self.creator_thresholds["revenue_prediction_accuracy_warning"]:
                alert = await self._create_revenue_prediction_alert(metrics)
                triggered_alerts.append(alert)
            
            # Check Creator Tier Prediction
            if metrics.creator_tier_prediction_accuracy < self.creator_thresholds["tier_prediction_accuracy_warning"]:
                alert = await self._create_tier_prediction_alert(metrics)
                triggered_alerts.append(alert)
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error evaluating Creator AI metrics: {e}")
            return []
    
    async def _create_creator_satisfaction_alert(self, metrics: CreatorAIMetrics, severity: str) -> IntelligentAlert:
        """Create alert for creator satisfaction score issues"""
        return IntelligentAlert(
            alert_id=f"creator_satisfaction_{severity}_{metrics.model_id}_{int(metrics.timestamp.timestamp())}",
            rule_id=f"creator_ai_satisfaction_{severity}",
            title=f"Creator Satisfaction AI Model {'Critical' if severity == 'critical' else 'Warning'}",
            description=f"Creator satisfaction prediction model showing {severity} performance: "
                       f"Score {metrics.creator_satisfaction_score:.2f} "
                       f"(threshold: {self.creator_thresholds[f'creator_satisfaction_{severity}']:.1f})",
            severity=AlertSeverity.CRITICAL if severity == "critical" else AlertSeverity.WARNING,
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            timestamp=metrics.timestamp,
            source="CreatorAIAlertManager",
            affected_resources=[metrics.model_id],
            metadata={
                "model_type": metrics.model_type.value,
                "creator_id": metrics.creator_id,
                "creator_type": metrics.creator_type,
                "satisfaction_score": metrics.creator_satisfaction_score,
                "business_impact": "creator_experience",
                "creator_economy_specific": True
            }
        )
    
    async def _create_multiformat_degradation_alert(self, metrics: CreatorAIMetrics) -> IntelligentAlert:
        """Create alert for multi-format content analysis degradation"""
        format_scores = {
            "audio": metrics.audio_processing_accuracy,
            "video": metrics.video_analysis_precision,
            "image": metrics.image_classification_accuracy,
            "text": metrics.text_sentiment_accuracy
        }
        
        return IntelligentAlert(
            alert_id=f"multiformat_degradation_{metrics.model_id}_{int(metrics.timestamp.timestamp())}",
            rule_id="creator_ai_multiformat_degradation",
            title="Multi-Format Content Analysis Performance Degradation",
            description=f"Content analysis showing degraded performance across formats: {format_scores}",
            severity=AlertSeverity.WARNING,
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            timestamp=metrics.timestamp,
            source="CreatorAIAlertManager",
            affected_resources=[metrics.model_id],
            metadata={
                "model_type": metrics.model_type.value,
                "format_accuracies": format_scores,
                "creator_id": metrics.creator_id,
                "business_impact": "content_quality",
                "creator_economy_specific": True
            }
        )
    
    async def _create_content_protection_alert(self, metrics: CreatorAIMetrics) -> IntelligentAlert:
        """Create alert for content protection AI performance issues"""
        return IntelligentAlert(
            alert_id=f"content_protection_{metrics.model_id}_{int(metrics.timestamp.timestamp())}",
            rule_id="creator_ai_content_protection_critical",
            title="Critical Content Protection AI Performance Issue",
            description=f"Content protection AI showing critical performance: "
                       f"Copyright precision: {metrics.copyright_detection_precision:.3f}, "
                       f"False positive rate: {metrics.false_positive_rate:.3f}",
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            timestamp=metrics.timestamp,
            source="CreatorAIAlertManager",
            affected_resources=[metrics.model_id],
            metadata={
                "model_type": metrics.model_type.value,
                "copyright_precision": metrics.copyright_detection_precision,
                "false_positive_rate": metrics.false_positive_rate,
                "authenticity_score": metrics.content_authenticity_score,
                "business_impact": "ip_protection",
                "legal_risk": "high",
                "creator_economy_specific": True
            }
        )
    
    async def _create_collaboration_performance_alert(self, metrics: CreatorAIMetrics) -> IntelligentAlert:
        """Create alert for collaboration algorithm performance issues"""
        return IntelligentAlert(
            alert_id=f"collaboration_performance_{metrics.model_id}_{int(metrics.timestamp.timestamp())}",
            rule_id="creator_ai_collaboration_warning",
            title="Creator Collaboration AI Performance Warning",
            description=f"Collaboration matching algorithm underperforming: "
                       f"Success rate: {metrics.matching_success_rate:.3f}, "
                       f"Compatibility precision: {metrics.creator_compatibility_precision:.3f}",
            severity=AlertSeverity.WARNING,
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            timestamp=metrics.timestamp,
            source="CreatorAIAlertManager",
            affected_resources=[metrics.model_id],
            metadata={
                "model_type": metrics.model_type.value,
                "matching_success_rate": metrics.matching_success_rate,
                "compatibility_precision": metrics.creator_compatibility_precision,
                "business_impact": "creator_collaboration",
                "community_impact": "partnership_success",
                "creator_economy_specific": True
            }
        )
    
    async def _create_revenue_prediction_alert(self, metrics: CreatorAIMetrics) -> IntelligentAlert:
        """Create alert for revenue prediction accuracy issues"""
        return IntelligentAlert(
            alert_id=f"revenue_prediction_{metrics.model_id}_{int(metrics.timestamp.timestamp())}",
            rule_id="creator_ai_revenue_prediction_warning",
            title="Creator Revenue Prediction Accuracy Warning",
            description=f"Revenue prediction model accuracy below threshold: "
                       f"{metrics.revenue_prediction_accuracy:.3f} "
                       f"(threshold: {self.creator_thresholds['revenue_prediction_accuracy_warning']:.2f})",
            severity=AlertSeverity.WARNING,
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            timestamp=metrics.timestamp,
            source="CreatorAIAlertManager",
            affected_resources=[metrics.model_id],
            metadata={
                "model_type": metrics.model_type.value,
                "revenue_accuracy": metrics.revenue_prediction_accuracy,
                "pricing_impact": metrics.pricing_optimization_impact,
                "business_impact": "monetization",
                "financial_risk": "medium",
                "creator_economy_specific": True
            }
        )
    
    async def _create_tier_prediction_alert(self, metrics: CreatorAIMetrics) -> IntelligentAlert:
        """Create alert for creator tier prediction accuracy issues"""
        return IntelligentAlert(
            alert_id=f"tier_prediction_{metrics.model_id}_{int(metrics.timestamp.timestamp())}",
            rule_id="creator_ai_tier_prediction_warning",
            title="Creator Tier Prediction Accuracy Warning",
            description=f"Creator tier prediction accuracy below threshold: "
                       f"{metrics.creator_tier_prediction_accuracy:.3f} "
                       f"(threshold: {self.creator_thresholds['tier_prediction_accuracy_warning']:.2f})",
            severity=AlertSeverity.WARNING,
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            timestamp=metrics.timestamp,
            source="CreatorAIAlertManager",
            affected_resources=[metrics.model_id],
            metadata={
                "model_type": metrics.model_type.value,
                "tier_accuracy": metrics.creator_tier_prediction_accuracy,
                "business_impact": "tier_management",
                "sla_impact": "creator_experience",
                "creator_economy_specific": True
            }
        )
    
    async def get_creator_ai_model_health(self, model_id: str) -> Dict[str, Any]:
        """Get comprehensive health status for Creator Economy AI models"""
        if model_id not in self.creator_metrics_history:
            return {"status": "unknown", "message": "No metrics available"}
        
        recent_metrics = self.creator_metrics_history[model_id][-10:]  # Last 10 metrics
        
        if not recent_metrics:
            return {"status": "unknown", "message": "No recent metrics"}
        
        latest_metrics = recent_metrics[-1]
        
        # Calculate health score based on Creator Economy specific factors
        health_factors = {
            "creator_satisfaction": latest_metrics.creator_satisfaction_score / 10.0,
            "content_protection": min(latest_metrics.copyright_detection_precision, 
                                    1.0 - latest_metrics.false_positive_rate),
            "collaboration_performance": (latest_metrics.matching_success_rate + 
                                        latest_metrics.creator_compatibility_precision) / 2.0,
            "revenue_accuracy": latest_metrics.revenue_prediction_accuracy,
            "tier_accuracy": latest_metrics.creator_tier_prediction_accuracy,
            "multiformat_performance": statistics.mean([
                latest_metrics.audio_processing_accuracy,
                latest_metrics.video_analysis_precision,
                latest_metrics.image_classification_accuracy,
                latest_metrics.text_sentiment_accuracy
            ]) if any([latest_metrics.audio_processing_accuracy,
                      latest_metrics.video_analysis_precision,
                      latest_metrics.image_classification_accuracy,
                      latest_metrics.text_sentiment_accuracy]) else 0.8
        }
        
        # Calculate weighted health score
        weights = {
            "creator_satisfaction": 0.25,
            "content_protection": 0.20,
            "collaboration_performance": 0.15,
            "revenue_accuracy": 0.15,
            "tier_accuracy": 0.15,
            "multiformat_performance": 0.10
        }
        
        health_score = sum(health_factors[factor] * weights[factor] 
                          for factor in health_factors if health_factors[factor] > 0)
        
        # Determine health status
        if health_score >= 0.9:
            status = "excellent"
        elif health_score >= 0.8:
            status = "good"
        elif health_score >= 0.7:
            status = "fair"
        elif health_score >= 0.6:
            status = "poor"
        else:
            status = "critical"
        
        return {
            "status": status,
            "health_score": health_score,
            "health_factors": health_factors,
            "model_type": latest_metrics.model_type.value,
            "creator_economy_optimized": True,
            "last_updated": latest_metrics.timestamp.isoformat(),
            "recommendations": self._get_creator_ai_recommendations(health_factors, latest_metrics)
        }
    
    def _get_creator_ai_recommendations(self, health_factors: Dict[str, float], metrics: CreatorAIMetrics) -> List[str]:
        """Get recommendations for improving Creator Economy AI model performance"""
        recommendations = []
        
        if health_factors["creator_satisfaction"] < 0.7:
            recommendations.append("Retrain creator satisfaction model with recent feedback data")
        
        if health_factors["content_protection"] < 0.9:
            recommendations.append("Enhance content protection algorithms with latest threat patterns")
        
        if health_factors["collaboration_performance"] < 0.7:
            recommendations.append("Update creator matching algorithms with collaboration outcome data")
        
        if health_factors["revenue_accuracy"] < 0.8:
            recommendations.append("Incorporate latest market trends into revenue prediction model")
        
        if health_factors["tier_accuracy"] < 0.85:
            recommendations.append("Recalibrate creator tier prediction with updated business metrics")
        
        if health_factors["multiformat_performance"] < 0.8:
            recommendations.append("Optimize multi-format content analysis for Creator Economy use cases")
        
        return recommendations


# Export the enhanced classes
__all__ = [
    "AIAlertManager",
    "ModelMetrics", 
    "ModelBaseline",
    "DriftDetectionResult",
    "AIModelType",
    "DriftType",
    "ModelHealth",
    # Creator Economy AI enhancements
    "CreatorAIModelType",
    "CreatorAIMetrics",
    "CreatorAIAlertManager"
]