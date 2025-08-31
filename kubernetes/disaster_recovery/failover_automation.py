"""IA Influencer Agent - Intelligent Failover Automation
Advanced automated failover with ML-based failure prediction

This module provides intelligent failover automation:
- Machine learning-based failure prediction and prevention  
- Automated decision-making for failover scenarios
- Predictive capacity planning and resource allocation
- Intelligent traffic routing and load balancing
- Self-healing system capabilities with adaptive responses

Author: Fahed Mlaiel <mlaiel@live.de>
License: Proprietary - All rights reserved
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import numpy as np
from collections import defaultdict, deque
import aioredis

from backend.core.database import DatabaseManager
from backend.core.config import Config
from backend.utils.metrics import MetricsCollector
from backend.deployment.disaster_recovery.failover_manager import FailoverManager
from backend.deployment.disaster_recovery.recovery_planner import RecoveryPlanner


class FailurePredictionModel(Enum):
    """Types of failure prediction models"""    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    CLASSIFICATION = "classification"
    ENSEMBLE = "ensemble"
    NEURAL_NETWORK = "neural_network"


class AutomationLevel(Enum):
    """Levels of failover automation"""    MANUAL = "manual"              # Human approval required
    SEMI_AUTOMATIC = "semi_automatic"  # Automatic with human oversight
    AUTOMATIC = "automatic"        # Fully automated
    INTELLIGENT = "intelligent"    # AI-driven decisions


class FailoverTrigger(Enum):
    """Types of failover triggers"""    THRESHOLD_BREACH = "threshold_breach"
    PREDICTION_ALERT = "prediction_alert"
    CASCADING_FAILURE = "cascading_failure"
    MANUAL_TRIGGER = "manual_trigger"
    SCHEDULED_MAINTENANCE = "scheduled_maintenance"


@dataclass
class FailureSignal:
    """Failure prediction signal"""    signal_id: str
    timestamp: datetime
    source_system: str
    signal_type: str
    confidence: float
    predicted_failure_time: Optional[datetime]
    impact_assessment: Dict[str, Any]
    recommended_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationRule:
    """Automation rule for failover decisions"""    rule_id: str
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    automation_level: AutomationLevel
    priority: int
    enabled: bool = True
    confidence_threshold: float = 0.8


@dataclass
class FailoverDecision:
    """Automated failover decision"""    decision_id: str
    timestamp: datetime
    trigger_type: FailoverTrigger
    automation_level: AutomationLevel
    confidence: float
    source_signals: List[str]
    target_systems: List[str]
    expected_impact: Dict[str, Any]
    approval_required: bool
    executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None


class PredictiveModel:
    """Base class for failure prediction models"""    
    def __init__(self, model_type: FailurePredictionModel):
        self.model_type = model_type
        self.model = None
        self.is_trained = False
        self.last_training = None
        self.feature_importance = {}
        
    async def train(self, training_data: List[Dict[str, Any]]):
        """Train the prediction model"""        # Default implementation for prediction models without training support
        logging.warning(f"Model training not implemented for {self.__class__.__name__}")
        pass
        
    async def predict(self, features: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Predict failure probability and metadata"""        # Default implementation for prediction models without prediction support
        logging.warning(f"Failure prediction not implemented for {self.__class__.__name__}")
        return 0.0, {"prediction_supported": False}
        
    async def update_model(self, new_data: List[Dict[str, Any]]):
        """Update model with new data"""        # Default implementation for prediction models without model updating
        logging.warning(f"Model updating not implemented for {self.__class__.__name__}")
        pass


