"""
Intelligent Monitoring & Predictive Analytics Engine

Advanced AI-powered monitoring system with predictive capabilities,
anomaly detection, automated incident response, and proactive
system optimization for the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL / LEGAL WARNING 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from uuid import uuid4
import threading
import pickle
import hashlib

# Machine learning imports for predictive analytics
try:
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler, RobustScaler
    from sklearn.decomposition import PCA
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.model_selection import train_test_split
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    from scipy import stats
    from scipy.signal import find_peaks, savgol_filter
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MonitoringScope(Enum):
    """Monitoring scope types"""
    SYSTEM_HEALTH = "system_health"
    APPLICATION_PERFORMANCE = "application_performance"
    USER_BEHAVIOR = "user_behavior"
    BUSINESS_METRICS = "business_metrics"
    SECURITY_EVENTS = "security_events"
    INFRASTRUCTURE = "infrastructure"
    AI_MODEL_PERFORMANCE = "ai_model_performance"
    CONTENT_PROTECTION = "content_protection"


class PredictionType(Enum):
    """Types of predictions"""
    ANOMALY_DETECTION = "anomaly_detection"
    CAPACITY_PLANNING = "capacity_planning"
    PERFORMANCE_FORECASTING = "performance_forecasting"
    USER_BEHAVIOR_PREDICTION = "user_behavior_prediction"
    REVENUE_FORECASTING = "revenue_forecasting"
    CHURN_PREDICTION = "churn_prediction"
    CONTENT_VIRALITY = "content_virality"
    SECURITY_THREAT = "security_threat"


class IncidentStatus(Enum):
    """Incident status types"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    ACKNOWLEDGED = "acknowledged"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class MonitoringMetric:
    """Monitoring metric definition"""
    metric_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    scope: MonitoringScope = MonitoringScope.SYSTEM_HEALTH
    value: float = 0.0
    unit: str = ""
    threshold_warning: float = 0.0
    threshold_critical: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    source: str = ""
    
    def is_warning(self) -> bool:
        """Check if metric value exceeds warning threshold"""



        return self.value >= self.threshold_warning
    
    def is_critical(self) -> bool:
        """Check if metric value exceeds critical threshold"""



        return self.value >= self.threshold_critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'status': 'critical' if self.is_critical() else 'warning' if self.is_warning() else 'normal'
        }


