"""🤖 AI Processing Performance Monitor - IA Influencer Agent Platform
=====================================================================

Advanced AI processing performance monitoring, optimization tracking, and intelligence
system for monitoring IA model performance, processing efficiency, and optimization results.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic Integration:
Content Input → IA Analysis → Processing Optimization → Quality Enhancement → Performance Tracking
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import json
from collections import defaultdict
import statistics
import time

logger = logging.getLogger(__name__)


class AIProcessingStage(Enum):
    """AI processing stages in the platform"""
    CONTENT_ANALYSIS = "content_analysis"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    SEO_OPTIMIZATION = "seo_optimization"
    CONTENT_GENERATION = "content_generation"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    FRAUD_DETECTION = "fraud_detection"
    CONTENT_MODERATION = "content_moderation"
    PERSONALIZATION = "personalization"


class AIModelType(Enum):
    """Types of AI models in the system"""
    LANGUAGE_MODEL = "language_model"
    VISION_MODEL = "vision_model"
    AUDIO_MODEL = "audio_model"
    RECOMMENDATION_MODEL = "recommendation_model"
    CLASSIFICATION_MODEL = "classification_model"
    GENERATION_MODEL = "generation_model"
    ENHANCEMENT_MODEL = "enhancement_model"
    OPTIMIZATION_MODEL = "optimization_model"


class ProcessingComplexity(Enum):
    """Processing complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class AIProcessingMetrics:
    """Comprehensive AI processing performance metrics"""
    processing_id: str
    stage: AIProcessingStage
    model_type: AIModelType
    
    # Performance metrics
    processing_time_ms: int = 0
    accuracy_score: float = 0.0
    confidence_score: float = 0.0
    efficiency_score: float = 0.0
    
    # Resource metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_usage_percent: float = 0.0
    network_io_mb: float = 0.0
    
    # Quality metrics
    output_quality_score: float = 0.0
    error_rate: float = 0.0
    success_rate: float = 1.0
    
    # Optimization metrics
    optimization_applied: bool = False
    performance_improvement: float = 0.0
    resource_optimization: float = 0.0
    
    # Business metrics
    cost_per_operation: Decimal = Decimal('0')
    throughput_per_second: float = 0.0
    scalability_factor: float = 1.0
    
    # Input/Output metrics
    input_size_kb: float = 0.0
    output_size_kb: float = 0.0
    processing_complexity: ProcessingComplexity = ProcessingComplexity.MEDIUM
    
    # Model-specific metrics
    model_version: str = "1.0.0"
    model_confidence: float = 0.0
    training_timestamp: Optional[datetime] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    platform: str = "default"
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class AIModelPerformanceProfile:
    """AI model performance profile and analytics"""
    model_id: str
    model_type: AIModelType
    model_version: str
    
    # Performance statistics
    average_processing_time_ms: float = 0.0
    median_processing_time_ms: float = 0.0
    p95_processing_time_ms: float = 0.0
    p99_processing_time_ms: float = 0.0
    
    # Accuracy statistics
    average_accuracy: float = 0.0
    accuracy_variance: float = 0.0
    accuracy_trend: str = "stable"
    
    # Resource efficiency
    average_cpu_usage: float = 0.0
    average_memory_usage: float = 0.0
    average_gpu_usage: float = 0.0
    resource_efficiency_score: float = 0.0
    
    # Throughput metrics
    peak_throughput: float = 0.0
    average_throughput: float = 0.0
    sustained_throughput: float = 0.0
    
    # Quality metrics
    average_output_quality: float = 0.0
    error_rate_percentage: float = 0.0
    success_rate_percentage: float = 100.0
    
    # Cost metrics
    average_cost_per_operation: Decimal = Decimal('0')
    cost_efficiency_score: float = 0.0
    
    # Optimization metrics
    optimization_opportunities: List[str] = field(default_factory=list)
    performance_bottlenecks: List[str] = field(default_factory=list)
    
    # Usage statistics
    total_operations: int = 0
    operations_per_day: float = 0.0
    last_operation: Optional[datetime] = None
    
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AIProcessingOptimizationRecommendations:
    """AI processing optimization recommendations"""
    model_id: str
    
    # Performance optimizations
    performance_recommendations: List[str] = field(default_factory=list)
    resource_optimizations: List[str] = field(default_factory=list)
    
    # Model optimizations
    model_tuning_suggestions: List[str] = field(default_factory=list)
    architecture_improvements: List[str] = field(default_factory=list)
    
    # Infrastructure optimizations
    infrastructure_recommendations: List[str] = field(default_factory=list)
    scaling_suggestions: List[str] = field(default_factory=list)
    
    # Cost optimizations
    cost_reduction_opportunities: List[str] = field(default_factory=list)
    efficiency_improvements: List[str] = field(default_factory=list)
    
    # Priority scoring
    high_priority_items: List[str] = field(default_factory=list)
    medium_priority_items: List[str] = field(default_factory=list)
    low_priority_items: List[str] = field(default_factory=list)
    
    # Expected impact
    estimated_performance_gain: float = 0.0
    estimated_cost_savings: Decimal = Decimal('0')
    estimated_resource_savings: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.now)