class AnomalyDetectionModel(PredictiveModel):
    """Anomaly detection based failure prediction"""    
    def __init__(self):
        super().__init__(FailurePredictionModel.ANOMALY_DETECTION)
        self.baseline_metrics = {}
        self.anomaly_thresholds = {}
        
    async def train(self, training_data: List[Dict[str, Any]]):
        """Train anomaly detection model"""        try:
            # Extract metrics from training data
            metrics_data = defaultdict(list)
            
            for data_point in training_data:
                for metric, value in data_point.get('metrics', {}).items():
                    if isinstance(value, (int, float)):
                        metrics_data[metric].append(value)
            
            # Calculate baseline statistics
            for metric, values in metrics_data.items():
                if len(values) >= 10:  # Minimum samples
                    self.baseline_metrics[metric] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'median': np.median(values),
                        'q75': np.percentile(values, 75),
                        'q95': np.percentile(values, 95)
                    }
                    
                    # Set anomaly threshold (3 sigma rule + percentile based)
                    sigma_threshold = self.baseline_metrics[metric]['mean'] + 3 * self.baseline_metrics[metric]['std']
                    percentile_threshold = self.baseline_metrics[metric]['q95']
                    
                    self.anomaly_thresholds[metric] = max(sigma_threshold, percentile_threshold)
            
            self.is_trained = True
            self.last_training = datetime.utcnow()
            
        except Exception as e:
            raise Exception(f"Anomaly detection training failed: {e}")
    
    async def predict(self, features: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Predict failure probability based on anomalies"""        try:
            if not self.is_trained:
                return 0.0, {'error': 'Model not trained'}
            
            anomaly_scores = {}
            total_anomaly_score = 0.0
            detected_anomalies = []
            
            metrics = features.get('metrics', {})
            
            for metric, value in metrics.items():
                if metric in self.baseline_metrics and isinstance(value, (int, float)):
                    baseline = self.baseline_metrics[metric]
                    threshold = self.anomaly_thresholds[metric]
                    
                    # Calculate z-score
                    z_score = abs((value - baseline['mean']) / baseline['std']) if baseline['std'] > 0 else 0
                    
                    # Calculate anomaly score
                    anomaly_score = min(z_score / 3.0, 1.0)  # Normalize to [0,1]
                    
                    anomaly_scores[metric] = anomaly_score
                    total_anomaly_score += anomaly_score
                    
                    if value > threshold:
                        detected_anomalies.append({
                            'metric': metric,
                            'value': value,
                            'threshold': threshold,
                            'deviation': (value - baseline['mean']) / baseline['std']
                        })
            
            # Calculate overall failure probability
            if anomaly_scores:
                avg_anomaly_score = total_anomaly_score / len(anomaly_scores)
                failure_probability = min(avg_anomaly_score, 0.95)  # Cap at 95%
            else:
                failure_probability = 0.0
            
            metadata = {
                'anomaly_scores': anomaly_scores,
                'detected_anomalies': detected_anomalies,
                'total_metrics_analyzed': len(anomaly_scores)
            }
            
            return failure_probability, metadata
            
        except Exception as e:
            return 0.0, {'error': str(e)}


class TimeSeriesPredictionModel(PredictiveModel):
    """Time series based failure prediction"""    
    def __init__(self):
        super().__init__(FailurePredictionModel.TIME_SERIES)
        self.trend_models = {}
        self.seasonal_patterns = {}
        
    async def train(self, training_data: List[Dict[str, Any]]):
        """Train time series prediction model"""        try:
            # Group data by timestamp
            time_series_data = defaultdict(lambda: defaultdict(list))
            
            for data_point in training_data:
                timestamp = data_point.get('timestamp')
                if timestamp:
                    for metric, value in data_point.get('metrics', {}).items():
                        if isinstance(value, (int, float)):
                            time_series_data[metric]['timestamps'].append(timestamp)
                            time_series_data[metric]['values'].append(value)
            
            # Analyze trends for each metric
            for metric, data in time_series_data.items():
                if len(data['values']) >= 20:  # Minimum for trend analysis
                    # Simple linear trend calculation
                    timestamps = [ts.timestamp() for ts in data['timestamps']]
                    values = data['values']
                    
                    # Calculate trend slope
                    n = len(values)
                    sum_x = sum(timestamps)
                    sum_y = sum(values)
                    sum_xy = sum(x * y for x, y in zip(timestamps, values))
                    sum_x2 = sum(x * x for x in timestamps)
                    
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    intercept = (sum_y - slope * sum_x) / n
                    
                    self.trend_models[metric] = {
                        'slope': slope,
                        'intercept': intercept,
                        'recent_avg': np.mean(values[-10:]),  # Last 10 values
                        'historical_max': max(values),
                        'historical_min': min(values)
                    }
            
            self.is_trained = True
            self.last_training = datetime.utcnow()
            
        except Exception as e:
            raise Exception(f"Time series training failed: {e}")
    
    async def predict(self, features: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Predict failure based on time series trends"""        try:
            if not self.is_trained:
                return 0.0, {'error': 'Model not trained'}
            
            current_time = datetime.utcnow().timestamp()
            prediction_horizon = 3600  # 1 hour ahead
            future_time = current_time + prediction_horizon
            
            risk_factors = []
            total_risk = 0.0
            
            metrics = features.get('metrics', {})
            
            for metric, current_value in metrics.items():
                if metric in self.trend_models and isinstance(current_value, (int, float)):
                    model = self.trend_models[metric]
                    
                    # Predict future value
                    predicted_value = model['slope'] * future_time + model['intercept']
                    
                    # Calculate risk based on trend and thresholds
                    risk_score = 0.0
                    
                    # Trend risk
                    if model['slope'] > 0:  # Increasing trend
                        if predicted_value > model['historical_max'] * 1.2:
                            risk_score += 0.4
                        elif predicted_value > model['historical_max']:
                            risk_score += 0.2
                    
                    # Current value risk
                    if current_value > model['recent_avg'] * 1.5:
                        risk_score += 0.3
                    elif current_value > model['recent_avg'] * 1.2:
                        risk_score += 0.15
                    
                    # Acceleration risk (rapid change)
                    if abs(current_value - model['recent_avg']) > abs(model['recent_avg'] - model['historical_max']) * 0.5:
                        risk_score += 0.3
                    
                    risk_factors.append({
                        'metric': metric,
                        'current_value': current_value,
                        'predicted_value': predicted_value,
                        'risk_score': min(risk_score, 1.0)
                    })
                    
                    total_risk += min(risk_score, 1.0)
            
            # Calculate overall failure probability
            if risk_factors:
                failure_probability = min(total_risk / len(risk_factors), 0.95)
            else:
                failure_probability = 0.0
            
            metadata = {
                'risk_factors': risk_factors,
                'prediction_horizon_seconds': prediction_horizon,
                'models_used': len(risk_factors)
            }
            
            return failure_probability, metadata
            
        except Exception as e:
            return 0.0, {'error': str(e)}


class IntelligentFailoverAutomation:
    """    Intelligent failover automation with ML-based prediction
    
    Features:
    - Multiple prediction models (anomaly detection, time series, ensemble)
    - Adaptive automation levels based on confidence and context
    - Intelligent decision-making with approval workflows
    - Predictive maintenance and proactive failover
    - Self-learning from historical incidents and outcomes
    - Context-aware automation rules and policies
    """
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager(config)
        self.metrics = MetricsCollector()
        self.failover_manager = FailoverManager(config)
        self.recovery_planner = RecoveryPlanner(config)
        
        # Prediction models
        self.prediction_models: Dict[str, PredictiveModel] = {
            'anomaly_detection': AnomalyDetectionModel(),
            'time_series': TimeSeriesPredictionModel()
        }
        
        # Automation state
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.failure_signals: deque = deque(maxlen=1000)
        self.pending_decisions: Dict[str, FailoverDecision] = {}
        
        # Learning and adaptation
        self.decision_history: List[FailoverDecision] = []
        self.model_performance: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'false_positive_rate': 0.0
        })
        
        # Redis for real-time coordination
        self.redis_client = None
        
        # Initialize automation rules
        self._initialize_automation_rules()

    async def initialize(self):
        """Initialize the automation system"""        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(
                self.config.get('redis_url', 'redis://localhost:6379')
            )
            
            # Load historical data for model training
            await self._load_and_train_models()
            
            # Start monitoring and prediction tasks
            asyncio.create_task(self._continuous_monitoring())
            asyncio.create_task(self._process_pending_decisions())
            
            self.logger.info("Intelligent failover automation initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize automation: {e}")
            raise

    def _initialize_automation_rules(self):
        """Initialize default automation rules"""        default_rules = [
            {
                'rule_id': 'high_confidence_auto_failover',
                'name': 'High Confidence Automatic Failover',
                'description': 'Automatically failover when prediction confidence > 90%',
                'conditions': [
                    {'type': 'prediction_confidence', 'operator': '>', 'value': 0.9},
                    {'type': 'predicted_impact', 'operator': '>', 'value': 'medium'}
                ],
                'actions': [
                    {'type': 'execute_failover', 'target': 'predicted_failing_systems'},
                    {'type': 'notify_operations', 'urgency': 'high'}
                ],
                'automation_level': AutomationLevel.AUTOMATIC,
                'priority': 1,
                'confidence_threshold': 0.9
            },
            {
                'rule_id': 'medium_confidence_approval_required',
                'name': 'Medium Confidence with Approval',
                'description': 'Require approval for medium confidence predictions',
                'conditions': [
                    {'type': 'prediction_confidence', 'operator': '>=', 'value': 0.7},
                    {'type': 'prediction_confidence', 'operator': '<', 'value': 0.9}
                ],
                'actions': [
                    {'type': 'request_approval', 'approvers': ['ops_team', 'platform_lead']},
                    {'type': 'prepare_failover_plan'}
                ],
                'automation_level': AutomationLevel.SEMI_AUTOMATIC,
                'priority': 2,
                'confidence_threshold': 0.7
            },
            {
                'rule_id': 'cascading_failure_protection',
                'name': 'Cascading Failure Protection',
                'description': 'Proactive protection against cascading failures',
                'conditions': [
                    {'type': 'failed_systems_count', 'operator': '>=', 'value': 2},
                    {'type': 'failure_rate', 'operator': '>', 'value': 0.1}  # 10% in timeframe
                ],
                'actions': [
                    {'type': 'isolate_failing_systems'},
                    {'type': 'scale_up_healthy_systems'},
                    {'type': 'activate_emergency_procedures'}
                ],
                'automation_level': AutomationLevel.AUTOMATIC,
                'priority': 0,  # Highest priority
                'confidence_threshold': 0.8
            },
            {
                'rule_id': 'predictive_maintenance',
                'name': 'Predictive Maintenance Scheduling',
                'description': 'Schedule maintenance based on failure predictions',
                'conditions': [
                    {'type': 'prediction_time_horizon', 'operator': '>', 'value': 86400},  # > 24 hours
                    {'type': 'prediction_confidence', 'operator': '>', 'value': 0.6}
                ],
                'actions': [
                    {'type': 'schedule_maintenance'},
                    {'type': 'notify_maintenance_team'}
                ],
                'automation_level': AutomationLevel.SEMI_AUTOMATIC,
                'priority': 3,
                'confidence_threshold': 0.6
            }
        ]
        
        for rule_config in default_rules:
            automation_rule = AutomationRule(
                rule_id=rule_config['rule_id'],
                name=rule_config['name'],
                description=rule_config['description'],
                conditions=rule_config['conditions'],
                actions=rule_config['actions'],
                automation_level=rule_config['automation_level'],
                priority=rule_config['priority'],
                confidence_threshold=rule_config['confidence_threshold']
            )
            
            self.automation_rules[rule_config['rule_id']] = automation_rule

    async def _load_and_train_models(self):
        """Load historical data and train prediction models"""        try:
            # Load historical incident and metrics data
            cutoff_date = datetime.utcnow() - timedelta(days=90)  # Last 90 days
            
            historical_data = await self.db_manager.get_historical_metrics_data(cutoff_date)
            
            if historical_data:
                # Train each prediction model
                for model_name, model in self.prediction_models.items():
                    try:
                        await model.train(historical_data)
                        self.logger.info(f"Trained {model_name} model with {len(historical_data)} data points")
                    except Exception as e:
                        self.logger.error(f"Failed to train {model_name} model: {e}")
            else:
                self.logger.warning("No historical data available for model training")
                
        except Exception as e:
            self.logger.error(f"Failed to load and train models: {e}")

    async def _continuous_monitoring(self):
        """Continuous monitoring and failure prediction"""        while True:
            try:
                # Collect current system metrics
                current_metrics = await self._collect_current_metrics()
                
                # Run predictions with all models
                predictions = await self._run_predictions(current_metrics)
                
                # Analyze predictions and generate signals
                failure_signals = await self._analyze_predictions(predictions, current_metrics)
                
                # Process failure signals through automation rules
                for signal in failure_signals:
                    await self._process_failure_signal(signal)
                
                # Update model performance if we have feedback
                await self._update_model_performance()
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)

    async def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics for prediction"""        try:
            # Collect from various sources
            system_metrics = await self.metrics.get_system_metrics()
            application_metrics = await self.metrics.get_application_metrics()
            infrastructure_metrics = await self.metrics.get_infrastructure_metrics()
            
            # Combine all metrics
            current_metrics = {
                'timestamp': datetime.utcnow(),
                'metrics': {
                    **system_metrics,
                    **application_metrics,
                    **infrastructure_metrics
                }
            }
            
            return current_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect current metrics: {e}")
            return {'timestamp': datetime.utcnow(), 'metrics': {}}

    async def _run_predictions(self, current_metrics: Dict[str, Any]) -> Dict[str, Tuple[float, Dict[str, Any]]]:
        """Run failure predictions with all models"""        predictions = {}
        
        for model_name, model in self.prediction_models.items():
            if model.is_trained:
                try:
                    confidence, metadata = await model.predict(current_metrics)
                    predictions[model_name] = (confidence, metadata)
                except Exception as e:
                    self.logger.error(f"Prediction failed for {model_name}: {e}")
                    predictions[model_name] = (0.0, {'error': str(e)})
        
        return predictions

    async def _analyze_predictions(self, predictions: Dict[str, Tuple[float, Dict[str, Any]]], 
                                 current_metrics: Dict[str, Any]) -> List[FailureSignal]:
        """Analyze predictions and generate failure signals"""        failure_signals = []
        
        # Ensemble prediction (average of all models)
        valid_predictions = [(conf, meta) for conf, meta in predictions.values() 
                           if 'error' not in meta]
        
        if valid_predictions:
            ensemble_confidence = sum(conf for conf, _ in valid_predictions) / len(valid_predictions)
            
            # Create failure signal if confidence exceeds minimum threshold
            if ensemble_confidence > 0.3:  # 30% minimum threshold
                # Estimate failure time based on trends
                predicted_failure_time = self._estimate_failure_time(current_metrics, ensemble_confidence)
                
                # Assess impact
                impact_assessment = await self._assess_failure_impact(current_metrics, ensemble_confidence)
                
                # Generate recommendations
                recommendations = self._generate_recommendations(
                    predictions, impact_assessment, ensemble_confidence
                )
                
                signal = FailureSignal(
                    signal_id=f"prediction_{int(datetime.utcnow().timestamp())}",
                    timestamp=datetime.utcnow(),
                    source_system='ml_prediction',
                    signal_type='failure_prediction',
                    confidence=ensemble_confidence,
                    predicted_failure_time=predicted_failure_time,
                    impact_assessment=impact_assessment,
                    recommended_actions=recommendations,
                    metadata={
                        'individual_predictions': predictions,
                        'model_count': len(valid_predictions),
                        'current_metrics': current_metrics
                    }
                )
                
                failure_signals.append(signal)
                self.failure_signals.append(signal)
        
        return failure_signals

    def _estimate_failure_time(self, current_metrics: Dict[str, Any], 
                             confidence: float) -> Optional[datetime]:
        """Estimate when failure might occur"""        try:
            # Simple heuristic based on confidence and current trends
            base_time = datetime.utcnow()
            
            if confidence > 0.9:
                # Very high confidence - immediate risk
                return base_time + timedelta(minutes=15)
            elif confidence > 0.7:
                # High confidence - within hours
                hours_ahead = max(1, int((1.0 - confidence) * 12))
                return base_time + timedelta(hours=hours_ahead)
            elif confidence > 0.5:
                # Medium confidence - within day
                hours_ahead = max(6, int((1.0 - confidence) * 48))
                return base_time + timedelta(hours=hours_ahead)
            else:
                # Lower confidence - longer term
                days_ahead = max(1, int((1.0 - confidence) * 7))
                return base_time + timedelta(days=days_ahead)
                
        except Exception as e:
            self.logger.error(f"Failed to estimate failure time: {e}")
            return None

    async def _assess_failure_impact(self, current_metrics: Dict[str, Any], 
                                   confidence: float) -> Dict[str, Any]:
        """Assess potential impact of predicted failure"""        try:
            # Get current system state
            active_services = await self.db_manager.get_active_services()
            active_users = await self.db_manager.get_active_user_count()
            
            # Estimate impact based on current load and confidence
            impact_assessment = {
                'affected_services': len(active_services),
                'affected_users': active_users,
                'estimated_downtime_minutes': min(confidence * 120, 240),  # Max 4 hours
                'business_impact_level': self._calculate_business_impact_level(
                    len(active_services), active_users, confidence
                ),
                'revenue_impact_per_hour': active_users * 0.1 * confidence,  # €0.1 per user
                'sla_breach_risk': confidence > 0.8
            }
            
            return impact_assessment
            
        except Exception as e:
            self.logger.error(f"Failed to assess failure impact: {e}")
            return {}

    def _calculate_business_impact_level(self, service_count: int, 
                                       user_count: int, confidence: float) -> str:
        """Calculate business impact level"""        impact_score = (service_count * 0.1) + (user_count * 0.0001) + (confidence * 0.5)
        
        if impact_score > 0.8:
            return 'critical'
        elif impact_score > 0.6:
            return 'high'
        elif impact_score > 0.4:
            return 'medium'
        else:
            return 'low'

    def _generate_recommendations(self, predictions: Dict[str, Tuple[float, Dict[str, Any]]], 
                                impact_assessment: Dict[str, Any],
                                confidence: float) -> List[str]:
        """Generate actionable recommendations"""        recommendations = []
        
        if confidence > 0.9:
            recommendations.extend([
                "Immediate failover preparation recommended",
                "Activate incident response team",
                "Prepare customer communication"
            ])
        elif confidence > 0.7:
            recommendations.extend([
                "Schedule proactive maintenance window",
                "Increase monitoring frequency",
                "Prepare backup systems"
            ])
        elif confidence > 0.5:
            recommendations.extend([
                "Investigate warning indicators",
                "Review system health",
                "Plan preventive actions"
            ])
        
        # Add specific recommendations based on impact
        impact_level = impact_assessment.get('business_impact_level', 'low')
        if impact_level in ['critical', 'high']:
            recommendations.append("Consider emergency capacity scaling")
            recommendations.append("Alert executive stakeholders")
        
        return recommendations

    async def _process_failure_signal(self, signal: FailureSignal):
        """Process failure signal through automation rules"""        try:
            # Find applicable automation rules
            applicable_rules = []
            
            for rule in self.automation_rules.values():
                if rule.enabled and self._evaluate_rule_conditions(rule, signal):
                    applicable_rules.append(rule)
            
            # Sort by priority
            applicable_rules.sort(key=lambda r: r.priority)
            
            # Process highest priority rule
            if applicable_rules:
                rule = applicable_rules[0]
                
                decision = FailoverDecision(
                    decision_id=f"decision_{int(datetime.utcnow().timestamp())}",
                    timestamp=datetime.utcnow(),
                    trigger_type=FailoverTrigger.PREDICTION_ALERT,
                    automation_level=rule.automation_level,
                    confidence=signal.confidence,
                    source_signals=[signal.signal_id],
                    target_systems=self._extract_target_systems(signal),
                    expected_impact=signal.impact_assessment,
                    approval_required=rule.automation_level in [
                        AutomationLevel.MANUAL, 
                        AutomationLevel.SEMI_AUTOMATIC
                    ]
                )
                
                # Execute or queue decision
                if rule.automation_level == AutomationLevel.AUTOMATIC:
                    await self._execute_decision(decision, rule)
                else:
                    self.pending_decisions[decision.decision_id] = decision
                    await self._request_approval(decision, rule)
                
        except Exception as e:
            self.logger.error(f"Failed to process failure signal: {e}")

    def _evaluate_rule_conditions(self, rule: AutomationRule, signal: FailureSignal) -> bool:
        """Evaluate if rule conditions are met"""        try:
            for condition in rule.conditions:
                condition_type = condition['type']
                operator = condition['operator']
                value = condition['value']
                
                if condition_type == 'prediction_confidence':
                    signal_value = signal.confidence
                elif condition_type == 'predicted_impact':
                    signal_value = signal.impact_assessment.get('business_impact_level', 'low')
                    # Convert to numeric for comparison
                    impact_values = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
                    signal_value = impact_values.get(signal_value, 0)
                    value = impact_values.get(value, 0) if isinstance(value, str) else value
                else:
                    continue  # Skip unknown condition types
                
                # Evaluate condition
                if not self._evaluate_condition(signal_value, operator, value):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate rule conditions: {e}")
            return False

    def _evaluate_condition(self, signal_value: Any, operator: str, threshold_value: Any) -> bool:
        """Evaluate individual condition"""        if operator == '>':
            return signal_value > threshold_value
        elif operator == '>=':
            return signal_value >= threshold_value
        elif operator == '<':
            return signal_value < threshold_value
        elif operator == '<=':
            return signal_value <= threshold_value
        elif operator == '==':
            return signal_value == threshold_value
        elif operator == '!=':
            return signal_value != threshold_value
        else:
            return False

    async def _execute_decision(self, decision: FailoverDecision, rule: AutomationRule):
        """Execute automated failover decision"""        try:
            execution_results = []
            
            for action in rule.actions:
                action_type = action['type']
                
                if action_type == 'execute_failover':
                    result = await self._execute_failover_action(decision, action)
                elif action_type == 'notify_operations':
                    result = await self._execute_notification_action(decision, action)
                elif action_type == 'isolate_failing_systems':
                    result = await self._execute_isolation_action(decision, action)
                elif action_type == 'scale_up_healthy_systems':
                    result = await self._execute_scaling_action(decision, action)
                else:
                    result = {'status': 'skipped', 'reason': f'Unknown action type: {action_type}'}
                
                execution_results.append({
                    'action_type': action_type,
                    'result': result
                })
            
            decision.executed = True
            decision.execution_result = {
                'success': all(r['result'].get('status') == 'success' for r in execution_results),
                'actions': execution_results,
                'execution_time': datetime.utcnow().isoformat()
            }
            
            self.decision_history.append(decision)
            
            self.logger.info(f"Executed automated decision {decision.decision_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to execute decision {decision.decision_id}: {e}")
            decision.execution_result = {'error': str(e)}

    async def get_automation_status(self) -> Dict[str, Any]:
        """Get comprehensive automation system status"""        try:
            model_status = {}
            for name, model in self.prediction_models.items():
                model_status[name] = {
                    'trained': model.is_trained,
                    'last_training': model.last_training.isoformat() if model.last_training else None,
                    'performance': self.model_performance.get(name, {})
                }
            
            return {
                'system_status': 'active',
                'prediction_models': model_status,
                'automation_rules': {
                    rule_id: {
                        'enabled': rule.enabled,
                        'automation_level': rule.automation_level.value,
                        'priority': rule.priority
                    }
                    for rule_id, rule in self.automation_rules.items()
                },
                'recent_signals': len([s for s in self.failure_signals 
                                     if s.timestamp > datetime.utcnow() - timedelta(hours=24)]),
                'pending_decisions': len(self.pending_decisions),
                'total_decisions': len(self.decision_history),
                'automation_effectiveness': self._calculate_automation_effectiveness()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get automation status: {e}")
            return {'error': str(e)}

    def _calculate_automation_effectiveness(self) -> Dict[str, float]:
        """Calculate automation effectiveness metrics"""        if not self.decision_history:
            return {'insufficient_data': True}
        
        total_decisions = len(self.decision_history)
        successful_decisions = sum(1 for d in self.decision_history 
                                 if d.execution_result and d.execution_result.get('success'))
        
        automated_decisions = sum(1 for d in self.decision_history 
                                if d.automation_level == AutomationLevel.AUTOMATIC)
        
        return {
            'success_rate': successful_decisions / total_decisions,
            'automation_rate': automated_decisions / total_decisions,
            'average_confidence': sum(d.confidence for d in self.decision_history) / total_decisions,
            'total_decisions': total_decisions
        }