@dataclass
class PredictiveAlert:
    """Predictive alert structure"""
    alert_id: str = field(default_factory=lambda: str(uuid4()))
    prediction_type: PredictionType = PredictionType.ANOMALY_DETECTION
    title: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    confidence: float = 0.0
    predicted_time: Optional[datetime] = None
    affected_metrics: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            **asdict(self),
            'created_at': self.created_at.isoformat(),
            'predicted_time': self.predicted_time.isoformat() if self.predicted_time else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class Incident:
    """Incident tracking structure"""
    incident_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: IncidentStatus = IncidentStatus.DETECTED
    affected_services: List[str] = field(default_factory=list)
    root_cause: str = ""
    resolution: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    assigned_to: str = ""
    tags: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_timeline_event(self, event: str, details: str = ""):
        """Add event to incident timeline"""
        self.timeline.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': event,
            'details': details
        })
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            **asdict(self),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class AnomalyDetector:
    """Advanced anomaly detection using multiple algorithms"""
    
    def __init__(self, sensitivity: float = 0.1):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sensitivity = sensitivity
        self.models = {}
        self.baseline_data = defaultdict(list)
        self.detection_history = defaultdict(list)
        
    async def detect_anomalies(self, metrics: List[MonitoringMetric]) -> List[PredictiveAlert]:
        """Detect anomalies in metrics using multiple algorithms"""



        try:
            anomalies = []
            
            if not HAS_SKLEARN:
                self.logger.warning("Scikit-learn not available, using statistical detection")
                return await self._statistical_anomaly_detection(metrics)
            
            # Group metrics by name for time series analysis
            metric_groups = defaultdict(list)
            for metric in metrics:
                metric_groups[metric.name].append(metric)
            
            for metric_name, metric_list in metric_groups.items():
                if len(metric_list) < 10:  # Need sufficient data
                    continue
                
                # Sort by timestamp
                metric_list.sort(key=lambda x: x.timestamp)
                values = [m.value for m in metric_list]
                
                # Multiple detection methods
                iso_anomalies = await self._isolation_forest_detection(metric_name, values)
                stat_anomalies = await self._statistical_detection(metric_name, values)
                pattern_anomalies = await self._pattern_based_detection(metric_name, metric_list)
                
                # Combine results
                all_anomalies = iso_anomalies + stat_anomalies + pattern_anomalies
                
                # Remove duplicates and filter by confidence
                unique_anomalies = self._deduplicate_anomalies(all_anomalies)
                anomalies.extend(unique_anomalies)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {str(e)}")
            return []
    
    async def _isolation_forest_detection(self, metric_name: str, values: List[float]) -> List[PredictiveAlert]:
        """Anomaly detection using Isolation Forest"""



        try:
            if len(values) < 20:
                return []
            
            # Prepare data
            X = np.array(values).reshape(-1, 1)
            
            # Train Isolation Forest
            iso_forest = IsolationForest(contamination=self.sensitivity, random_state=42)
            anomaly_labels = iso_forest.fit_predict(X)
            anomaly_scores = iso_forest.score_samples(X)
            
            anomalies = []
            for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
                if label == -1:  # Anomaly detected
                    confidence = abs(score) * 100
                    
                    alert = PredictiveAlert(
                        prediction_type=PredictionType.ANOMALY_DETECTION,
                        title=f"Anomaly detected in {metric_name}",
                        description=f"Unusual value {values[i]:.2f} detected using Isolation Forest",
                        severity=self._determine_severity(confidence),
                        confidence=confidence,
                        affected_metrics=[metric_name],
                        supporting_data={
                            'value': values[i],
                            'anomaly_score': float(score),
                            'detection_method': 'isolation_forest'
                        }
                    )
                    
                    anomalies.append(alert)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Isolation Forest detection failed: {str(e)}")
            return []
    
    async def _statistical_detection(self, metric_name: str, values: List[float]) -> List[PredictiveAlert]:
        """Statistical anomaly detection using Z-score and IQR"""



        try:
            if len(values) < 10:
                return []
            
            values_array = np.array(values)
            anomalies = []
            
            # Z-score method
            mean_val = np.mean(values_array)
            std_val = np.std(values_array)
            
            if std_val > 0:
                z_scores = np.abs((values_array - mean_val) / std_val)
                z_threshold = 3.0  # 3-sigma rule
                
                z_anomalies = np.where(z_scores > z_threshold)[0]
                
                for idx in z_anomalies:
                    confidence = min((z_scores[idx] / z_threshold) * 100, 100)
                    
                    alert = PredictiveAlert(
                        prediction_type=PredictionType.ANOMALY_DETECTION,
                        title=f"Statistical anomaly in {metric_name}",
                        description=f"Value {values[idx]:.2f} exceeds {z_threshold}-sigma threshold",
                        severity=self._determine_severity(confidence),
                        confidence=confidence,
                        affected_metrics=[metric_name],
                        supporting_data={
                            'value': values[idx],
                            'z_score': float(z_scores[idx]),
                            'detection_method': 'z_score'
                        }
                    )
                    
                    anomalies.append(alert)
            
            # IQR method
            q75, q25 = np.percentile(values_array, [75, 25])
            iqr = q75 - q25
            
            if iqr > 0:
                lower_bound = q25 - (1.5 * iqr)
                upper_bound = q75 + (1.5 * iqr)
                
                iqr_anomalies = np.where((values_array < lower_bound) | (values_array > upper_bound))[0]
                
                for idx in iqr_anomalies:
                    # Calculate distance from bounds as confidence
                    if values[idx] < lower_bound:
                        distance = abs(values[idx] - lower_bound)
                    else:
                        distance = abs(values[idx] - upper_bound)
                    
                    confidence = min((distance / iqr) * 50, 100)
                    
                    alert = PredictiveAlert(
                        prediction_type=PredictionType.ANOMALY_DETECTION,
                        title=f"IQR anomaly in {metric_name}",
                        description=f"Value {values[idx]:.2f} outside IQR bounds",
                        severity=self._determine_severity(confidence),
                        confidence=confidence,
                        affected_metrics=[metric_name],
                        supporting_data={
                            'value': values[idx],
                            'iqr_distance': distance,
                            'detection_method': 'iqr'
                        }
                    )
                    
                    anomalies.append(alert)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Statistical detection failed: {str(e)}")
            return []
    
    async def _pattern_based_detection(self, metric_name: str, metrics: List[MonitoringMetric]) -> List[PredictiveAlert]:
        """Pattern-based anomaly detection"""



        try:
            if len(metrics) < 20:
                return []
            
            anomalies = []
            values = [m.value for m in metrics]
            timestamps = [m.timestamp for m in metrics]
            
            # Detect sudden spikes or drops
            if HAS_SCIPY:
                # Smooth the signal to remove noise
                smoothed = savgol_filter(values, window_length=min(11, len(values)//2*2+1), polyorder=3)
                
                # Find peaks (spikes)
                peaks, peak_properties = find_peaks(smoothed, prominence=np.std(values))
                
                for peak_idx in peaks:
                    prominence = peak_properties['prominences'][list(peaks).index(peak_idx)]
                    if prominence > 2 * np.std(values):
                        confidence = min((prominence / np.std(values)) * 30, 100)
                        
                        alert = PredictiveAlert(
                            prediction_type=PredictionType.ANOMALY_DETECTION,
                            title=f"Sudden spike in {metric_name}",
                            description=f"Significant peak detected at {timestamps[peak_idx]}",
                            severity=self._determine_severity(confidence),
                            confidence=confidence,
                            affected_metrics=[metric_name],
                            supporting_data={
                                'peak_value': values[peak_idx],
                                'prominence': float(prominence),
                                'detection_method': 'peak_detection'
                            }
                        )
                        
                        anomalies.append(alert)
                
                # Find valleys (drops)
                inverted_values = [-v for v in smoothed]
                valleys, valley_properties = find_peaks(inverted_values, prominence=np.std(values))
                
                for valley_idx in valleys:
                    prominence = valley_properties['prominences'][list(valleys).index(valley_idx)]
                    if prominence > 2 * np.std(values):
                        confidence = min((prominence / np.std(values)) * 30, 100)
                        
                        alert = PredictiveAlert(
                            prediction_type=PredictionType.ANOMALY_DETECTION,
                            title=f"Sudden drop in {metric_name}",
                            description=f"Significant valley detected at {timestamps[valley_idx]}",
                            severity=self._determine_severity(confidence),
                            confidence=confidence,
                            affected_metrics=[metric_name],
                            supporting_data={
                                'valley_value': values[valley_idx],
                                'prominence': float(prominence),
                                'detection_method': 'valley_detection'
                            }
                        )
                        
                        anomalies.append(alert)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Pattern-based detection failed: {str(e)}")
            return []
    
    async def _statistical_anomaly_detection(self, metrics: List[MonitoringMetric]) -> List[PredictiveAlert]:
        """Fallback statistical anomaly detection when ML libraries unavailable"""



        try:
            anomalies = []
            
            # Group metrics by name
            metric_groups = defaultdict(list)
            for metric in metrics:
                metric_groups[metric.name].append(metric.value)
            
            for metric_name, values in metric_groups.items():
                if len(values) < 5:
                    continue
                
                mean_val = np.mean(values)
                std_val = np.std(values)
                
                if std_val == 0:
                    continue
                
                # Simple 2-sigma rule
                threshold = 2.0
                
                for i, value in enumerate(values):
                    z_score = abs((value - mean_val) / std_val)
                    
                    if z_score > threshold:
                        confidence = min((z_score / threshold) * 100, 100)
                        
                        alert = PredictiveAlert(
                            prediction_type=PredictionType.ANOMALY_DETECTION,
                            title=f"Simple anomaly in {metric_name}",
                            description=f"Value {value:.2f} exceeds statistical threshold",
                            severity=self._determine_severity(confidence),
                            confidence=confidence,
                            affected_metrics=[metric_name],
                            supporting_data={
                                'value': value,
                                'z_score': z_score,
                                'detection_method': 'simple_statistical'
                            }
                        )
                        
                        anomalies.append(alert)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Statistical anomaly detection failed: {str(e)}")
            return []
    
    def _determine_severity(self, confidence: float) -> AlertSeverity:
        """Determine alert severity based on confidence"""
        if confidence >= 90:
            return AlertSeverity.CRITICAL
        elif confidence >= 70:
            return AlertSeverity.HIGH
        elif confidence >= 50:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _deduplicate_anomalies(self, anomalies: List[PredictiveAlert]) -> List[PredictiveAlert]:
        """Remove duplicate anomalies and keep highest confidence ones"""
        if not anomalies:
            return []
        
        # Group by affected metrics and time proximity
        grouped = defaultdict(list)
        
        for anomaly in anomalies:
            key = tuple(sorted(anomaly.affected_metrics))
            grouped[key].append(anomaly)
        
        deduplicated = []
        for group in grouped.values():
            if len(group) == 1:
                deduplicated.extend(group)
            else:
                # Keep the highest confidence anomaly
                best_anomaly = max(group, key=lambda x: x.confidence)
                deduplicated.append(best_anomaly)
        
        return deduplicated


class PredictiveEngine:
    """Advanced predictive analytics engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.prediction_models = {}
        self.training_data = defaultdict(list)
        self.prediction_history = defaultdict(list)
        
    async def predict_capacity_needs(self, resource_metrics: List[MonitoringMetric], 
                                   forecast_horizon: timedelta = timedelta(days=7)) -> List[PredictiveAlert]:
        """Predict future capacity needs based on current trends"""



        try:
            predictions = []
            
            if not HAS_SKLEARN:
                return await self._simple_capacity_prediction(resource_metrics, forecast_horizon)
            
            # Group metrics by resource type
            resource_groups = defaultdict(list)
            for metric in resource_metrics:
                resource_groups[metric.name].append(metric)
            
            for resource_name, metrics in resource_groups.items():
                if len(metrics) < 20:  # Need sufficient historical data
                    continue
                
                # Sort by timestamp
                metrics.sort(key=lambda x: x.timestamp)
                
                # Prepare time series data
                values = [m.value for m in metrics]
                timestamps = [(m.timestamp - metrics[0].timestamp).total_seconds() / 3600 for m in metrics]  # Hours
                
                # Train prediction model
                if len(values) >= 10:
                    prediction = await self._forecast_resource_usage(
                        resource_name, timestamps, values, forecast_horizon
                    )
                    
                    if prediction:
                        predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Capacity prediction failed: {str(e)}")
            return []
    
    async def _forecast_resource_usage(self, resource_name: str, timestamps: List[float], 
                                     values: List[float], horizon: timedelta) -> Optional[PredictiveAlert]:
        """Forecast resource usage using regression"""



        try:
            X = np.array(timestamps).reshape(-1, 1)
            y = np.array(values)
            
            # Train Random Forest model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Predict future values
            future_hours = horizon.total_seconds() / 3600
            future_timestamps = np.arange(
                timestamps[-1] + 1, 
                timestamps[-1] + future_hours + 1, 
                1
            ).reshape(-1, 1)
            
            predicted_values = model.predict(future_timestamps)
            
            # Check if predicted values exceed thresholds
            max_predicted = np.max(predicted_values)
            current_max = np.max(values)
            
            # Determine if capacity alert is needed
            if max_predicted > current_max * 1.2:  # 20% increase threshold
                confidence = min(((max_predicted - current_max) / current_max) * 100, 100)
                
                predicted_time = datetime.utcnow() + timedelta(
                    hours=future_timestamps[np.argmax(predicted_values)][0] - timestamps[-1]
                )
                
                alert = PredictiveAlert(
                    prediction_type=PredictionType.CAPACITY_PLANNING,
                    title=f"Capacity alert for {resource_name}",
                    description=f"Predicted peak usage: {max_predicted:.2f} (current max: {current_max:.2f})",
                    severity=self._determine_capacity_severity(max_predicted, current_max),
                    confidence=confidence,
                    predicted_time=predicted_time,
                    affected_metrics=[resource_name],
                    recommended_actions=[
                        f"Consider scaling {resource_name} resources",
                        "Monitor usage trends closely",
                        "Review capacity allocation policies"
                    ],
                    supporting_data={
                        'current_max': current_max,
                        'predicted_max': float(max_predicted),
                        'forecast_horizon_hours': future_hours,
                        'prediction_model': 'random_forest'
                    }
                )
                
                return alert
            
            return None
            
        except Exception as e:
            self.logger.error(f"Resource usage forecasting failed: {str(e)}")
            return None
    
    async def predict_user_churn(self, user_metrics: List[Dict[str, Any]]) -> List[PredictiveAlert]:
        """Predict users at risk of churning"""



        try:
            if not user_metrics or not HAS_SKLEARN:
                return []
            
            df = pd.DataFrame(user_metrics)
            churn_predictions = []
            
            # Required features for churn prediction
            required_features = ['days_since_last_visit', 'engagement_score', 'session_count']
            available_features = [f for f in required_features if f in df.columns]
            
            if len(available_features) < 2:
                return []
            
            # Simple churn risk scoring
            for _, user in df.iterrows():
                churn_score = 0
                risk_factors = []
                
                # Days since last visit
                if 'days_since_last_visit' in user and user['days_since_last_visit'] > 14:
                    churn_score += 30
                    risk_factors.append("Extended absence (>14 days)")
                
                # Low engagement
                if 'engagement_score' in user and user['engagement_score'] < 30:
                    churn_score += 25
                    risk_factors.append("Low engagement score")
                
                # Reduced session frequency
                if 'session_count' in user and user['session_count'] < 5:
                    churn_score += 20
                    risk_factors.append("Low session frequency")
                
                # Declining metrics trend
                if 'engagement_trend' in user and user['engagement_trend'] == 'declining':
                    churn_score += 25
                    risk_factors.append("Declining engagement trend")
                
                if churn_score >= 50:  # High churn risk threshold
                    alert = PredictiveAlert(
                        prediction_type=PredictionType.CHURN_PREDICTION,
                        title=f"High churn risk user detected",
                        description=f"User at high risk of churning (score: {churn_score})",
                        severity=AlertSeverity.HIGH if churn_score >= 70 else AlertSeverity.MEDIUM,
                        confidence=churn_score,
                        affected_metrics=['user_retention'],
                        recommended_actions=[
                            "Implement targeted retention campaign",
                            "Send personalized re-engagement content",
                            "Offer special incentives or features",
                            "Conduct user feedback survey"
                        ],
                        supporting_data={
                            'user_id': user.get('user_id', 'unknown'),
                            'churn_score': churn_score,
                            'risk_factors': risk_factors,
                            'prediction_model': 'risk_scoring'
                        }
                    )
                    
                    churn_predictions.append(alert)
            
            return churn_predictions
            
        except Exception as e:
            self.logger.error(f"Churn prediction failed: {str(e)}")
            return []
    
    async def predict_content_virality(self, content_metrics: List[Dict[str, Any]]) -> List[PredictiveAlert]:
        """Predict content with viral potential"""



        try:
            if not content_metrics:
                return []
            
            df = pd.DataFrame(content_metrics)
            viral_predictions = []
            
            for _, content in df.iterrows():
                viral_score = 0
                viral_indicators = []
                
                # Early engagement velocity
                if 'engagement_velocity' in content and content['engagement_velocity'] > 100:
                    viral_score += 30
                    viral_indicators.append("High engagement velocity")
                
                # Share rate
                if 'share_rate' in content and content['share_rate'] > 10:
                    viral_score += 25
                    viral_indicators.append("High share rate")
                
                # Comment engagement
                if 'comment_rate' in content and content['comment_rate'] > 15:
                    viral_score += 20
                    viral_indicators.append("High comment engagement")
                
                # Cross-platform traction
                if 'platform_spread' in content and content['platform_spread'] > 2:
                    viral_score += 25
                    viral_indicators.append("Multi-platform traction")
                
                if viral_score >= 60:  # Viral potential threshold
                    alert = PredictiveAlert(
                        prediction_type=PredictionType.CONTENT_VIRALITY,
                        title=f"High viral potential content detected",
                        description=f"Content shows strong viral indicators (score: {viral_score})",
                        severity=AlertSeverity.INFO,
                        confidence=viral_score,
                        affected_metrics=['content_performance'],
                        recommended_actions=[
                            "Boost content promotion budget",
                            "Cross-promote on all platforms",
                            "Engage actively with comments",
                            "Prepare for increased traffic load",
                            "Monitor for content protection needs"
                        ],
                        supporting_data={
                            'content_id': content.get('content_id', 'unknown'),
                            'viral_score': viral_score,
                            'viral_indicators': viral_indicators,
                            'prediction_model': 'viral_scoring'
                        }
                    )
                    
                    viral_predictions.append(alert)
            
            return viral_predictions
            
        except Exception as e:
            self.logger.error(f"Content virality prediction failed: {str(e)}")
            return []
    
    async def _simple_capacity_prediction(self, metrics: List[MonitoringMetric], 
                                        horizon: timedelta) -> List[PredictiveAlert]:
        """Simple capacity prediction without ML libraries"""



        try:
            predictions = []
            
            # Group metrics by name
            metric_groups = defaultdict(list)
            for metric in metrics:
                metric_groups[metric.name].append(metric)
            
            for metric_name, metric_list in metric_groups.items():
                if len(metric_list) < 5:
                    continue
                
                # Sort by timestamp
                metric_list.sort(key=lambda x: x.timestamp)
                values = [m.value for m in metric_list]
                
                # Simple linear trend
                if len(values) >= 3:
                    recent_avg = np.mean(values[-3:])
                    earlier_avg = np.mean(values[:3])
                    
                    if recent_avg > earlier_avg * 1.2:  # 20% increase
                        predicted_increase = (recent_avg - earlier_avg) / len(values)
                        future_hours = horizon.total_seconds() / 3600
                        predicted_max = recent_avg + (predicted_increase * future_hours)
                        
                        confidence = min(((recent_avg - earlier_avg) / earlier_avg) * 100, 100)
                        
                        alert = PredictiveAlert(
                            prediction_type=PredictionType.CAPACITY_PLANNING,
                            title=f"Simple capacity forecast for {metric_name}",
                            description=f"Linear trend suggests increase to {predicted_max:.2f}",
                            severity=self._determine_capacity_severity(predicted_max, recent_avg),
                            confidence=confidence,
                            affected_metrics=[metric_name],
                            supporting_data={
                                'current_avg': recent_avg,
                                'predicted_max': float(predicted_max),
                                'prediction_model': 'simple_linear'
                            }
                        )
                        
                        predictions.append(alert)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Simple capacity prediction failed: {str(e)}")
            return []
    
    def _determine_capacity_severity(self, predicted: float, current: float) -> AlertSeverity:
        """Determine severity based on predicted capacity increase"""
        increase_ratio = predicted / current if current > 0 else 1
        
        if increase_ratio >= 2.0:  # 100% increase
            return AlertSeverity.CRITICAL
        elif increase_ratio >= 1.5:  # 50% increase
            return AlertSeverity.HIGH
        elif increase_ratio >= 1.2:  # 20% increase
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW


class IncidentManager:
    """Intelligent incident management and response"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.active_incidents = {}
        self.incident_history = []
        self.escalation_rules = {}
        self.auto_response_rules = {}
        
    async def create_incident(self, alert: PredictiveAlert, 
                            additional_context: Optional[Dict[str, Any]] = None) -> Incident:
        """Create incident from alert"""



        try:
            incident = Incident(
                title=alert.title,
                description=alert.description,
                severity=alert.severity,
                affected_services=alert.affected_metrics,
                tags=[alert.prediction_type.value]
            )
            
            # Add additional context if provided
            if additional_context:
                incident.description += f"\n\nAdditional context: {json.dumps(additional_context, indent=2)}"
            
            # Add to active incidents
            self.active_incidents[incident.incident_id] = incident
            
            # Add initial timeline event
            incident.add_timeline_event("Incident created", f"Auto-created from {alert.prediction_type.value} alert")
            
            # Check for auto-response rules
            await self._check_auto_response(incident)
            
            self.logger.info(f"Created incident: {incident.title} ({incident.incident_id})")
            return incident
            
        except Exception as e:
            self.logger.error(f"Incident creation failed: {str(e)}")
            raise
    
    async def update_incident_status(self, incident_id: str, 
                                   new_status: IncidentStatus,
                                   notes: str = "") -> bool:
        """Update incident status"""



        try:
            if incident_id not in self.active_incidents:
                return False
            
            incident = self.active_incidents[incident_id]
            old_status = incident.status
            incident.status = new_status
            
            # Add timeline event
            status_change_msg = f"Status changed from {old_status.value} to {new_status.value}"
            incident.add_timeline_event("Status update", f"{status_change_msg}. {notes}")
            
            # Handle status-specific actions
            if new_status == IncidentStatus.RESOLVED:
                incident.resolved_at = datetime.utcnow()
                await self._handle_incident_resolution(incident)
            elif new_status == IncidentStatus.CLOSED:
                self._archive_incident(incident)
            
            self.logger.info(f"Updated incident {incident_id} status to {new_status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Incident status update failed: {str(e)}")
            return False
    
    async def _check_auto_response(self, incident: Incident):
        """Check and execute auto-response rules"""



        try:
            # Example auto-response rules
            if incident.severity == AlertSeverity.CRITICAL:
                # Auto-escalate critical incidents
                incident.add_timeline_event("Auto-escalation", "Critical incident auto-escalated to on-call team")
                
                # Could trigger:
                # - Page on-call engineer
                # - Create war room
                # - Auto-scale resources
                # - Activate backup systems
            
            elif "capacity" in incident.title.lower():
                # Auto-response for capacity issues
                incident.add_timeline_event("Auto-response", "Capacity alert triggered auto-scaling evaluation")
                
                # Could trigger:
                # - Auto-scaling actions
                # - Load balancer adjustments
                # - Resource reallocation
            
            elif "churn" in incident.title.lower():
                # Auto-response for churn predictions
                incident.add_timeline_event("Auto-response", "Churn prediction triggered retention workflow")
                
                # Could trigger:
                # - Retention campaign activation
                # - Personalized content delivery
                # - Customer success team notification
            
        except Exception as e:
            self.logger.error(f"Auto-response check failed: {str(e)}")
    
    async def _handle_incident_resolution(self, incident: Incident):
        """Handle incident resolution actions"""



        try:
            # Post-resolution actions
            incident.add_timeline_event("Resolution actions", "Executing post-resolution procedures")
            
            # Could include:
            # - Notifying stakeholders
            # - Updating monitoring thresholds
            # - Scheduling post-mortem
            # - Updating runbooks
            # - Training model updates
            
            self.logger.info(f"Handled resolution for incident {incident.incident_id}")
            
        except Exception as e:
            self.logger.error(f"Incident resolution handling failed: {str(e)}")
    
    def _archive_incident(self, incident: Incident):
        """Archive closed incident"""



        try:
            # Move to history
            self.incident_history.append(incident)
            
            # Remove from active incidents
            if incident.incident_id in self.active_incidents:
                del self.active_incidents[incident.incident_id]
            
            self.logger.info(f"Archived incident {incident.incident_id}")
            
        except Exception as e:
            self.logger.error(f"Incident archiving failed: {str(e)}")
    
    def get_active_incidents(self, severity_filter: Optional[AlertSeverity] = None) -> List[Incident]:
        """Get active incidents, optionally filtered by severity"""



        try:
            incidents = list(self.active_incidents.values())
            
            if severity_filter:
                incidents = [i for i in incidents if i.severity == severity_filter]
            
            # Sort by severity and creation time
            severity_order = {
                AlertSeverity.CRITICAL: 5,
                AlertSeverity.HIGH: 4,
                AlertSeverity.MEDIUM: 3,
                AlertSeverity.LOW: 2,
                AlertSeverity.INFO: 1
            }
            
            incidents.sort(key=lambda x: (severity_order.get(x.severity, 0), x.created_at), reverse=True)
            return incidents
            
        except Exception as e:
            self.logger.error(f"Failed to get active incidents: {str(e)}")
            return []
    
    def get_incident_statistics(self) -> Dict[str, Any]:
        """Get incident statistics and insights"""



        try:
            all_incidents = list(self.active_incidents.values()) + self.incident_history
            
            if not all_incidents:
                return {"total_incidents": 0}
            
            # Basic statistics
            total_incidents = len(all_incidents)
            active_count = len(self.active_incidents)
            resolved_count = len([i for i in all_incidents if i.status == IncidentStatus.RESOLVED])
            
            # Severity breakdown
            severity_counts = defaultdict(int)
            for incident in all_incidents:
                severity_counts[incident.severity.value] += 1
            
            # Average resolution time for resolved incidents
            resolved_incidents = [i for i in all_incidents if i.resolved_at]
            avg_resolution_time = 0
            
            if resolved_incidents:
                resolution_times = [
                    (i.resolved_at - i.created_at).total_seconds() / 3600  # Hours
                    for i in resolved_incidents
                ]
                avg_resolution_time = np.mean(resolution_times)
            
            return {
                "total_incidents": total_incidents,
                "active_incidents": active_count,
                "resolved_incidents": resolved_count,
                "severity_breakdown": dict(severity_counts),
                "avg_resolution_time_hours": avg_resolution_time,
                "resolution_rate": (resolved_count / max(total_incidents, 1)) * 100
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get incident statistics: {str(e)}")
            return {"error": str(e)}


class IntelligentMonitoringSystem:
    """Main intelligent monitoring and predictive analytics system"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.anomaly_detector = AnomalyDetector()
        self.predictive_engine = PredictiveEngine()
        self.incident_manager = IncidentManager()
        
        # System state
        self.active_monitoring = True
        self.monitoring_threads = []
        self.metric_buffer = deque(maxlen=10000)
        self.alert_buffer = deque(maxlen=1000)
        
        # Configuration
        self.monitoring_config = {
            "monitoring_interval": 30,  # seconds
            "anomaly_detection_window": 300,  # 5 minutes
            "prediction_interval": 3600,  # 1 hour
            "metric_retention_hours": 24,
            "alert_suppression_minutes": 10
        }
        
        # Start monitoring processes
        self._start_monitoring_processes()
    
    def _start_monitoring_processes(self):
        """Start background monitoring processes"""



        try:
            # Metric collection thread
            metric_thread = threading.Thread(
                target=self._metric_collection_loop,
                daemon=True,
                name="MetricCollector"
            )
            metric_thread.start()
            self.monitoring_threads.append(metric_thread)
            
            # Anomaly detection thread
            anomaly_thread = threading.Thread(
                target=self._anomaly_detection_loop,
                daemon=True,
                name="AnomalyDetector"
            )
            anomaly_thread.start()
            self.monitoring_threads.append(anomaly_thread)
            
            # Predictive analytics thread
            prediction_thread = threading.Thread(
                target=self._prediction_loop,
                daemon=True,
                name="PredictiveEngine"
            )
            prediction_thread.start()
            self.monitoring_threads.append(prediction_thread)
            
            self.logger.info("Started intelligent monitoring processes")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring processes: {str(e)}")
    
    def _metric_collection_loop(self):
        """Background metric collection loop"""
        while self.active_monitoring:
            try:
                # Collect system metrics
                current_time = datetime.utcnow()
                
                # Here you would collect real metrics from various sources
                # For demonstration, we create sample metrics
                sample_metrics = self._generate_sample_metrics(current_time)
                
                # Add to buffer
                self.metric_buffer.extend(sample_metrics)
                
                # Clean old metrics
                cutoff_time = current_time - timedelta(hours=self.monitoring_config["metric_retention_hours"])
                self.metric_buffer = deque([
                    m for m in self.metric_buffer 
                    if m.timestamp > cutoff_time
                ], maxlen=self.metric_buffer.maxlen)
                
                time.sleep(self.monitoring_config["monitoring_interval"])
                
            except Exception as e:
                self.logger.error(f"Metric collection error: {str(e)}")
                time.sleep(60)
    
    def _anomaly_detection_loop(self):
        """Background anomaly detection loop"""
        while self.active_monitoring:
            try:
                # Get recent metrics for analysis
                current_time = datetime.utcnow()
                analysis_window = current_time - timedelta(
                    seconds=self.monitoring_config["anomaly_detection_window"]
                )
                
                recent_metrics = [
                    m for m in self.metric_buffer
                    if m.timestamp > analysis_window
                ]
                
                if len(recent_metrics) > 10:  # Need minimum data
                    # Run anomaly detection
                    anomalies = asyncio.run(
                        self.anomaly_detector.detect_anomalies(recent_metrics)
                    )
                    
                    # Process detected anomalies
                    for anomaly in anomalies:
                        asyncio.run(self._handle_alert(anomaly))
                
                time.sleep(self.monitoring_config["anomaly_detection_window"])
                
            except Exception as e:
                self.logger.error(f"Anomaly detection error: {str(e)}")
                time.sleep(60)
    
    def _prediction_loop(self):
        """Background prediction loop"""
        while self.active_monitoring:
            try:
                # Get metrics for prediction
                recent_metrics = list(self.metric_buffer)
                
                if len(recent_metrics) > 50:  # Need sufficient data
                    # Run capacity predictions
                    capacity_predictions = asyncio.run(
                        self.predictive_engine.predict_capacity_needs(recent_metrics)
                    )
                    
                    for prediction in capacity_predictions:
                        # Handle alert asynchronously without await
                        try:
                            asyncio.run(self._handle_alert(prediction))
                        except Exception as alert_error:
                            self.logger.error(f"Alert handling error: {alert_error}")
                
                time.sleep(self.monitoring_config["prediction_interval"])
                
            except Exception as e:
                self.logger.error(f"Prediction loop error: {str(e)}")
                time.sleep(300)  # 5 minute retry delay
    
    async def _handle_alert(self, alert: PredictiveAlert):
        """Handle generated alerts"""



        try:
            # Check for alert suppression (avoid spam)
            if self._is_alert_suppressed(alert):
                return
            
            # Add to alert buffer
            self.alert_buffer.append(alert)
            
            # Create incident if severity is high enough
            if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                incident = await self.incident_manager.create_incident(alert)
                self.logger.warning(f"Created incident for high-severity alert: {incident.incident_id}")
            
            # Log alert
            self.logger.info(f"Alert generated: {alert.title} (Severity: {alert.severity.value})")
            
        except Exception as e:
            self.logger.error(f"Alert handling failed: {str(e)}")
    
    def _is_alert_suppressed(self, alert: PredictiveAlert) -> bool:
        """Check if alert should be suppressed to avoid spam"""



        try:
            suppression_window = timedelta(minutes=self.monitoring_config["alert_suppression_minutes"])
            cutoff_time = datetime.utcnow() - suppression_window
            
            # Check recent alerts for similar ones
            recent_similar_alerts = [
                a for a in self.alert_buffer
                if a.created_at > cutoff_time
                and a.prediction_type == alert.prediction_type
                and set(a.affected_metrics) & set(alert.affected_metrics)
            ]
            
            return len(recent_similar_alerts) > 0
            
        except Exception as e:
            self.logger.error(f"Alert suppression check failed: {str(e)}")
            return False
    
    def _generate_sample_metrics(self, timestamp: datetime) -> List[MonitoringMetric]:
        """Generate sample metrics for demonstration"""



        try:
            import random
            
            base_values = {
                'cpu_usage': 45.0,
                'memory_usage': 60.0,
                'disk_usage': 30.0,
                'network_io': 100.0,
                'response_time': 250.0,
                'error_rate': 2.0,
                'active_users': 1000.0,
                'request_rate': 500.0
            }
            
            metrics = []
            for name, base_value in base_values.items():
                # Add some random variation
                variation = random.uniform(-0.2, 0.2) * base_value
                current_value = max(0, base_value + variation)
                
                # Occasionally add anomalies
                if random.random() < 0.05:  # 5% chance of anomaly
                    current_value *= random.uniform(1.5, 3.0)
                
                metric = MonitoringMetric(
                    name=name,
                    value=current_value,
                    timestamp=timestamp,
                    scope=MonitoringScope.SYSTEM_HEALTH,
                    unit=self._get_metric_unit(name),
                    threshold_warning=base_value * 1.2,
                    threshold_critical=base_value * 1.5,
                    source="intelligent_monitoring_system"
                )
                
                metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Sample metric generation failed: {str(e)}")
            return []
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Get appropriate unit for metric"""
        unit_map = {
            'cpu_usage': '%',
            'memory_usage': '%',
            'disk_usage': '%',
            'network_io': 'MB/s',
            'response_time': 'ms',
            'error_rate': '%',
            'active_users': 'count',
            'request_rate': 'req/s'
        }
        return unit_map.get(metric_name, '')
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""



        try:
            current_time = datetime.utcnow()
            
            # Recent metrics summary
            recent_window = current_time - timedelta(minutes=10)
            recent_metrics = [m for m in self.metric_buffer if m.timestamp > recent_window]
            
            # Recent alerts
            recent_alerts = [a for a in self.alert_buffer if a.created_at > recent_window]
            
            # Incident statistics
            incident_stats = self.incident_manager.get_incident_statistics()
            
            status = {
                "timestamp": current_time.isoformat(),
                "monitoring_active": self.active_monitoring,
                "system_health": {
                    "total_metrics_collected": len(self.metric_buffer),
                    "recent_metrics": len(recent_metrics),
                    "metric_collection_rate": len(recent_metrics) / 10 if recent_metrics else 0  # per minute
                },
                "alert_status": {
                    "total_alerts": len(self.alert_buffer),
                    "recent_alerts": len(recent_alerts),
                    "active_incidents": len(self.incident_manager.active_incidents)
                },
                "incident_management": incident_stats,
                "prediction_status": {
                    "anomaly_detection_active": True,
                    "predictive_analytics_active": True,
                    "last_analysis": current_time.isoformat()
                },
                "performance": {
                    "monitoring_threads": len(self.monitoring_threads),
                    "buffer_utilization": len(self.metric_buffer) / self.metric_buffer.maxlen
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"System status retrieval failed: {str(e)}")
            return {"error": str(e)}
    
    async def run_manual_analysis(self, analysis_type: str, 
                                parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run manual analysis on demand"""



        try:
            results = {"analysis_type": analysis_type, "timestamp": datetime.utcnow().isoformat()}
            
            if analysis_type == "anomaly_detection":
                recent_metrics = list(self.metric_buffer)[-1000:]  # Last 1000 metrics
                anomalies = await self.anomaly_detector.detect_anomalies(recent_metrics)
                results["anomalies"] = [a.to_dict() for a in anomalies]
            
            elif analysis_type == "capacity_prediction":
                resource_metrics = [m for m in self.metric_buffer 
                                  if m.scope == MonitoringScope.INFRASTRUCTURE]
                predictions = await self.predictive_engine.predict_capacity_needs(resource_metrics)
                results["predictions"] = [p.to_dict() for p in predictions]
            
            elif analysis_type == "system_health":
                results.update(await self.get_system_status())
            
            else:
                results["error"] = f"Unknown analysis type: {analysis_type}"
            
            return results
            
        except Exception as e:
            self.logger.error(f"Manual analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def stop_monitoring(self):
        """Stop all monitoring processes"""



        try:
            self.active_monitoring = False
            
            # Wait for threads to finish
            for thread in self.monitoring_threads:
                if thread.is_alive():
                    thread.join(timeout=5)
            
            self.logger.info("Intelligent monitoring system stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {str(e)}")


# Export classes
__all__ = [
    'AlertSeverity',
    'MonitoringScope',
    'PredictionType',
    'IncidentStatus',
    'MonitoringMetric',
    'PredictiveAlert',
    'Incident',
    'AnomalyDetector',
    'PredictiveEngine', 
    'IncidentManager',
    'IntelligentMonitoringSystem'
]