class AIProcessingPerformanceMonitor:
    """
    Advanced AI processing performance monitoring system providing comprehensive
    analytics, optimization tracking, and performance insights for AI models.
    """
    
    def __init__(self):
        self.processing_metrics: Dict[str, List[AIProcessingMetrics]] = defaultdict(list)
        self.model_profiles: Dict[str, AIModelPerformanceProfile] = {}
        self.optimization_recommendations: Dict[str, AIProcessingOptimizationRecommendations] = {}
        
        # Performance thresholds
        self.performance_thresholds = {
            "max_processing_time_ms": 5000,  # 5 seconds max
            "min_accuracy_score": 0.85,      # 85% minimum accuracy
            "max_error_rate": 0.05,          # 5% maximum error rate
            "min_efficiency_score": 0.7,     # 70% minimum efficiency
            "max_cpu_usage": 80.0,           # 80% maximum CPU usage
            "max_memory_usage": 4096.0,      # 4GB maximum memory usage
        }
        
        # Model performance baselines
        self.performance_baselines = {
            AIModelType.LANGUAGE_MODEL: {
                "target_processing_time_ms": 1000,
                "target_accuracy": 0.92,
                "target_throughput": 100.0
            },
            AIModelType.VISION_MODEL: {
                "target_processing_time_ms": 2000,
                "target_accuracy": 0.90,
                "target_throughput": 50.0
            },
            AIModelType.AUDIO_MODEL: {
                "target_processing_time_ms": 3000,
                "target_accuracy": 0.88,
                "target_throughput": 30.0
            }
        }
    
    async def track_ai_processing(
        self,
        processing_id: str,
        stage: AIProcessingStage,
        model_type: AIModelType,
        processing_data: Dict[str, Any]
    ) -> AIProcessingMetrics:
        """
        Track AI processing performance and generate comprehensive metrics
        """
        try:
            # Record processing start time
            start_time = time.time()
            
            # Simulate or extract processing metrics
            metrics = await self._collect_processing_metrics(
                processing_id, stage, model_type, processing_data, start_time
            )
            
            # Analyze performance against thresholds
            await self._analyze_performance_compliance(metrics)
            
            # Update model profile
            await self._update_model_profile(metrics)
            
            # Store metrics
            model_key = f"{model_type.value}_{metrics.model_version}"
            self.processing_metrics[model_key].append(metrics)
            
            # Limit history to last 1000 entries per model
            if len(self.processing_metrics[model_key]) > 1000:
                self.processing_metrics[model_key] = self.processing_metrics[model_key][-1000:]
            
            # Generate optimization recommendations if performance issues detected
            if await self._requires_optimization(metrics):
                await self._generate_optimization_recommendations(model_key, metrics)
            
            logger.info(f"AI processing tracked: {processing_id} - {stage.value}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error tracking AI processing {processing_id}: {e}")
            # Return default metrics on error
            return AIProcessingMetrics(
                processing_id=processing_id,
                stage=stage,
                model_type=model_type
            )
    
    async def generate_model_performance_report(
        self,
        model_type: AIModelType,
        model_version: str = "latest",
        timeframe: timedelta = timedelta(days=7)
    ) -> AIModelPerformanceProfile:
        """
        Generate comprehensive performance report for AI model
        """
        try:
            model_key = f"{model_type.value}_{model_version}" if model_version != "latest" else None
            
            # Get relevant metrics
            if model_key:
                metrics_list = self.processing_metrics.get(model_key, [])
            else:
                # Get metrics for all versions of this model type
                metrics_list = []
                for key, metrics in self.processing_metrics.items():
                    if key.startswith(model_type.value):
                        metrics_list.extend(metrics)
            
            # Filter by timeframe
            cutoff_time = datetime.now() - timeframe
            recent_metrics = [m for m in metrics_list if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                logger.warning(f"No recent metrics found for model type {model_type.value}")
                return AIModelPerformanceProfile(
                    model_id=model_key or f"{model_type.value}_unknown",
                    model_type=model_type,
                    model_version=model_version
                )
            
            # Calculate performance statistics
            profile = await self._calculate_model_performance_profile(
                model_type, model_version, recent_metrics
            )
            
            # Store profile
            profile_key = f"{model_type.value}_{model_version}"
            self.model_profiles[profile_key] = profile
            
            logger.info(f"Performance report generated for {model_type.value}")
            return profile
            
        except Exception as e:
            logger.error(f"Error generating performance report for {model_type.value}: {e}")
            return AIModelPerformanceProfile(
                model_id=f"{model_type.value}_error",
                model_type=model_type,
                model_version=model_version
            )
    
    async def get_ai_processing_dashboard(
        self,
        model_type: Optional[AIModelType] = None,
        timeframe: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI processing dashboard data
        """
        try:
            # Get relevant metrics
            all_metrics = []
            for key, metrics_list in self.processing_metrics.items():
                if model_type is None or key.startswith(model_type.value):
                    all_metrics.extend(metrics_list)
            
            # Filter by timeframe
            cutoff_time = datetime.now() - timeframe
            recent_metrics = [m for m in all_metrics if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return {"error": "No recent AI processing data available"}
            
            # Calculate dashboard metrics
            dashboard_data = {
                "timeframe": str(timeframe),
                "last_updated": datetime.now().isoformat(),
                "total_operations": len(recent_metrics),
                
                # Performance overview
                "performance_overview": await self._calculate_performance_overview(recent_metrics),
                
                # Model-specific metrics
                "model_performance": await self._calculate_model_metrics(recent_metrics),
                
                # Resource utilization
                "resource_utilization": await self._calculate_resource_metrics(recent_metrics),
                
                # Quality metrics
                "quality_metrics": await self._calculate_quality_metrics(recent_metrics),
                
                # Optimization insights
                "optimization_insights": await self._calculate_optimization_insights(recent_metrics),
                
                # Trend data
                "trend_data": await self._generate_trend_data(recent_metrics),
                
                # Alerts and recommendations
                "alerts": await self._generate_performance_alerts(recent_metrics),
                "recommendations": await self._get_top_recommendations()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating AI processing dashboard: {e}")
            return {"error": str(e)}
    
    async def optimize_model_performance(
        self,
        model_type: AIModelType,
        model_version: str,
        optimization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply performance optimizations to AI model based on analysis
        """
        try:
            model_key = f"{model_type.value}_{model_version}"
            
            # Get current performance profile
            profile = self.model_profiles.get(model_key)
            if not profile:
                profile = await self.generate_model_performance_report(model_type, model_version)
            
            # Apply optimizations based on configuration
            optimization_results = await self._apply_optimizations(
                model_key, profile, optimization_config
            )
            
            # Record optimization attempt
            await self._record_optimization_attempt(model_key, optimization_results)
            
            logger.info(f"Model optimization completed for {model_key}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing model {model_type.value}: {e}")
            return {"error": str(e), "success": False}
    
    # Helper methods for metric collection and analysis
    
    async def _collect_processing_metrics(
        self,
        processing_id: str,
        stage: AIProcessingStage,
        model_type: AIModelType,
        processing_data: Dict[str, Any],
        start_time: float
    ) -> AIProcessingMetrics:
        """Collect comprehensive processing metrics"""
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract or simulate metrics based on processing data
        accuracy_score = processing_data.get("accuracy", 0.85 + (processing_time_ms % 100) / 1000)
        confidence_score = processing_data.get("confidence", accuracy_score * 0.9)
        
        # Calculate efficiency score based on processing time and accuracy
        baseline = self.performance_baselines.get(model_type, {})
        target_time = baseline.get("target_processing_time_ms", 2000)
        efficiency_score = min(1.0, target_time / max(processing_time_ms, 1))
        
        # Simulate resource usage
        complexity = processing_data.get("complexity", ProcessingComplexity.MEDIUM)
        complexity_multiplier = {
            ProcessingComplexity.LOW: 0.5,
            ProcessingComplexity.MEDIUM: 1.0,
            ProcessingComplexity.HIGH: 1.5,
            ProcessingComplexity.EXTREME: 2.0
        }.get(complexity, 1.0)
        
        cpu_usage = min(100.0, 30 + (processing_time_ms / 100) * complexity_multiplier)
        memory_usage = min(4096.0, 512 + (processing_time_ms / 10) * complexity_multiplier)
        gpu_usage = min(100.0, 20 + (processing_time_ms / 200) * complexity_multiplier) if model_type in [
            AIModelType.VISION_MODEL, AIModelType.GENERATION_MODEL
        ] else 0.0
        
        # Calculate quality metrics
        output_quality_score = min(1.0, accuracy_score * confidence_score)
        error_rate = max(0.0, (1.0 - accuracy_score) * 0.1)
        success_rate = 1.0 - error_rate
        
        # Calculate business metrics
        cost_per_operation = Decimal(str(processing_time_ms / 1000 * 0.01))  # $0.01 per second
        throughput_per_second = 1000.0 / max(processing_time_ms, 1)
        
        # Input/output size simulation
        input_size_kb = processing_data.get("input_size_kb", 100.0)
        output_size_kb = processing_data.get("output_size_kb", input_size_kb * 0.8)
        
        return AIProcessingMetrics(
            processing_id=processing_id,
            stage=stage,
            model_type=model_type,
            processing_time_ms=processing_time_ms,
            accuracy_score=accuracy_score,
            confidence_score=confidence_score,
            efficiency_score=efficiency_score,
            cpu_usage_percent=cpu_usage,
            memory_usage_mb=memory_usage,
            gpu_usage_percent=gpu_usage,
            output_quality_score=output_quality_score,
            error_rate=error_rate,
            success_rate=success_rate,
            cost_per_operation=cost_per_operation,
            throughput_per_second=throughput_per_second,
            input_size_kb=input_size_kb,
            output_size_kb=output_size_kb,
            processing_complexity=complexity,
            model_version=processing_data.get("model_version", "1.0.0"),
            model_confidence=confidence_score,
            user_id=processing_data.get("user_id"),
            content_id=processing_data.get("content_id"),
            platform=processing_data.get("platform", "default")
        )
    
    async def _analyze_performance_compliance(self, metrics: AIProcessingMetrics):
        """Analyze performance against defined thresholds"""
        compliance_issues = []
        
        if metrics.processing_time_ms > self.performance_thresholds["max_processing_time_ms"]:
            compliance_issues.append(f"Processing time exceeded threshold: {metrics.processing_time_ms}ms")
        
        if metrics.accuracy_score < self.performance_thresholds["min_accuracy_score"]:
            compliance_issues.append(f"Accuracy below threshold: {metrics.accuracy_score:.3f}")
        
        if metrics.error_rate > self.performance_thresholds["max_error_rate"]:
            compliance_issues.append(f"Error rate exceeded threshold: {metrics.error_rate:.3f}")
        
        if metrics.cpu_usage_percent > self.performance_thresholds["max_cpu_usage"]:
            compliance_issues.append(f"CPU usage exceeded threshold: {metrics.cpu_usage_percent:.1f}%")
        
        if compliance_issues:
            logger.warning(f"Performance compliance issues detected: {compliance_issues}")
            # In production, this would trigger alerts
    
    async def _update_model_profile(self, metrics: AIProcessingMetrics):
        """Update model performance profile with new metrics"""
        model_key = f"{metrics.model_type.value}_{metrics.model_version}"
        
        if model_key not in self.model_profiles:
            self.model_profiles[model_key] = AIModelPerformanceProfile(
                model_id=model_key,
                model_type=metrics.model_type,
                model_version=metrics.model_version
            )
        
        profile = self.model_profiles[model_key]
        
        # Update operation counts
        profile.total_operations += 1
        profile.last_operation = metrics.timestamp
        
        # Update running averages (simplified moving average)
        alpha = 0.1  # Learning rate for moving average
        
        profile.average_processing_time_ms = (
            profile.average_processing_time_ms * (1 - alpha) + 
            metrics.processing_time_ms * alpha
        )
        
        profile.average_accuracy = (
            profile.average_accuracy * (1 - alpha) + 
            metrics.accuracy_score * alpha
        )
        
        profile.average_cpu_usage = (
            profile.average_cpu_usage * (1 - alpha) + 
            metrics.cpu_usage_percent * alpha
        )
        
        profile.average_memory_usage = (
            profile.average_memory_usage * (1 - alpha) + 
            metrics.memory_usage_mb * alpha
        )
        
        profile.average_output_quality = (
            profile.average_output_quality * (1 - alpha) + 
            metrics.output_quality_score * alpha
        )
        
        # Update throughput
        profile.average_throughput = (
            profile.average_throughput * (1 - alpha) + 
            metrics.throughput_per_second * alpha
        )
        
        if metrics.throughput_per_second > profile.peak_throughput:
            profile.peak_throughput = metrics.throughput_per_second
        
        # Update cost metrics
        profile.average_cost_per_operation = (
            profile.average_cost_per_operation * Decimal(str(1 - alpha)) + 
            metrics.cost_per_operation * Decimal(str(alpha))
        )
    
    async def _requires_optimization(self, metrics: AIProcessingMetrics) -> bool:
        """Determine if model requires optimization based on performance"""
        # Check if any critical thresholds are exceeded
        if (metrics.processing_time_ms > self.performance_thresholds["max_processing_time_ms"] or
            metrics.accuracy_score < self.performance_thresholds["min_accuracy_score"] or
            metrics.error_rate > self.performance_thresholds["max_error_rate"] or
            metrics.efficiency_score < self.performance_thresholds["min_efficiency_score"]):
            return True
        
        return False
    
    async def _generate_optimization_recommendations(
        self, 
        model_key: str, 
        metrics: AIProcessingMetrics
    ):
        """Generate optimization recommendations based on performance analysis"""
        recommendations = AIProcessingOptimizationRecommendations(model_id=model_key)
        
        # Performance recommendations
        if metrics.processing_time_ms > self.performance_thresholds["max_processing_time_ms"]:
            recommendations.performance_recommendations.extend([
                "Optimize model architecture for faster inference",
                "Implement model quantization",
                "Consider GPU acceleration",
                "Optimize input preprocessing pipeline"
            ])
            recommendations.high_priority_items.append("Reduce processing time")
        
        # Accuracy recommendations
        if metrics.accuracy_score < self.performance_thresholds["min_accuracy_score"]:
            recommendations.model_tuning_suggestions.extend([
                "Retrain model with additional data",
                "Adjust model hyperparameters",
                "Implement ensemble methods",
                "Review training data quality"
            ])
            recommendations.high_priority_items.append("Improve model accuracy")
        
        # Resource optimization
        if metrics.cpu_usage_percent > self.performance_thresholds["max_cpu_usage"]:
            recommendations.resource_optimizations.extend([
                "Implement CPU usage optimization",
                "Consider horizontal scaling",
                "Optimize computation pipelines",
                "Implement caching strategies"
            ])
            recommendations.medium_priority_items.append("Optimize CPU usage")
        
        # Cost optimization
        if float(metrics.cost_per_operation) > 0.05:  # $0.05 threshold
            recommendations.cost_reduction_opportunities.extend([
                "Optimize resource allocation",
                "Implement request batching",
                "Consider cost-efficient infrastructure",
                "Optimize model complexity"
            ])
            recommendations.medium_priority_items.append("Reduce operational costs")
        
        # Estimate impact
        recommendations.estimated_performance_gain = min(0.5, max(0.1, 
            (self.performance_thresholds["max_processing_time_ms"] - metrics.processing_time_ms) / 
            self.performance_thresholds["max_processing_time_ms"]
        ))
        
        recommendations.estimated_cost_savings = Decimal(str(float(metrics.cost_per_operation) * 0.3))
        recommendations.estimated_resource_savings = min(0.4, metrics.cpu_usage_percent / 100 * 0.3)
        
        self.optimization_recommendations[model_key] = recommendations
    
    # Dashboard calculation methods
    
    async def _calculate_performance_overview(self, metrics: List[AIProcessingMetrics]) -> Dict[str, Any]:
        """Calculate performance overview metrics"""
        if not metrics:
            return {}
        
        processing_times = [m.processing_time_ms for m in metrics]
        accuracy_scores = [m.accuracy_score for m in metrics]
        efficiency_scores = [m.efficiency_score for m in metrics]
        
        return {
            "average_processing_time_ms": statistics.mean(processing_times),
            "median_processing_time_ms": statistics.median(processing_times),
            "p95_processing_time_ms": sorted(processing_times)[int(len(processing_times) * 0.95)] if len(processing_times) > 20 else max(processing_times),
            "average_accuracy": statistics.mean(accuracy_scores),
            "accuracy_variance": statistics.variance(accuracy_scores) if len(accuracy_scores) > 1 else 0,
            "average_efficiency": statistics.mean(efficiency_scores),
            "total_operations": len(metrics),
            "success_rate": statistics.mean([m.success_rate for m in metrics])
        }
    
    async def _calculate_model_metrics(self, metrics: List[AIProcessingMetrics]) -> Dict[str, Dict]:
        """Calculate model-specific performance metrics"""
        model_metrics = {}
        
        # Group by model type
        by_model = defaultdict(list)
        for metric in metrics:
            by_model[metric.model_type.value].append(metric)
        
        for model_type, model_metrics_list in by_model.items():
            processing_times = [m.processing_time_ms for m in model_metrics_list]
            accuracy_scores = [m.accuracy_score for m in model_metrics_list]
            
            model_metrics[model_type] = {
                "operation_count": len(model_metrics_list),
                "average_processing_time": statistics.mean(processing_times),
                "average_accuracy": statistics.mean(accuracy_scores),
                "average_throughput": statistics.mean([m.throughput_per_second for m in model_metrics_list]),
                "success_rate": statistics.mean([m.success_rate for m in model_metrics_list])
            }
        
        return model_metrics
    
    async def _calculate_resource_metrics(self, metrics: List[AIProcessingMetrics]) -> Dict[str, float]:
        """Calculate resource utilization metrics"""
        if not metrics:
            return {}
        
        return {
            "average_cpu_usage": statistics.mean([m.cpu_usage_percent for m in metrics]),
            "peak_cpu_usage": max([m.cpu_usage_percent for m in metrics]),
            "average_memory_usage": statistics.mean([m.memory_usage_mb for m in metrics]),
            "peak_memory_usage": max([m.memory_usage_mb for m in metrics]),
            "average_gpu_usage": statistics.mean([m.gpu_usage_percent for m in metrics]),
            "peak_gpu_usage": max([m.gpu_usage_percent for m in metrics])
        }
    
    async def _calculate_quality_metrics(self, metrics: List[AIProcessingMetrics]) -> Dict[str, float]:
        """Calculate quality metrics"""
        if not metrics:
            return {}
        
        return {
            "average_output_quality": statistics.mean([m.output_quality_score for m in metrics]),
            "average_confidence": statistics.mean([m.confidence_score for m in metrics]),
            "error_rate": statistics.mean([m.error_rate for m in metrics]),
            "quality_variance": statistics.variance([m.output_quality_score for m in metrics]) if len(metrics) > 1 else 0
        }
    
    async def _calculate_optimization_insights(self, metrics: List[AIProcessingMetrics]) -> Dict[str, Any]:
        """Calculate optimization insights"""
        optimization_count = sum(1 for m in metrics if m.optimization_applied)
        total_count = len(metrics)
        
        if optimization_count > 0:
            optimized_metrics = [m for m in metrics if m.optimization_applied]
            average_improvement = statistics.mean([m.performance_improvement for m in optimized_metrics])
        else:
            average_improvement = 0.0
        
        return {
            "optimization_rate": optimization_count / total_count if total_count > 0 else 0,
            "average_performance_improvement": average_improvement,
            "optimization_opportunities": len(self.optimization_recommendations),
            "models_requiring_optimization": len([
                rec for rec in self.optimization_recommendations.values() 
                if rec.high_priority_items
            ])
        }
    
    async def _generate_trend_data(self, metrics: List[AIProcessingMetrics]) -> Dict[str, List]:
        """Generate trend data for charts"""
        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        # Group by hour for trend analysis
        hourly_data = defaultdict(list)
        for metric in sorted_metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_data[hour_key].append(metric)
        
        trend_data = {
            "timestamps": [],
            "processing_times": [],
            "accuracy_scores": [],
            "throughput": [],
            "resource_usage": []
        }
        
        for hour, hour_metrics in sorted(hourly_data.items()):
            trend_data["timestamps"].append(hour.isoformat())
            trend_data["processing_times"].append(statistics.mean([m.processing_time_ms for m in hour_metrics]))
            trend_data["accuracy_scores"].append(statistics.mean([m.accuracy_score for m in hour_metrics]))
            trend_data["throughput"].append(statistics.mean([m.throughput_per_second for m in hour_metrics]))
            trend_data["resource_usage"].append(statistics.mean([m.cpu_usage_percent for m in hour_metrics]))
        
        return trend_data
    
    async def _generate_performance_alerts(self, metrics: List[AIProcessingMetrics]) -> List[Dict[str, str]]:
        """Generate performance alerts based on metrics"""
        alerts = []
        
        # Check for performance issues
        high_processing_times = [m for m in metrics if m.processing_time_ms > self.performance_thresholds["max_processing_time_ms"]]
        if len(high_processing_times) > len(metrics) * 0.1:  # More than 10% of operations
            alerts.append({
                "type": "performance",
                "severity": "high",
                "message": f"{len(high_processing_times)} operations exceeded processing time threshold",
                "recommendation": "Review and optimize model performance"
            })
        
        # Check for accuracy issues
        low_accuracy = [m for m in metrics if m.accuracy_score < self.performance_thresholds["min_accuracy_score"]]
        if len(low_accuracy) > len(metrics) * 0.05:  # More than 5% of operations
            alerts.append({
                "type": "accuracy",
                "severity": "high",
                "message": f"{len(low_accuracy)} operations had low accuracy scores",
                "recommendation": "Review model training and data quality"
            })
        
        # Check for resource issues
        high_cpu_usage = [m for m in metrics if m.cpu_usage_percent > self.performance_thresholds["max_cpu_usage"]]
        if len(high_cpu_usage) > len(metrics) * 0.2:  # More than 20% of operations
            alerts.append({
                "type": "resource",
                "severity": "medium",
                "message": f"{len(high_cpu_usage)} operations had high CPU usage",
                "recommendation": "Consider resource optimization or scaling"
            })
        
        return alerts
    
    async def _get_top_recommendations(self) -> List[Dict[str, str]]:
        """Get top optimization recommendations across all models"""
        recommendations = []
        
        for model_key, rec in self.optimization_recommendations.items():
            for item in rec.high_priority_items:
                recommendations.append({
                    "model": model_key,
                    "priority": "high",
                    "recommendation": item,
                    "estimated_impact": f"{rec.estimated_performance_gain:.1%}"
                })
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def _calculate_model_performance_profile(
        self,
        model_type: AIModelType,
        model_version: str,
        metrics: List[AIProcessingMetrics]
    ) -> AIModelPerformanceProfile:
        """Calculate comprehensive model performance profile"""
        
        processing_times = [m.processing_time_ms for m in metrics]
        accuracy_scores = [m.accuracy_score for m in metrics]
        
        profile = AIModelPerformanceProfile(
            model_id=f"{model_type.value}_{model_version}",
            model_type=model_type,
            model_version=model_version,
            
            # Processing time statistics
            average_processing_time_ms=statistics.mean(processing_times),
            median_processing_time_ms=statistics.median(processing_times),
            p95_processing_time_ms=sorted(processing_times)[int(len(processing_times) * 0.95)] if len(processing_times) > 20 else max(processing_times),
            p99_processing_time_ms=sorted(processing_times)[int(len(processing_times) * 0.99)] if len(processing_times) > 100 else max(processing_times),
            
            # Accuracy statistics
            average_accuracy=statistics.mean(accuracy_scores),
            accuracy_variance=statistics.variance(accuracy_scores) if len(accuracy_scores) > 1 else 0,
            
            # Resource efficiency
            average_cpu_usage=statistics.mean([m.cpu_usage_percent for m in metrics]),
            average_memory_usage=statistics.mean([m.memory_usage_mb for m in metrics]),
            average_gpu_usage=statistics.mean([m.gpu_usage_percent for m in metrics]),
            
            # Throughput metrics
            peak_throughput=max([m.throughput_per_second for m in metrics]),
            average_throughput=statistics.mean([m.throughput_per_second for m in metrics]),
            
            # Quality metrics
            average_output_quality=statistics.mean([m.output_quality_score for m in metrics]),
            error_rate_percentage=statistics.mean([m.error_rate for m in metrics]) * 100,
            success_rate_percentage=statistics.mean([m.success_rate for m in metrics]) * 100,
            
            # Cost metrics
            average_cost_per_operation=Decimal(str(statistics.mean([float(m.cost_per_operation) for m in metrics]))),
            
            # Usage statistics
            total_operations=len(metrics),
            operations_per_day=len(metrics) / 7,  # Assuming 7-day period
            last_operation=max([m.timestamp for m in metrics])
        )
        
        # Calculate efficiency scores
        baseline = self.performance_baselines.get(model_type, {})
        if baseline:
            target_time = baseline.get("target_processing_time_ms", 2000)
            target_accuracy = baseline.get("target_accuracy", 0.85)
            
            profile.resource_efficiency_score = min(1.0, target_time / max(profile.average_processing_time_ms, 1))
            profile.cost_efficiency_score = min(1.0, target_accuracy / max(profile.average_accuracy, 0.1))
        
        # Generate optimization opportunities
        if profile.average_processing_time_ms > baseline.get("target_processing_time_ms", 2000):
            profile.optimization_opportunities.append("Reduce processing time")
        if profile.average_accuracy < baseline.get("target_accuracy", 0.85):
            profile.optimization_opportunities.append("Improve accuracy")
        if profile.average_cpu_usage > 70:
            profile.optimization_opportunities.append("Optimize CPU usage")
        
        return profile
    
    async def _apply_optimizations(
        self,
        model_key: str,
        profile: AIModelPerformanceProfile,
        optimization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply optimizations based on configuration"""
        # In a real implementation, this would apply actual optimizations
        # For now, we'll simulate the optimization results
        
        results = {
            "success": True,
            "optimizations_applied": [],
            "performance_improvements": {},
            "resource_savings": {},
            "estimated_impact": {}
        }
        
        # Simulate optimization applications
        if "reduce_processing_time" in optimization_config:
            results["optimizations_applied"].append("processing_time_optimization")
            results["performance_improvements"]["processing_time_reduction"] = "15%"
            results["estimated_impact"]["processing_time"] = 0.15
        
        if "improve_accuracy" in optimization_config:
            results["optimizations_applied"].append("accuracy_enhancement")
            results["performance_improvements"]["accuracy_improvement"] = "8%"
            results["estimated_impact"]["accuracy"] = 0.08
        
        if "optimize_resources" in optimization_config:
            results["optimizations_applied"].append("resource_optimization")
            results["resource_savings"]["cpu_reduction"] = "25%"
            results["resource_savings"]["memory_reduction"] = "20%"
            results["estimated_impact"]["resource_efficiency"] = 0.25
        
        return results
    
    async def _record_optimization_attempt(self, model_key: str, results: Dict[str, Any]):
        """Record optimization attempt for tracking"""
        # In production, this would be stored in a database
        logger.info(f"Optimization applied to {model_key}: {results['optimizations_applied']}")


# Global AI processing performance monitor instance
ai_processing_monitor = AIProcessingPerformanceMonitor()


# Convenience functions for external use
async def track_ai_processing(
    processing_id: str,
    stage: AIProcessingStage,
    model_type: AIModelType,
    processing_data: Dict[str, Any]
) -> AIProcessingMetrics:
    """Track AI processing performance"""
    return await ai_processing_monitor.track_ai_processing(processing_id, stage, model_type, processing_data)


async def generate_model_report(
    model_type: AIModelType,
    model_version: str = "latest",
    timeframe: timedelta = timedelta(days=7)
) -> AIModelPerformanceProfile:
    """Generate model performance report"""
    return await ai_processing_monitor.generate_model_performance_report(model_type, model_version, timeframe)


async def get_ai_dashboard(
    model_type: Optional[AIModelType] = None,
    timeframe: timedelta = timedelta(hours=24)
) -> Dict[str, Any]:
    """Get AI processing dashboard"""
    return await ai_processing_monitor.get_ai_processing_dashboard(model_type, timeframe)


async def optimize_model(
    model_type: AIModelType,
    model_version: str,
    optimization_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Optimize model performance"""
    return await ai_processing_monitor.optimize_model_performance(model_type, model_version, optimization_config)


def get_model_profile(model_type: AIModelType, model_version: str = "latest") -> Optional[AIModelPerformanceProfile]:
    """Get model performance profile"""
    model_key = f"{model_type.value}_{model_version}"
    return ai_processing_monitor.model_profiles.get(model_key)


def get_optimization_recommendations(model_type: AIModelType, model_version: str = "latest") -> Optional[AIProcessingOptimizationRecommendations]:
    """Get optimization recommendations for model"""
    model_key = f"{model_type.value}_{model_version}"
    return ai_processing_monitor.optimization_recommendations.get(model_key)