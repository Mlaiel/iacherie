"""AI Processing Insights and Model Performance Analytics
Advanced AI model monitoring and processing insights for multimedia content.

This module provides comprehensive AI model performance tracking, processing insights,
prediction analytics, and optimization recommendations for AI-powered multimedia processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from enum import Enum
from collections import defaultdict, deque
import json
import hashlib

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """AI model types"""
    AUDIO_ENHANCEMENT = "audio_enhancement"
    VIDEO_UPSCALING = "video_upscaling"
    IMAGE_ENHANCEMENT = "image_enhancement"
    QUALITY_ASSESSMENT = "quality_assessment"
    CONTENT_ANALYSIS = "content_analysis"
    STYLE_TRANSFER = "style_transfer"
    NOISE_REDUCTION = "noise_reduction"
    SCENE_DETECTION = "scene_detection"
    OBJECT_DETECTION = "object_detection"
    CLASSIFICATION = "classification"

class ProcessingStage(Enum):
    """AI processing stages"""
    PREPROCESSING = "preprocessing"
    INFERENCE = "inference"
    POSTPROCESSING = "postprocessing"
    VALIDATION = "validation"

@dataclass
class ModelMetrics:
    """AI model performance metrics"""
    model_id: str
    model_type: ModelType
    model_version: str
    timestamp: datetime
    
    # Performance metrics
    inference_time: float = 0.0
    throughput: float = 0.0  # samples per second
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    
    # Resource utilization
    gpu_memory_used: Optional[float] = None  # MB
    cpu_usage: Optional[float] = None  # percentage
    memory_usage: Optional[float] = None  # MB
    
    # Quality metrics
    output_quality_score: Optional[float] = None
    confidence_score: Optional[float] = None
    uncertainty_score: Optional[float] = None
    
    # Model-specific metrics
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Processing context
    input_size: Optional[int] = None  # bytes
    output_size: Optional[int] = None  # bytes
    batch_size: int = 1
    
    # Error tracking
    error_count: int = 0
    warning_count: int = 0
    error_details: List[str] = field(default_factory=list)

@dataclass
class ProcessingInsight:
    """AI processing insight"""
    insight_id: str
    timestamp: datetime
    insight_type: str  # performance, quality, anomaly, optimization
    severity: str  # low, medium, high, critical
    
    title: str
    description: str
    
    # Data context
    affected_models: List[str] = field(default_factory=list)
    metrics_involved: List[str] = field(default_factory=list)
    
    # Actionable recommendations
    recommendations: List[str] = field(default_factory=list)
    estimated_impact: Optional[str] = None
    
    # Supporting data
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    
    # Status tracking
    status: str = "active"  # active, resolved, dismissed
    resolution_notes: Optional[str] = None

@dataclass
class PredictionAnalytics:
    """Prediction and forecasting analytics"""
    analysis_timestamp: datetime
    prediction_horizon: timedelta
    
    # Performance predictions
    predicted_throughput: float = 0.0
    predicted_accuracy: float = 0.0
    predicted_resource_usage: Dict[str, float] = field(default_factory=dict)
    
    # Capacity planning
    capacity_recommendations: List[str] = field(default_factory=list)
    scaling_suggestions: List[str] = field(default_factory=list)
    
    # Model lifecycle predictions
    model_performance_trends: Dict[str, List[float]] = field(default_factory=dict)
    recommended_retraining: List[str] = field(default_factory=list)
    
    # Quality predictions
    quality_trend_forecast: List[float] = field(default_factory=list)
    anomaly_probability: float = 0.0
    
    # Business impact predictions
    cost_projections: Dict[str, float] = field(default_factory=dict)
    efficiency_gains: Dict[str, float] = field(default_factory=dict)


class ModelPerformanceTracker:
    """AI model performance tracking and monitoring"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Data storage
        self.model_metrics: deque = deque(maxlen=self.config.get('max_metrics', 10000))
        self.model_registry: Dict[str, Dict[str, Any]] = {}
        
        # Real-time tracking
        self.active_inferences: Dict[str, Dict[str, Any]] = {}
        
        # Performance baselines
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # Alert thresholds
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'inference_time_threshold': 5.0,  # seconds
            'accuracy_drop_threshold': 0.05,   # 5% drop
            'memory_threshold': 0.9,           # 90% GPU memory
            'error_rate_threshold': 0.02       # 2% error rate
        })
        
    async def register_model(self, model_id -> None: str, model_info -> None: Dict[str, Any]) -> None:
        """Register a new AI model for tracking"""
        try:
            self.model_registry[model_id] = {
                'model_type': model_info.get('model_type'),
                'model_version': model_info.get('model_version'),
                'creation_time': datetime.now(),
                'framework': model_info.get('framework'),
                'model_size': model_info.get('model_size'),
                'parameters': model_info.get('parameters', {}),
                'expected_performance': model_info.get('expected_performance', {}),
                'metadata': model_info.get('metadata', {})
            }
            
            # Initialize performance baseline
            self.performance_baselines[model_id] = model_info.get('expected_performance', {})
            
            self.logger.info(f"Registered model {model_id} for performance tracking")
            
        except Exception as e:
            self.logger.error(f"Failed to register model {model_id}: {e}")
            raise
    
    async def start_inference_tracking(self, model_id: str, inference_data: Dict[str, Any]) -> str:
        """Start tracking an AI inference operation"""
        try:
            inference_id = self._generate_inference_id(model_id)
            
            self.active_inferences[inference_id] = {
                'model_id': model_id,
                'start_time': datetime.now(),
                'input_data': inference_data,
                'stage': ProcessingStage.PREPROCESSING,
                'metrics': {}
            }
            
            return inference_id
            
        except Exception as e:
            self.logger.error(f"Failed to start inference tracking: {e}")
            raise
    
    async def update_inference_progress(self, inference_id -> None: str, stage -> None: ProcessingStage,
                                      metrics -> None: Optional[Dict[str, Any]] = None) -> None:
        """Update inference progress and metrics"""
        try:
            if inference_id not in self.active_inferences:
                self.logger.warning(f"Inference {inference_id} not found")
                return
            
            inference = self.active_inferences[inference_id]
            inference['stage'] = stage
            inference['last_update'] = datetime.now()
            
            if metrics:
                inference['metrics'].update(metrics)
            
        except Exception as e:
            self.logger.error(f"Failed to update inference progress: {e}")
    
    async def complete_inference_tracking(self, inference_id -> None: str, results -> None: Dict[str, Any]) -> None:
        """Complete inference tracking and record final metrics"""
        try:
            if inference_id not in self.active_inferences:
                self.logger.warning(f"Inference {inference_id} not found")
                return
            
            inference = self.active_inferences[inference_id]
            end_time = datetime.now()
            
            # Calculate final metrics
            model_metrics = ModelMetrics(
                model_id=inference['model_id'],
                model_type=ModelType(self.model_registry[inference['model_id']]['model_type']),
                model_version=self.model_registry[inference['model_id']]['model_version'],
                timestamp=end_time,
                inference_time=(end_time - inference['start_time']).total_seconds()
            )
            
            # Update metrics from results
            if 'accuracy' in results:
                model_metrics.accuracy = results['accuracy']
            if 'precision' in results:
                model_metrics.precision = results['precision']
            if 'recall' in results:
                model_metrics.recall = results['recall']
            if 'f1_score' in results:
                model_metrics.f1_score = results['f1_score']
            if 'output_quality_score' in results:
                model_metrics.output_quality_score = results['output_quality_score']
            if 'confidence_score' in results:
                model_metrics.confidence_score = results['confidence_score']
            
            # Update resource usage
            model_metrics.gpu_memory_used = inference['metrics'].get('gpu_memory_used')
            model_metrics.cpu_usage = inference['metrics'].get('cpu_usage')
            model_metrics.memory_usage = inference['metrics'].get('memory_usage')
            
            # Update sizes
            model_metrics.input_size = inference['input_data'].get('size')
            model_metrics.output_size = results.get('output_size')
            model_metrics.batch_size = inference['input_data'].get('batch_size', 1)
            
            # Calculate throughput
            if model_metrics.inference_time > 0:
                model_metrics.throughput = model_metrics.batch_size / model_metrics.inference_time
            
            # Update custom metrics
            model_metrics.custom_metrics = results.get('custom_metrics', {})
            
            # Store metrics
            self.model_metrics.append(model_metrics)
            
            # Clean up active inference
            del self.active_inferences[inference_id]
            
            # Check for alerts
            await self._check_performance_alerts(model_metrics)
            
            self.logger.info(f"Completed inference tracking for {inference_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to complete inference tracking: {e}")
    
    def _generate_inference_id(self, model_id: str) -> str:
        """Generate unique inference tracking ID"""
        content = f"{model_id}_{datetime.now().isoformat()}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def _check_performance_alerts(self, metrics -> None: ModelMetrics) -> None:
        """Check for performance alerts and anomalies"""
        try:
            alerts = []
            
            # Check inference time
            if metrics.inference_time > self.alert_thresholds['inference_time_threshold']:
                alerts.append({
                    'type': 'performance',
                    'severity': 'warning',
                    'message': f"High inference time: {metrics.inference_time:.2f}s",
                    'model_id': metrics.model_id
                })
            
            # Check accuracy drop
            if metrics.model_id in self.performance_baselines:
                baseline_accuracy = self.performance_baselines[metrics.model_id].get('accuracy')
                if baseline_accuracy and metrics.accuracy:
                    accuracy_drop = baseline_accuracy - metrics.accuracy
                    if accuracy_drop > self.alert_thresholds['accuracy_drop_threshold']:
                        alerts.append({
                            'type': 'quality',
                            'severity': 'warning',
                            'message': f"Accuracy drop detected: {accuracy_drop:.3f}",
                            'model_id': metrics.model_id
                        })
            
            # Check memory usage
            if metrics.gpu_memory_used and metrics.gpu_memory_used > self.alert_thresholds['memory_threshold'] * 1000:
                alerts.append({
                    'type': 'resource',
                    'severity': 'warning',
                    'message': f"High GPU memory usage: {metrics.gpu_memory_used:.1f}MB",
                    'model_id': metrics.model_id
                })
            
            if alerts:
                self.logger.warning(f"Performance alerts for model {metrics.model_id}: {alerts}")
            
        except Exception as e:
            self.logger.error(f"Performance alert checking failed: {e}")
    
    async def get_model_performance_summary(self, model_id: str, 
                                          hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for a specific model"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter metrics for this model and time period
            model_metrics_list = [
                m for m in self.model_metrics
                if m.model_id == model_id and m.timestamp >= cutoff_time
            ]
            
            if not model_metrics_list:
                return {'message': f'No metrics available for model {model_id}'}
            
            # Calculate summary statistics
            summary = {
                'model_id': model_id,
                'analysis_period': f"Last {hours} hours",
                'total_inferences': len(model_metrics_list),
                'metrics': {}
            }
            
            # Inference time statistics
            inference_times = [m.inference_time for m in model_metrics_list]
            summary['metrics']['inference_time'] = {
                'mean': np.mean(inference_times),
                'median': np.median(inference_times),
                'min': np.min(inference_times),
                'max': np.max(inference_times),
                'std': np.std(inference_times)
            }
            
            # Throughput statistics
            throughputs = [m.throughput for m in model_metrics_list if m.throughput > 0]
            if throughputs:
                summary['metrics']['throughput'] = {
                    'mean': np.mean(throughputs),
                    'median': np.median(throughputs),
                    'min': np.min(throughputs),
                    'max': np.max(throughputs)
                }
            
            # Accuracy statistics
            accuracies = [m.accuracy for m in model_metrics_list if m.accuracy is not None]
            if accuracies:
                summary['metrics']['accuracy'] = {
                    'mean': np.mean(accuracies),
                    'median': np.median(accuracies),
                    'min': np.min(accuracies),
                    'max': np.max(accuracies),
                    'std': np.std(accuracies)
                }
            
            # Resource usage statistics
            gpu_memory_usage = [m.gpu_memory_used for m in model_metrics_list if m.gpu_memory_used]
            if gpu_memory_usage:
                summary['metrics']['gpu_memory'] = {
                    'mean': np.mean(gpu_memory_usage),
                    'max': np.max(gpu_memory_usage)
                }
            
            # Error statistics
            error_counts = [m.error_count for m in model_metrics_list]
            total_errors = sum(error_counts)
            summary['metrics']['error_rate'] = total_errors / len(model_metrics_list) if model_metrics_list else 0
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Model performance summary generation failed: {e}")
            return {'error': str(e)}


class AIInsightEngine:
    """AI processing insights generation and analysis"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Insight storage
        self.insights_history: deque = deque(maxlen=1000)
        
        # Insight generation rules
        self.insight_rules = self._initialize_insight_rules()
        
    def _initialize_insight_rules(self) -> Dict[str, Callable]:
        """Initialize insight generation rules"""
        return {
            'performance_degradation': self._detect_performance_degradation,
            'resource_optimization': self._detect_resource_optimization_opportunities,
            'quality_anomalies': self._detect_quality_anomalies,
            'capacity_planning': self._generate_capacity_insights,
            'model_lifecycle': self._analyze_model_lifecycle
        }
    
    async def generate_insights(self, metrics_data: List[ModelMetrics]) -> List[ProcessingInsight]:
        """Generate AI processing insights from metrics data"""
        try:
            insights = []
            
            # Run all insight generation rules
            for rule_name, rule_func in self.insight_rules.items():
                try:
                    rule_insights = await rule_func(metrics_data)
                    insights.extend(rule_insights)
                except Exception as e:
                    self.logger.error(f"Insight rule {rule_name} failed: {e}")
            
            # Store insights
            self.insights_history.extend(insights)
            
            # Sort by severity and timestamp
            insights.sort(key=lambda x: (x.severity, x.timestamp), reverse=True)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {e}")
            return []
    
    async def _detect_performance_degradation(self, metrics_data: List[ModelMetrics]) -> List[ProcessingInsight]:
        """Detect performance degradation patterns"""
        insights = []
        
        try:
            # Group by model
            model_groups = defaultdict(list)
            for metric in metrics_data:
                model_groups[metric.model_id].append(metric)
            
            for model_id, model_metrics in model_groups.items():
                if len(model_metrics) < 10:  # Need sufficient data
                    continue
                
                # Sort by timestamp
                model_metrics.sort(key=lambda x: x.timestamp)
                
                # Analyze inference time trend
                recent_times = [m.inference_time for m in model_metrics[-5:]]
                older_times = [m.inference_time for m in model_metrics[-10:-5]]
                
                if recent_times and older_times:
                    recent_avg = np.mean(recent_times)
                    older_avg = np.mean(older_times)
                    
                    if recent_avg > older_avg * 1.2:  # 20% increase
                        insights.append(ProcessingInsight(
                            insight_id=f"perf_deg_{model_id}_{int(time.time())}",
                            timestamp=datetime.now(),
                            insight_type="performance",
                            severity="medium",
                            title="Performance Degradation Detected",
                            description=f"Model {model_id} showing 20% increase in inference time",
                            affected_models=[model_id],
                            metrics_involved=["inference_time"],
                            recommendations=[
                                "Check model cache efficiency",
                                "Monitor system resource availability",
                                "Consider model optimization"
                            ],
                            supporting_data={
                                "recent_avg_time": recent_avg,
                                "previous_avg_time": older_avg,
                                "degradation_percentage": ((recent_avg - older_avg) / older_avg) * 100
                            }
                        ))
            
        except Exception as e:
            self.logger.error(f"Performance degradation detection failed: {e}")
        
        return insights
    
    async def _detect_resource_optimization_opportunities(self, metrics_data: List[ModelMetrics]) -> List[ProcessingInsight]:
        """Detect resource optimization opportunities"""
        insights = []
        
        try:
            # Analyze GPU memory usage patterns
            gpu_usage = [m.gpu_memory_used for m in metrics_data if m.gpu_memory_used]
            
            if gpu_usage:
                avg_usage = np.mean(gpu_usage)
                max_usage = np.max(gpu_usage)
                
                # Low utilization insight
                if avg_usage < 500:  # Less than 500MB average
                    insights.append(ProcessingInsight(
                        insight_id=f"gpu_low_util_{int(time.time())}",
                        timestamp=datetime.now(),
                        insight_type="optimization",
                        severity="low",
                        title="Low GPU Utilization",
                        description="GPU memory utilization is consistently low",
                        recommendations=[
                            "Consider increasing batch sizes",
                            "Evaluate model precision settings",
                            "Optimize GPU memory allocation"
                        ],
                        supporting_data={"average_usage_mb": avg_usage}
                    ))
                
                # High utilization insight
                elif avg_usage > 8000:  # More than 8GB average
                    insights.append(ProcessingInsight(
                        insight_id=f"gpu_high_util_{int(time.time())}",
                        timestamp=datetime.now(),
                        insight_type="optimization",
                        severity="medium",
                        title="High GPU Memory Usage",
                        description="GPU memory utilization is consistently high",
                        recommendations=[
                            "Consider reducing batch sizes",
                            "Implement model quantization",
                            "Add memory monitoring alerts"
                        ],
                        supporting_data={"average_usage_mb": avg_usage}
                    ))
            
        except Exception as e:
            self.logger.error(f"Resource optimization detection failed: {e}")
        
        return insights
    
    async def _detect_quality_anomalies(self, metrics_data: List[ModelMetrics]) -> List[ProcessingInsight]:
        """Detect quality anomalies and outliers"""
        insights = []
        
        try:
            # Analyze output quality scores
            quality_scores = [m.output_quality_score for m in metrics_data if m.output_quality_score]
            
            if len(quality_scores) > 10:
                mean_quality = np.mean(quality_scores)
                std_quality = np.std(quality_scores)
                
                # Find outliers (more than 2 standard deviations from mean)
                outliers = [score for score in quality_scores if abs(score - mean_quality) > 2 * std_quality]
                
                if len(outliers) > len(quality_scores) * 0.1:  # More than 10% outliers
                    insights.append(ProcessingInsight(
                        insight_id=f"quality_anomaly_{int(time.time())}",
                        timestamp=datetime.now(),
                        insight_type="quality",
                        severity="medium",
                        title="Quality Score Anomalies Detected",
                        description=f"Detected {len(outliers)} quality outliers in recent processing",
                        recommendations=[
                            "Review input data quality",
                            "Check model calibration",
                            "Validate preprocessing pipeline"
                        ],
                        supporting_data={
                            "outlier_count": len(outliers),
                            "total_samples": len(quality_scores),
                            "mean_quality": mean_quality,
                            "quality_std": std_quality
                        }
                    ))
            
        except Exception as e:
            self.logger.error(f"Quality anomaly detection failed: {e}")
        
        return insights
    
    async def _generate_capacity_insights(self, metrics_data: List[ModelMetrics]) -> List[ProcessingInsight]:
        """Generate capacity planning insights"""
        insights = []
        
        try:
            if len(metrics_data) < 50:  # Need sufficient data
                return insights
            
            # Analyze throughput trends
            recent_metrics = sorted(metrics_data, key=lambda x: x.timestamp)[-20:]
            throughputs = [m.throughput for m in recent_metrics if m.throughput > 0]
            
            if throughputs:
                avg_throughput = np.mean(throughputs)
                
                # Capacity recommendations based on throughput
                if avg_throughput < 1.0:  # Less than 1 sample/second
                    insights.append(ProcessingInsight(
                        insight_id=f"capacity_low_{int(time.time())}",
                        timestamp=datetime.now(),
                        insight_type="capacity",
                        severity="medium",
                        title="Low Processing Throughput",
                        description="Current processing throughput may limit scalability",
                        recommendations=[
                            "Consider parallel processing",
                            "Optimize model inference speed",
                            "Evaluate hardware upgrade options"
                        ],
                        supporting_data={"current_throughput": avg_throughput}
                    ))
            
        except Exception as e:
            self.logger.error(f"Capacity insights generation failed: {e}")
        
        return insights
    
    async def _analyze_model_lifecycle(self, metrics_data: List[ModelMetrics]) -> List[ProcessingInsight]:
        """Analyze model lifecycle and retraining needs"""
        insights = []
        
        try:
            # Group by model
            model_groups = defaultdict(list)
            for metric in metrics_data:
                model_groups[metric.model_id].append(metric)
            
            for model_id, model_metrics in model_groups.items():
                if len(model_metrics) < 100:  # Need sufficient data
                    continue
                
                # Analyze accuracy trends
                sorted_metrics = sorted(model_metrics, key=lambda x: x.timestamp)
                accuracies = [m.accuracy for m in sorted_metrics if m.accuracy is not None]
                
                if len(accuracies) > 20:
                    # Check for declining accuracy trend
                    recent_acc = np.mean(accuracies[-10:])
                    older_acc = np.mean(accuracies[:10])
                    
                    if recent_acc < older_acc * 0.95:  # 5% decline
                        insights.append(ProcessingInsight(
                            insight_id=f"model_lifecycle_{model_id}_{int(time.time())}",
                            timestamp=datetime.now(),
                            insight_type="model_lifecycle",
                            severity="high",
                            title="Model Performance Decline",
                            description=f"Model {model_id} showing accuracy decline, may need retraining",
                            affected_models=[model_id],
                            recommendations=[
                                "Schedule model retraining",
                                "Collect additional training data",
                                "Review data distribution shifts"
                            ],
                            supporting_data={
                                "recent_accuracy": recent_acc,
                                "baseline_accuracy": older_acc,
                                "decline_percentage": ((older_acc - recent_acc) / older_acc) * 100
                            }
                        ))
            
        except Exception as e:
            self.logger.error(f"Model lifecycle analysis failed: {e}")
        
        return insights


class PredictionAnalytics:
    """Prediction and forecasting analytics for AI processing"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
    
    async def generate_performance_predictions(self, metrics_data: List[ModelMetrics],
                                             horizon_hours: int = 24) -> PredictionAnalytics:
        """Generate performance predictions and forecasts"""
        try:
            prediction = PredictionAnalytics(
                analysis_timestamp=datetime.now(),
                prediction_horizon=timedelta(hours=horizon_hours)
            )
            
            if len(metrics_data) < 10:
                return prediction
            
            # Predict throughput
            throughputs = [m.throughput for m in metrics_data if m.throughput > 0]
            if throughputs:
                # Simple trend-based prediction
                recent_throughput = np.mean(throughputs[-10:])
                prediction.predicted_throughput = recent_throughput
            
            # Predict accuracy
            accuracies = [m.accuracy for m in metrics_data if m.accuracy is not None]
            if accuracies:
                recent_accuracy = np.mean(accuracies[-10:])
                prediction.predicted_accuracy = recent_accuracy
            
            # Resource usage predictions
            gpu_usage = [m.gpu_memory_used for m in metrics_data if m.gpu_memory_used]
            if gpu_usage:
                predicted_gpu = np.mean(gpu_usage[-10:])
                prediction.predicted_resource_usage['gpu_memory'] = predicted_gpu
            
            # Generate recommendations
            prediction.capacity_recommendations = await self._generate_capacity_recommendations(metrics_data)
            prediction.scaling_suggestions = await self._generate_scaling_suggestions(metrics_data)
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Performance prediction generation failed: {e}")
            return PredictionAnalytics(
                analysis_timestamp=datetime.now(),
                prediction_horizon=timedelta(hours=horizon_hours)
            )
    
    async def _generate_capacity_recommendations(self, metrics_data: List[ModelMetrics]) -> List[str]:
        """Generate capacity planning recommendations"""
        recommendations = []
        
        try:
            if len(metrics_data) < 10:
                return recommendations
            
            # Analyze resource trends
            gpu_usage = [m.gpu_memory_used for m in metrics_data if m.gpu_memory_used]
            inference_times = [m.inference_time for m in metrics_data]
            
            # GPU memory recommendations
            if gpu_usage:
                avg_gpu = np.mean(gpu_usage)
                max_gpu = np.max(gpu_usage)
                
                if max_gpu > 8000:  # More than 8GB
                    recommendations.append("Consider upgrading to higher memory GPU")
                elif avg_gpu < 2000:  # Less than 2GB average
                    recommendations.append("Current GPU capacity is sufficient for workload")
            
            # Processing speed recommendations
            if inference_times:
                avg_time = np.mean(inference_times)
                
                if avg_time > 2.0:  # More than 2 seconds
                    recommendations.append("Consider parallel processing or model optimization")
                elif avg_time < 0.1:  # Less than 100ms
                    recommendations.append("Excellent processing speed, consider increasing batch size")
            
        except Exception as e:
            self.logger.error(f"Capacity recommendations generation failed: {e}")
        
        return recommendations
    
    async def _generate_scaling_suggestions(self, metrics_data: List[ModelMetrics]) -> List[str]:
        """Generate scaling suggestions"""
        suggestions = []
        
        try:
            # Analyze load patterns
            throughputs = [m.throughput for m in metrics_data if m.throughput > 0]
            
            if throughputs:
                avg_throughput = np.mean(throughputs)
                throughput_var = np.var(throughputs)
                
                if avg_throughput < 5.0:  # Low throughput
                    suggestions.append("Consider horizontal scaling with multiple model instances")
                
                if throughput_var > avg_throughput:  # High variability
                    suggestions.append("Implement dynamic scaling based on demand")
                
                if avg_throughput > 50.0:  # High throughput
                    suggestions.append("Current scaling is adequate for workload")
            
        except Exception as e:
            self.logger.error(f"Scaling suggestions generation failed: {e}")
        
        return suggestions