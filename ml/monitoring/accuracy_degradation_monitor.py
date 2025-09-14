"""
Accuracy Degradation Monitor - Model Accuracy Degradation Tracking and Alerting
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade accuracy degradation monitoring with trend analysis, 
early warning systems, and automated remediation triggers.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
from collections import deque, defaultdict
from scipy import stats
import uuid

@dataclass
class AccuracyMeasurement:
    """Individual accuracy measurement."""
    measurement_id: str
    model_id: str
    model_version: str
    timestamp: datetime
    accuracy_score: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    measurement_context: Dict[str, Any]
    ground_truth_source: str
    evaluation_method: str
    domain_specific_metrics: Dict[str, float]

@dataclass
class DegradationAlert:
    """Accuracy degradation alert."""
    alert_id: str
    model_id: str
    alert_level: str  # "warning", "critical", "severe"
    degradation_type: str  # "sudden", "gradual", "oscillating"
    current_accuracy: float
    baseline_accuracy: float
    degradation_percentage: float
    detection_timestamp: datetime
    alert_message: str
    recommended_actions: List[str]
    estimated_impact: Dict[str, Any]

@dataclass
class DegradationTrend:
    """Accuracy degradation trend analysis."""
    trend_id: str
    model_id: str
    trend_direction: str  # "declining", "stable", "improving"
    trend_magnitude: float
    trend_significance: float
    trend_duration_days: int
    projected_accuracy: Dict[str, float]  # time -> accuracy projections
    risk_assessment: Dict[str, Any]
    intervention_recommendations: List[str]

class AccuracyDegradationMonitor:
    """
    Advanced accuracy degradation monitoring and alerting system.
    
    Features:
    - Continuous accuracy tracking with statistical significance testing
    - Multi-window trend analysis (short, medium, long-term)
    - Early warning system with configurable thresholds
    - Degradation pattern recognition (sudden, gradual, cyclical)
    - Creator-domain specific accuracy standards
    - Automated remediation trigger recommendations
    - Performance impact assessment
    - Historical degradation pattern analysis
    """
    
    def __init__(self, monitoring_config -> None: Dict[str, Any] = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = monitoring_config or self._get_default_config()
        
        # Accuracy measurement storage
        self.accuracy_history = defaultdict(deque)  # model_id -> measurements
        self.baseline_accuracies = {}               # model_id -> baseline accuracy
        self.degradation_alerts = defaultdict(list) # model_id -> alerts
        
        # Trend analysis components
        self.trend_analyzers = {}
        self.pattern_detectors = {}
        
        # Alert management
        self.alert_thresholds = {
            "warning": {"relative_drop": 0.05, "absolute_drop": 0.02},
            "critical": {"relative_drop": 0.10, "absolute_drop": 0.05},
            "severe": {"relative_drop": 0.20, "absolute_drop": 0.10}
        }
        
        # Domain-specific accuracy standards
        self.domain_accuracy_standards = {
            "musician": {
                "genre_classification": {"min_acceptable": 0.85, "excellent": 0.92},
                "mood_detection": {"min_acceptable": 0.80, "excellent": 0.88},
                "tempo_estimation": {"min_acceptable": 0.75, "excellent": 0.85},
                "engagement_prediction": {"min_acceptable": 0.70, "excellent": 0.80}
            },
            "blogger": {
                "topic_classification": {"min_acceptable": 0.88, "excellent": 0.95},
                "sentiment_analysis": {"min_acceptable": 0.82, "excellent": 0.90},
                "readability_scoring": {"min_acceptable": 0.75, "excellent": 0.85},
                "seo_optimization": {"min_acceptable": 0.70, "excellent": 0.80}
            },
            "photographer": {
                "aesthetic_scoring": {"min_acceptable": 0.78, "excellent": 0.86},
                "style_classification": {"min_acceptable": 0.85, "excellent": 0.92},
                "composition_analysis": {"min_acceptable": 0.75, "excellent": 0.83},
                "commercial_potential": {"min_acceptable": 0.68, "excellent": 0.78}
            },
            "influencer": {
                "engagement_prediction": {"min_acceptable": 0.72, "excellent": 0.82},
                "viral_potential": {"min_acceptable": 0.65, "excellent": 0.75},
                "brand_alignment": {"min_acceptable": 0.80, "excellent": 0.88},
                "authenticity_scoring": {"min_acceptable": 0.75, "excellent": 0.85}
            }
        }
        
        # Monitoring windows for trend analysis
        self.monitoring_windows = {
            "short_term": timedelta(hours=6),
            "medium_term": timedelta(days=1),
            "long_term": timedelta(days=7),
            "historical": timedelta(days=30)
        }
        
        # Remediation action templates
        self.remediation_actions = {
            "data_drift": [
                "Retrain model with recent data",
                "Update feature preprocessing pipeline",
                "Implement online learning adaptation"
            ],
            "concept_drift": [
                "Perform model architecture review",
                "Implement transfer learning from similar models",
                "Trigger emergency fallback to backup model"
            ],
            "gradual_degradation": [
                "Schedule incremental model update",
                "Increase training data collection",
                "Implement continuous learning pipeline"
            ],
            "sudden_degradation": [
                "Immediate model rollback to stable version",
                "Investigate data quality issues",
                "Activate manual review process"
            ]
        }
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration."""
        return {
            "measurement_frequency_minutes": 30,
            "min_sample_size": 100,
            "baseline_establishment_days": 7,
            "trend_analysis_enabled": True,
            "early_warning_enabled": True,
            "automated_alerts": True,
            "statistical_significance_level": 0.05,
            "min_measurements_for_trend": 10,
            "alert_cooldown_hours": 2
        }
    
    async def record_accuracy_measurement(
        self,
        model_id: str,
        model_version: str,
        accuracy_score: float,
        sample_size: int,
        measurement_context: Dict[str, Any] = None,
        domain_metrics: Dict[str, float] = None
    ) -> str:
        """Record a new accuracy measurement."""
        try:
            measurement_id = str(uuid.uuid4())
            
            # Calculate confidence interval
            confidence_interval = await self._calculate_confidence_interval(
                accuracy_score, sample_size
            )
            
            # Create measurement record
            measurement = AccuracyMeasurement(
                measurement_id=measurement_id,
                model_id=model_id,
                model_version=model_version,
                timestamp=datetime.now(),
                accuracy_score=accuracy_score,
                sample_size=sample_size,
                confidence_interval=confidence_interval,
                measurement_context=measurement_context or {},
                ground_truth_source=measurement_context.get("ground_truth_source", "manual"),
                evaluation_method=measurement_context.get("evaluation_method", "standard"),
                domain_specific_metrics=domain_metrics or {}
            )
            
            # Store measurement
            self.accuracy_history[model_id].append(measurement)
            
            # Maintain history size
            max_history = self.config.get("max_history_size", 1000)
            if len(self.accuracy_history[model_id]) > max_history:
                self.accuracy_history[model_id].popleft()
            
            # Update baseline if needed
            if model_id not in self.baseline_accuracies:
                await self._establish_baseline_accuracy(model_id)
            
            # Check for degradation
            degradation_check = await self._check_for_degradation(model_id, measurement)
            
            # Perform trend analysis
            if self.config.get("trend_analysis_enabled", True):
                await self._analyze_accuracy_trends(model_id)
            
            # Log measurement
            self.logger.debug(f"Accuracy recorded: {model_id} = {accuracy_score:.3f} "
                            f"(n={sample_size})")
            
            return measurement_id
            
        except Exception as e:
            self.logger.error(f"Error recording accuracy measurement: {e}")
            raise
    
    async def detect_accuracy_degradation(
        self,
        model_id: str,
        analysis_window: str = "medium_term"
    ) -> List[DegradationAlert]:
        """Detect accuracy degradation patterns."""
        try:
            if model_id not in self.accuracy_history:
                return []
            
            # Get analysis window
            window_duration = self.monitoring_windows.get(
                analysis_window, self.monitoring_windows["medium_term"]
            )
            
            # Filter measurements within window
            cutoff_time = datetime.now() - window_duration
            recent_measurements = [
                m for m in self.accuracy_history[model_id]
                if m.timestamp >= cutoff_time
            ]
            
            if len(recent_measurements) < self.config.get("min_measurements_for_trend", 10):
                return []
            
            alerts = []
            
            # Sudden degradation detection
            sudden_alert = await self._detect_sudden_degradation(
                model_id, recent_measurements
            )
            if sudden_alert:
                alerts.append(sudden_alert)
            
            # Gradual degradation detection
            gradual_alert = await self._detect_gradual_degradation(
                model_id, recent_measurements
            )
            if gradual_alert:
                alerts.append(gradual_alert)
            
            # Oscillating pattern detection
            oscillating_alert = await self._detect_oscillating_degradation(
                model_id, recent_measurements
            )
            if oscillating_alert:
                alerts.append(oscillating_alert)
            
            # Performance threshold breach detection
            threshold_alert = await self._detect_threshold_breach(
                model_id, recent_measurements
            )
            if threshold_alert:
                alerts.append(threshold_alert)
            
            # Store alerts
            self.degradation_alerts[model_id].extend(alerts)
            
            # Send notifications if configured
            if self.config.get("automated_alerts", True) and alerts:
                await self._send_degradation_alerts(alerts)
            
            self.logger.info(f"Degradation detection completed: {len(alerts)} alerts for {model_id}")
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error detecting accuracy degradation: {e}")
            return []
    
    async def analyze_degradation_trends(
        self,
        model_id: str,
        forecast_days: int = 7
    ) -> DegradationTrend:
        """Analyze accuracy degradation trends and forecast future performance."""
        try:
            if model_id not in self.accuracy_history:
                raise ValueError(f"No accuracy history found for model: {model_id}")
            
            measurements = list(self.accuracy_history[model_id])
            if len(measurements) < 5:
                raise ValueError("Insufficient measurements for trend analysis")
            
            trend_id = str(uuid.uuid4())
            
            # Extract time series data
            timestamps = [m.timestamp for m in measurements]
            accuracies = [m.accuracy_score for m in measurements]
            
            # Trend direction analysis
            trend_direction, trend_magnitude = await self._calculate_trend_direction(
                timestamps, accuracies
            )
            
            # Statistical significance of trend
            trend_significance = await self._calculate_trend_significance(
                timestamps, accuracies
            )
            
            # Calculate trend duration
            trend_duration = (timestamps[-1] - timestamps[0]).days
            
            # Forecast future accuracy
            projected_accuracy = await self._forecast_accuracy(
                timestamps, accuracies, forecast_days
            )
            
            # Risk assessment
            risk_assessment = await self._assess_degradation_risk(
                model_id, trend_direction, trend_magnitude, projected_accuracy
            )
            
            # Generate intervention recommendations
            intervention_recommendations = await self._generate_intervention_recommendations(
                model_id, trend_direction, trend_magnitude, risk_assessment
            )
            
            # Create trend analysis result
            trend_analysis = DegradationTrend(
                trend_id=trend_id,
                model_id=model_id,
                trend_direction=trend_direction,
                trend_magnitude=trend_magnitude,
                trend_significance=trend_significance,
                trend_duration_days=trend_duration,
                projected_accuracy=projected_accuracy,
                risk_assessment=risk_assessment,
                intervention_recommendations=intervention_recommendations
            )
            
            self.logger.info(f"Trend analysis completed: {model_id} - {trend_direction} trend")
            return trend_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing degradation trends: {e}")
            raise
    
    async def generate_degradation_report(
        self,
        model_ids: List[str] = None,
        report_period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive degradation monitoring report."""
        try:
            if model_ids is None:
                model_ids = list(self.accuracy_history.keys())
            
            report = {
                "report_id": str(uuid.uuid4()),
                "generation_timestamp": datetime.now().isoformat(),
                "report_period_days": report_period_days,
                "models_analyzed": len(model_ids),
                "model_summaries": {},
                "overall_statistics": {},
                "critical_alerts": [],
                "recommendations": []
            }
            
            # Analyze each model
            all_alerts = []
            degradation_counts = {"warning": 0, "critical": 0, "severe": 0}
            
            for model_id in model_ids:
                model_summary = await self._generate_model_summary(
                    model_id, report_period_days
                )
                report["model_summaries"][model_id] = model_summary
                
                # Collect alerts
                model_alerts = model_summary.get("recent_alerts", [])
                all_alerts.extend(model_alerts)
                
                # Count degradation by severity
                for alert in model_alerts:
                    severity = alert.get("alert_level", "warning")
                    degradation_counts[severity] += 1
            
            # Overall statistics
            report["overall_statistics"] = {
                "total_alerts": len(all_alerts),
                "degradation_by_severity": degradation_counts,
                "models_with_degradation": len([
                    mid for mid in model_ids 
                    if report["model_summaries"][mid]["has_degradation"]
                ]),
                "average_accuracy_change": np.mean([
                    report["model_summaries"][mid]["accuracy_change_percentage"]
                    for mid in model_ids
                ]),
                "models_requiring_attention": len([
                    mid for mid in model_ids
                    if report["model_summaries"][mid]["requires_attention"]
                ])
            }
            
            # Identify critical alerts
            report["critical_alerts"] = [
                alert for alert in all_alerts
                if alert.get("alert_level") in ["critical", "severe"]
            ]
            
            # Generate overall recommendations
            overall_recommendations = await self._generate_overall_recommendations(
                report["model_summaries"], report["overall_statistics"]
            )
            report["recommendations"] = overall_recommendations
            
            # Save report
            await self._save_degradation_report(report)
            
            self.logger.info(f"Degradation report generated: {len(model_ids)} models analyzed")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating degradation report: {e}")
            raise
    
    async def _calculate_confidence_interval(
        self,
        accuracy: float,
        sample_size: int,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate confidence interval for accuracy measurement."""
        try:
            if sample_size <= 1:
                return (accuracy, accuracy)
            
            # Use normal approximation for binomial proportion
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            standard_error = np.sqrt((accuracy * (1 - accuracy)) / sample_size)
            margin_of_error = z_score * standard_error
            
            lower_bound = max(0.0, accuracy - margin_of_error)
            upper_bound = min(1.0, accuracy + margin_of_error)
            
            return (lower_bound, upper_bound)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence interval: {e}")
            return (accuracy, accuracy)
    
    async def _detect_sudden_degradation(
        self,
        model_id: str,
        measurements: List[AccuracyMeasurement]
    ) -> Optional[DegradationAlert]:
        """Detect sudden accuracy drops."""
        try:
            if len(measurements) < 3:
                return None
            
            # Check last measurement against baseline
            latest_measurement = measurements[-1]
            baseline_accuracy = self.baseline_accuracies.get(model_id)
            
            if baseline_accuracy is None:
                return None
            
            # Calculate degradation
            absolute_drop = baseline_accuracy - latest_measurement.accuracy_score
            relative_drop = absolute_drop / baseline_accuracy
            
            # Check thresholds
            alert_level = None
            if (relative_drop >= self.alert_thresholds["severe"]["relative_drop"] or
                absolute_drop >= self.alert_thresholds["severe"]["absolute_drop"]):
                alert_level = "severe"
            elif (relative_drop >= self.alert_thresholds["critical"]["relative_drop"] or
                  absolute_drop >= self.alert_thresholds["critical"]["absolute_drop"]):
                alert_level = "critical"
            elif (relative_drop >= self.alert_thresholds["warning"]["relative_drop"] or
                  absolute_drop >= self.alert_thresholds["warning"]["absolute_drop"]):
                alert_level = "warning"
            
            if alert_level:
                # Generate alert
                alert = DegradationAlert(
                    alert_id=str(uuid.uuid4()),
                    model_id=model_id,
                    alert_level=alert_level,
                    degradation_type="sudden",
                    current_accuracy=latest_measurement.accuracy_score,
                    baseline_accuracy=baseline_accuracy,
                    degradation_percentage=relative_drop * 100,
                    detection_timestamp=datetime.now(),
                    alert_message=f"Sudden accuracy drop detected: {relative_drop*100:.1f}% decrease",
                    recommended_actions=self.remediation_actions["sudden_degradation"],
                    estimated_impact=await self._estimate_degradation_impact(
                        model_id, relative_drop
                    )
                )
                
                return alert
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting sudden degradation: {e}")
            return None

# Example usage and testing
async def main() -> None:
    """Example usage of AccuracyDegradationMonitor."""
    monitor = AccuracyDegradationMonitor()
    
    model_id = "musician-genre-classifier"
    
    # Simulate accuracy measurements over time
    base_accuracy = 0.90
    measurements = []
    
    # Simulate 30 days of measurements with gradual degradation
    for day in range(30):
        # Add some noise and gradual degradation
        noise = np.random.normal(0, 0.02)
        degradation = day * 0.001  # 0.1% degradation per day
        accuracy = max(0.0, min(1.0, base_accuracy - degradation + noise))
        
        sample_size = np.random.randint(100, 500)
        
        measurement_id = await monitor.record_accuracy_measurement(
            model_id=model_id,
            model_version="v1.0",
            accuracy_score=accuracy,
            sample_size=sample_size,
            measurement_context={
                "evaluation_method": "holdout",
                "ground_truth_source": "expert_labels"
            },
            domain_metrics={
                "genre_accuracy": accuracy,
                "confidence_score": 0.85
            }
        )
        
        measurements.append((day, accuracy, measurement_id))
    
    print(f"Recorded {len(measurements)} accuracy measurements")
    
    # Detect degradation
    alerts = await monitor.detect_accuracy_degradation(model_id, "long_term")
    
    print(f"\nDegradation alerts: {len(alerts)}")
    for alert in alerts:
        print(f"- {alert.alert_level.upper()}: {alert.alert_message}")
        print(f"  Degradation: {alert.degradation_percentage:.1f}%")
        print(f"  Actions: {len(alert.recommended_actions)} recommended")
    
    # Analyze trends
    trend_analysis = await monitor.analyze_degradation_trends(model_id, forecast_days=7)
    
    print(f"\nTrend analysis:")
    print(f"- Direction: {trend_analysis.trend_direction}")
    print(f"- Magnitude: {trend_analysis.trend_magnitude:.3f}")
    print(f"- Significance: {trend_analysis.trend_significance:.3f}")
    print(f"- Duration: {trend_analysis.trend_duration_days} days")
    print(f"- Interventions: {len(trend_analysis.intervention_recommendations)}")
    
    # Generate report
    report = await monitor.generate_degradation_report([model_id], report_period_days=30)
    
    print(f"\nDegradation report:")
    print(f"- Models analyzed: {report['models_analyzed']}")
    print(f"- Total alerts: {report['overall_statistics']['total_alerts']}")
    print(f"- Critical alerts: {len(report['critical_alerts'])}")
    print(f"- Recommendations: {len(report['recommendations'])}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())