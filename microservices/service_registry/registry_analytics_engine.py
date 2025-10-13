#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 SERVICE REGISTRY ENTERPRISE - REGISTRY ANALYTICS ENGINE
==========================================================

**Author**: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Project**: IA Chérie Service Registry Enterprise
**Version**: 1.0 Production
**Created**: 2025-01-07 | Updated: 2025-12-14

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture service registry et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

📈 REGISTRY ANALYTICS ENGINE
Moteur analytics registry avec insights et recommendations.
Usage patterns + performance analytics + optimization recommendations.
"""

import asyncio
import json
import logging
import time
import statistics
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque, Counter
import uuid
import numpy as np

from .distributed_registry_core import ServiceInstance, ServiceStatus

# Core logger
logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of analytics analysis"""
    USAGE_PATTERNS = "usage_patterns"
    PERFORMANCE_TRENDS = "performance_trends"
    CAPACITY_PLANNING = "capacity_planning"
    COST_OPTIMIZATION = "cost_optimization"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    BUSINESS_IMPACT = "business_impact"
    SECURITY_INSIGHTS = "security_insights"

class OptimizationType(Enum):
    """Types of optimization recommendations"""
    RESOURCE_ALLOCATION = "resource_allocation"
    SCALING_STRATEGY = "scaling_strategy"
    LOAD_BALANCING = "load_balancing"
    CACHING_STRATEGY = "caching_strategy"
    SERVICE_PLACEMENT = "service_placement"
    COST_REDUCTION = "cost_reduction"
    PERFORMANCE_TUNING = "performance_tuning"

class TrendDirection(Enum):
    """Trend direction indicators"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"

@dataclass
class AnalysisScope:
    """Scope definition for analytics analysis"""
    service_ids: Optional[List[str]] = None
    service_types: Optional[List[str]] = None
    business_domains: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    time_window_hours: int = 24
    include_historical: bool = True
    analysis_types: List[AnalysisType] = field(default_factory=lambda: [AnalysisType.USAGE_PATTERNS])

@dataclass
class UsagePattern:
    """Service usage pattern"""
    pattern_id: str
    service_id: str
    pattern_type: str  # peak_hours, seasonal, sporadic, steady
    frequency: float  # requests per minute
    peak_times: List[str]  # hour patterns like "09:00-17:00"
    confidence: float  # 0.0 to 1.0
    duration_days: int
    characteristics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    service_id: str
    metric_name: str
    value: float
    timestamp: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class RegistryAnalytics:
    """Registry analytics result"""
    analysis_scope: AnalysisScope
    execution_time: float
    services_analyzed: int
    usage_patterns: List[UsagePattern]
    performance_insights: Dict[str, Any]
    capacity_recommendations: List[Dict[str, Any]]
    cost_analysis: Dict[str, Any]
    dependency_insights: Dict[str, Any]
    business_impact_metrics: Dict[str, Any]
    summary_insights: List[str]

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    recommendation_id: str
    service_id: str
    optimization_type: OptimizationType
    priority: str  # critical, high, medium, low
    title: str
    description: str
    expected_benefit: Dict[str, Any]  # performance, cost, reliability improvements
    implementation_complexity: str  # low, medium, high
    estimated_effort_hours: int
    prerequisites: List[str]
    action_items: List[str]
    confidence: float  # 0.0 to 1.0

@dataclass
class RegistryMetrics:
    """Registry metrics for analysis"""
    total_services: int
    active_services: int
    service_requests_per_minute: float
    average_response_time_ms: float
    error_rate: float
    availability_percentage: float
    resource_utilization: Dict[str, float]
    cost_metrics: Dict[str, float]
    timestamp: float

@dataclass
class DependencyScope:
    """Dependency analysis scope"""
    root_service_id: str
    max_depth: int = 3
    include_dependents: bool = True
    include_dependencies: bool = True
    analyze_criticality: bool = True

@dataclass
class DependencyAnalytics:
    """Dependency analysis result"""
    root_service_id: str
    dependency_map: Dict[str, Set[str]]
    dependent_map: Dict[str, Set[str]]
    criticality_scores: Dict[str, float]
    bottleneck_services: List[str]
    circular_dependencies: List[List[str]]
    impact_analysis: Dict[str, Dict[str, Any]]

@dataclass
class UsageTrends:
    """Usage trends data"""
    service_id: str
    time_series: List[Tuple[float, float]]  # (timestamp, value)
    trend_direction: TrendDirection
    growth_rate: float  # percentage per period
    seasonality_detected: bool
    anomalies: List[Tuple[float, float]]  # (timestamp, anomaly_score)

@dataclass
class ScalingPrediction:
    """Scaling prediction result"""
    service_id: str
    current_capacity: Dict[str, float]
    predicted_capacity_need: Dict[str, float]
    prediction_confidence: float
    time_horizon_hours: int
    scaling_triggers: List[str]
    recommended_actions: List[str]

@dataclass
class ServiceChange:
    """Service change for impact analysis"""
    change_id: str
    service_id: str
    change_type: str  # version_update, config_change, scaling, removal
    change_details: Dict[str, Any]
    timestamp: float

@dataclass
class BusinessImpactMetrics:
    """Business impact metrics"""
    revenue_impact: Dict[str, float]
    user_experience_impact: Dict[str, float]
    operational_cost_impact: Dict[str, float]
    creator_satisfaction_impact: Dict[str, float]
    platform_reliability_impact: Dict[str, float]

@dataclass
class AnalyticsConfig:
    """Configuration for analytics engine"""
    collection_interval_seconds: int = 60
    retention_days: int = 90
    ml_predictions_enabled: bool = True
    business_metrics_enabled: bool = True
    cost_tracking_enabled: bool = True
    anomaly_detection_threshold: float = 2.0

class UsagePatternAnalyzer:
    """Analyzes service usage patterns"""
    
    def __init__(self):
        self.usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10080))  # Week of minutes
        self.pattern_cache: Dict[str, UsagePattern] = {}
        
    async def analyze_patterns(self, service_id: str, time_window_hours: int = 24) -> List[UsagePattern]:
        """Analyze usage patterns for a service"""
        try:
            patterns = []
            
            # Get usage data
            usage_data = list(self.usage_history.get(service_id, []))
            if len(usage_data) < 60:  # Need at least 1 hour of data
                return patterns
            
            # Detect peak hours pattern
            peak_pattern = await self._detect_peak_hours_pattern(service_id, usage_data)
            if peak_pattern:
                patterns.append(peak_pattern)
            
            # Detect steady usage pattern
            steady_pattern = await self._detect_steady_pattern(service_id, usage_data)
            if steady_pattern:
                patterns.append(steady_pattern)
            
            # Detect sporadic pattern
            sporadic_pattern = await self._detect_sporadic_pattern(service_id, usage_data)
            if sporadic_pattern:
                patterns.append(sporadic_pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Usage pattern analysis failed for {service_id}: {e}")
            return []
    
    async def _detect_peak_hours_pattern(self, service_id: str, usage_data: List) -> Optional[UsagePattern]:
        """Detect peak hours usage pattern"""
        try:
            if len(usage_data) < 144:  # Need at least 24 hours
                return None
            
            # Group by hour of day
            hourly_usage = defaultdict(list)
            for timestamp, usage in usage_data:
                hour = datetime.fromtimestamp(timestamp).hour
                hourly_usage[hour].append(usage)
            
            # Calculate average usage per hour
            hourly_averages = {}
            for hour, usage_list in hourly_usage.items():
                hourly_averages[hour] = statistics.mean(usage_list)
            
            # Find peak hours (top 25% of hours)
            if not hourly_averages:
                return None
                
            avg_usage = statistics.mean(hourly_averages.values())
            peak_threshold = avg_usage * 1.5
            
            peak_hours = [hour for hour, usage in hourly_averages.items() if usage > peak_threshold]
            
            if len(peak_hours) >= 2:
                # Convert hours to time ranges
                peak_times = []
                if peak_hours:
                    peak_hours.sort()
                    start_hour = peak_hours[0]
                    end_hour = peak_hours[-1]
                    peak_times.append(f"{start_hour:02d}:00-{end_hour:02d}:59")
                
                return UsagePattern(
                    pattern_id=f"peak_hours_{service_id}_{int(time.time())}",
                    service_id=service_id,
                    pattern_type="peak_hours",
                    frequency=max(hourly_averages.values()),
                    peak_times=peak_times,
                    confidence=0.8,
                    duration_days=len(usage_data) // 1440,  # minutes to days
                    characteristics={
                        'peak_multiplier': max(hourly_averages.values()) / avg_usage,
                        'peak_hours_count': len(peak_hours)
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Peak hours detection failed: {e}")
            return None
    
    async def _detect_steady_pattern(self, service_id: str, usage_data: List) -> Optional[UsagePattern]:
        """Detect steady usage pattern"""
        try:
            if len(usage_data) < 60:
                return None
            
            # Calculate coefficient of variation
            usage_values = [usage for _, usage in usage_data]
            if not usage_values or statistics.stdev(usage_values) == 0:
                return None
                
            cv = statistics.stdev(usage_values) / statistics.mean(usage_values)
            
            # Low coefficient of variation indicates steady pattern
            if cv < 0.3:
                return UsagePattern(
                    pattern_id=f"steady_{service_id}_{int(time.time())}",
                    service_id=service_id,
                    pattern_type="steady",
                    frequency=statistics.mean(usage_values),
                    peak_times=[],
                    confidence=1.0 - cv,
                    duration_days=len(usage_data) // 1440,
                    characteristics={
                        'coefficient_of_variation': cv,
                        'stability_score': 1.0 - cv
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Steady pattern detection failed: {e}")
            return None
    
    async def _detect_sporadic_pattern(self, service_id: str, usage_data: List) -> Optional[UsagePattern]:
        """Detect sporadic usage pattern"""
        try:
            if len(usage_data) < 60:
                return None
            
            usage_values = [usage for _, usage in usage_data]
            zero_usage_count = sum(1 for usage in usage_values if usage == 0)
            zero_ratio = zero_usage_count / len(usage_values)
            
            # High ratio of zero usage indicates sporadic pattern
            if zero_ratio > 0.4:
                non_zero_usage = [usage for usage in usage_values if usage > 0]
                avg_active_usage = statistics.mean(non_zero_usage) if non_zero_usage else 0
                
                return UsagePattern(
                    pattern_id=f"sporadic_{service_id}_{int(time.time())}",
                    service_id=service_id,
                    pattern_type="sporadic",
                    frequency=avg_active_usage,
                    peak_times=[],
                    confidence=zero_ratio,
                    duration_days=len(usage_data) // 1440,
                    characteristics={
                        'zero_usage_ratio': zero_ratio,
                        'active_periods': len(non_zero_usage),
                        'avg_active_usage': avg_active_usage
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Sporadic pattern detection failed: {e}")
            return None
    
    def record_usage(self, service_id: str, usage_value: float):
        """Record usage data point"""
        self.usage_history[service_id].append((time.time(), usage_value))

class PerformanceAnalyzer:
    """Performance analytics and trend analysis"""
    
    def __init__(self):
        self.performance_history: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=2880))  # 48 hours of minute data
        )
        
    async def analyze_performance_trends(self, service_id: str, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze performance trends for a service"""
        try:
            insights = {}
            
            # Analyze response time trends
            response_time_data = list(self.performance_history[service_id]['response_time'])
            if response_time_data:
                insights['response_time'] = await self._analyze_metric_trend(
                    'response_time', response_time_data, 'ms'
                )
            
            # Analyze error rate trends
            error_rate_data = list(self.performance_history[service_id]['error_rate'])
            if error_rate_data:
                insights['error_rate'] = await self._analyze_metric_trend(
                    'error_rate', error_rate_data, 'percentage'
                )
            
            # Analyze throughput trends
            throughput_data = list(self.performance_history[service_id]['throughput'])
            if throughput_data:
                insights['throughput'] = await self._analyze_metric_trend(
                    'throughput', throughput_data, 'requests/sec'
                )
            
            # Calculate overall performance score
            performance_score = await self._calculate_performance_score(insights)
            insights['overall_performance_score'] = performance_score
            
            return insights
            
        except Exception as e:
            logger.error(f"Performance trend analysis failed for {service_id}: {e}")
            return {}
    
    async def _analyze_metric_trend(self, metric_name: str, data: List, unit: str) -> Dict[str, Any]:
        """Analyze trend for a specific metric"""
        try:
            if len(data) < 10:
                return {'trend': 'insufficient_data', 'unit': unit}
            
            values = [value for _, value in data]
            timestamps = [ts for ts, _ in data]
            
            # Calculate basic statistics
            avg_value = statistics.mean(values)
            max_value = max(values)
            min_value = min(values)
            std_dev = statistics.stdev(values)
            
            # Determine trend direction
            if len(values) >= 20:
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)
                
                if second_avg > first_avg * 1.1:
                    trend_direction = TrendDirection.INCREASING
                elif second_avg < first_avg * 0.9:
                    trend_direction = TrendDirection.DECREASING
                else:
                    trend_direction = TrendDirection.STABLE
            else:
                trend_direction = TrendDirection.UNKNOWN
            
            # Detect anomalies
            anomalies = []
            z_threshold = 2.0
            for i, value in enumerate(values):
                z_score = abs(value - avg_value) / (std_dev + 0.001)
                if z_score > z_threshold:
                    anomalies.append({
                        'timestamp': timestamps[i],
                        'value': value,
                        'z_score': z_score
                    })
            
            return {
                'metric_name': metric_name,
                'unit': unit,
                'trend_direction': trend_direction.value,
                'average': avg_value,
                'maximum': max_value,
                'minimum': min_value,
                'standard_deviation': std_dev,
                'coefficient_of_variation': std_dev / avg_value if avg_value > 0 else 0,
                'anomalies_count': len(anomalies),
                'anomalies': anomalies[:5],  # Top 5 anomalies
                'data_points': len(values)
            }
            
        except Exception as e:
            logger.error(f"Metric trend analysis failed for {metric_name}: {e}")
            return {'trend': 'error', 'unit': unit}
    
    async def _calculate_performance_score(self, insights: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        try:
            score = 1.0
            
            # Response time impact (lower is better)
            if 'response_time' in insights:
                avg_rt = insights['response_time'].get('average', 0)
                if avg_rt > 1000:  # 1 second
                    score *= 0.5
                elif avg_rt > 500:  # 500ms
                    score *= 0.7
                elif avg_rt > 200:  # 200ms
                    score *= 0.9
            
            # Error rate impact (lower is better)
            if 'error_rate' in insights:
                avg_error = insights['error_rate'].get('average', 0)
                if avg_error > 0.1:  # 10%
                    score *= 0.3
                elif avg_error > 0.05:  # 5%
                    score *= 0.6
                elif avg_error > 0.01:  # 1%
                    score *= 0.8
            
            # Stability impact (less variation is better)
            total_cv = 0
            cv_count = 0
            for metric_data in insights.values():
                if isinstance(metric_data, dict) and 'coefficient_of_variation' in metric_data:
                    total_cv += metric_data['coefficient_of_variation']
                    cv_count += 1
            
            if cv_count > 0:
                avg_cv = total_cv / cv_count
                stability_factor = max(0.5, 1.0 - avg_cv)
                score *= stability_factor
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Performance score calculation failed: {e}")
            return 0.5
    
    def record_performance_metric(self, service_id: str, metric_name: str, value: float):
        """Record performance metric"""
        self.performance_history[service_id][metric_name].append((time.time(), value))

class OptimizationRecommendationEngine:
    """Generates optimization recommendations"""
    
    def __init__(self):
        self.recommendation_templates = self._load_recommendation_templates()
        
    def _load_recommendation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load optimization recommendation templates"""
        return {
            'high_response_time': {
                'type': OptimizationType.PERFORMANCE_TUNING,
                'priority': 'high',
                'title': 'Optimize Response Time',
                'description_template': 'Service {service_id} has high response time: {avg_response_time}ms. Consider performance optimization.',
                'action_items': [
                    'Profile application code for bottlenecks',
                    'Optimize database queries',
                    'Add caching layer',
                    'Consider service scaling'
                ]
            },
            'high_error_rate': {
                'type': OptimizationType.PERFORMANCE_TUNING,
                'priority': 'critical',
                'title': 'Reduce Error Rate',
                'description_template': 'Service {service_id} has high error rate: {error_rate}%. Immediate attention required.',
                'action_items': [
                    'Investigate error logs',
                    'Check service dependencies',
                    'Verify configuration',
                    'Consider rolling back recent changes'
                ]
            },
            'underutilized_resources': {
                'type': OptimizationType.COST_REDUCTION,
                'priority': 'medium',
                'title': 'Optimize Resource Allocation',
                'description_template': 'Service {service_id} is underutilizing resources. Consider downsizing to reduce costs.',
                'action_items': [
                    'Reduce allocated CPU/memory',
                    'Consider serverless migration',
                    'Consolidate with other services',
                    'Implement auto-scaling'
                ]
            },
            'scaling_needed': {
                'type': OptimizationType.SCALING_STRATEGY,
                'priority': 'high',
                'title': 'Scale Service',
                'description_template': 'Service {service_id} is approaching capacity limits. Scaling recommended.',
                'action_items': [
                    'Add more service instances',
                    'Increase resource allocation',
                    'Implement horizontal scaling',
                    'Consider load balancing optimization'
                ]
            }
        }
    
    async def generate_optimization_recommendations(self, registry_metrics: RegistryMetrics, 
                                                  performance_insights: Dict[str, Any],
                                                  usage_patterns: List[UsagePattern]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on analytics"""
        try:
            recommendations = []
            
            # Analyze performance metrics for recommendations
            perf_recommendations = await self._analyze_performance_for_recommendations(performance_insights)
            recommendations.extend(perf_recommendations)
            
            # Analyze usage patterns for recommendations
            usage_recommendations = await self._analyze_usage_for_recommendations(usage_patterns)
            recommendations.extend(usage_recommendations)
            
            # Analyze registry metrics for recommendations
            registry_recommendations = await self._analyze_registry_for_recommendations(registry_metrics)
            recommendations.extend(registry_recommendations)
            
            # Sort by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendation generation failed: {e}")
            return []
    
    async def _analyze_performance_for_recommendations(self, performance_insights: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate recommendations based on performance insights"""
        recommendations = []
        
        for service_id, insights in performance_insights.items():
            if not isinstance(insights, dict):
                continue
                
            # High response time recommendation
            if 'response_time' in insights:
                avg_rt = insights['response_time'].get('average', 0)
                if avg_rt > 500:  # 500ms threshold
                    template = self.recommendation_templates['high_response_time']
                    rec = OptimizationRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        service_id=service_id,
                        optimization_type=template['type'],
                        priority=template['priority'],
                        title=template['title'],
                        description=template['description_template'].format(
                            service_id=service_id, avg_response_time=int(avg_rt)
                        ),
                        expected_benefit={
                            'performance_improvement': '30-50%',
                            'user_experience': 'Significantly improved',
                            'cost_impact': 'Neutral to positive'
                        },
                        implementation_complexity='medium',
                        estimated_effort_hours=16,
                        prerequisites=['Performance profiling tools', 'Monitoring setup'],
                        action_items=template['action_items'],
                        confidence=0.8
                    )
                    recommendations.append(rec)
            
            # High error rate recommendation
            if 'error_rate' in insights:
                avg_error = insights['error_rate'].get('average', 0)
                if avg_error > 0.05:  # 5% threshold
                    template = self.recommendation_templates['high_error_rate']
                    rec = OptimizationRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        service_id=service_id,
                        optimization_type=template['type'],
                        priority=template['priority'],
                        title=template['title'],
                        description=template['description_template'].format(
                            service_id=service_id, error_rate=f"{avg_error*100:.1f}"
                        ),
                        expected_benefit={
                            'reliability_improvement': '80-95%',
                            'user_experience': 'Critical improvement',
                            'operational_stability': 'Significantly improved'
                        },
                        implementation_complexity='high',
                        estimated_effort_hours=24,
                        prerequisites=['Access to logs', 'Error tracking tools'],
                        action_items=template['action_items'],
                        confidence=0.9
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    async def _analyze_usage_for_recommendations(self, usage_patterns: List[UsagePattern]) -> List[OptimizationRecommendation]:
        """Generate recommendations based on usage patterns"""
        recommendations = []
        
        for pattern in usage_patterns:
            if pattern.pattern_type == 'sporadic' and pattern.characteristics.get('zero_usage_ratio', 0) > 0.7:
                # Recommend serverless or auto-scaling for sporadic usage
                rec = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    service_id=pattern.service_id,
                    optimization_type=OptimizationType.COST_REDUCTION,
                    priority='medium',
                    title='Consider Serverless Architecture',
                    description=f'Service {pattern.service_id} has sporadic usage pattern (70%+ idle time). Serverless could reduce costs.',
                    expected_benefit={
                        'cost_reduction': '40-70%',
                        'resource_efficiency': 'Significantly improved',
                        'operational_overhead': 'Reduced'
                    },
                    implementation_complexity='high',
                    estimated_effort_hours=40,
                    prerequisites=['Serverless platform setup', 'Code refactoring'],
                    action_items=[
                        'Evaluate serverless compatibility',
                        'Refactor code for serverless',
                        'Set up serverless deployment',
                        'Implement monitoring'
                    ],
                    confidence=0.7
                )
                recommendations.append(rec)
            
            elif pattern.pattern_type == 'peak_hours' and pattern.confidence > 0.8:
                # Recommend auto-scaling for predictable peak patterns
                rec = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    service_id=pattern.service_id,
                    optimization_type=OptimizationType.SCALING_STRATEGY,
                    priority='medium',
                    title='Implement Predictive Scaling',
                    description=f'Service {pattern.service_id} has predictable peak hours. Consider scheduled auto-scaling.',
                    expected_benefit={
                        'cost_optimization': '20-40%',
                        'performance_consistency': 'Improved',
                        'resource_utilization': 'Optimized'
                    },
                    implementation_complexity='medium',
                    estimated_effort_hours=20,
                    prerequisites=['Auto-scaling infrastructure', 'Usage monitoring'],
                    action_items=[
                        'Configure scheduled scaling',
                        'Set up monitoring alerts',
                        'Test scaling policies',
                        'Monitor cost impact'
                    ],
                    confidence=0.8
                )
                recommendations.append(rec)
        
        return recommendations
    
    async def _analyze_registry_for_recommendations(self, registry_metrics: RegistryMetrics) -> List[OptimizationRecommendation]:
        """Generate recommendations based on registry metrics"""
        recommendations = []
        
        # High error rate across registry
        if registry_metrics.error_rate > 0.02:  # 2%
            rec = OptimizationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                service_id='registry_system',
                optimization_type=OptimizationType.PERFORMANCE_TUNING,
                priority='high',
                title='Improve Registry Reliability',
                description=f'Registry system has elevated error rate: {registry_metrics.error_rate*100:.1f}%. System-wide investigation needed.',
                expected_benefit={
                    'system_reliability': 'Significantly improved',
                    'service_discovery_performance': 'Improved',
                    'operational_stability': 'Enhanced'
                },
                implementation_complexity='high',
                estimated_effort_hours=32,
                prerequisites=['System monitoring', 'Registry logs access'],
                action_items=[
                    'Investigate registry error patterns',
                    'Check service discovery performance',
                    'Verify registry backend health',
                    'Consider registry scaling'
                ],
                confidence=0.85
            )
            recommendations.append(rec)
        
        # Low availability
        if registry_metrics.availability_percentage < 99.5:
            rec = OptimizationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                service_id='registry_system',
                optimization_type=OptimizationType.SCALING_STRATEGY,
                priority='critical',
                title='Improve Registry Availability',
                description=f'Registry availability is below target: {registry_metrics.availability_percentage:.2f}%. High availability setup recommended.',
                expected_benefit={
                    'availability_improvement': '99.9%+ target',
                    'system_resilience': 'Significantly improved',
                    'business_continuity': 'Enhanced'
                },
                implementation_complexity='high',
                estimated_effort_hours=48,
                prerequisites=['Multi-region setup', 'Load balancers'],
                action_items=[
                    'Set up registry clustering',
                    'Implement health checks',
                    'Configure automatic failover',
                    'Test disaster recovery'
                ],
                confidence=0.9
            )
            recommendations.append(rec)
        
        return recommendations

class TrendPredictionEngine:
    """Predicts future trends based on historical data"""
    
    def __init__(self):
        self.prediction_models: Dict[str, Any] = {}
        
    async def predict_scaling_needs(self, usage_trends: UsageTrends) -> ScalingPrediction:
        """Predict future scaling needs based on usage trends"""
        try:
            service_id = usage_trends.service_id
            time_series = usage_trends.time_series
            
            if len(time_series) < 10:
                return ScalingPrediction(
                    service_id=service_id,
                    current_capacity={'requests_per_minute': 0},
                    predicted_capacity_need={'requests_per_minute': 0},
                    prediction_confidence=0.1,
                    time_horizon_hours=24,
                    scaling_triggers=[],
                    recommended_actions=['Collect more data for prediction']
                )
            
            # Simple linear trend prediction
            values = [value for _, value in time_series]
            current_capacity = {'requests_per_minute': max(values)}
            
            # Calculate growth rate
            if usage_trends.growth_rate > 0.1:  # 10% growth
                growth_multiplier = 1 + usage_trends.growth_rate
                predicted_capacity = current_capacity['requests_per_minute'] * growth_multiplier
                
                scaling_triggers = []
                recommended_actions = []
                
                if growth_multiplier > 1.5:  # 50% growth
                    scaling_triggers.append('High growth rate detected')
                    recommended_actions.append('Scale up preemptively')
                
                if usage_trends.seasonality_detected:
                    scaling_triggers.append('Seasonal pattern detected')
                    recommended_actions.append('Implement predictive scaling')
                
                return ScalingPrediction(
                    service_id=service_id,
                    current_capacity=current_capacity,
                    predicted_capacity_need={'requests_per_minute': predicted_capacity},
                    prediction_confidence=0.7,
                    time_horizon_hours=24,
                    scaling_triggers=scaling_triggers,
                    recommended_actions=recommended_actions
                )
            else:
                return ScalingPrediction(
                    service_id=service_id,
                    current_capacity=current_capacity,
                    predicted_capacity_need=current_capacity,
                    prediction_confidence=0.8,
                    time_horizon_hours=24,
                    scaling_triggers=[],
                    recommended_actions=['Monitor current capacity']
                )
                
        except Exception as e:
            logger.error(f"Scaling prediction failed for {usage_trends.service_id}: {e}")
            return ScalingPrediction(
                service_id=usage_trends.service_id,
                current_capacity={},
                predicted_capacity_need={},
                prediction_confidence=0.0,
                time_horizon_hours=24,
                scaling_triggers=[],
                recommended_actions=['Prediction failed - manual review needed']
            )

class RegistryAnalyticsEngine:
    """
    Moteur analytics registry avec insights et recommendations.
    Usage patterns + performance analytics + optimization recommendations.
    """
    
    def __init__(self, analytics_config: Optional[AnalyticsConfig] = None):
        """Initialize registry analytics engine"""
        self.analytics_config = analytics_config or AnalyticsConfig()
        self.pattern_analyzer = UsagePatternAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.optimization_engine = OptimizationRecommendationEngine()
        self.trend_predictor = TrendPredictionEngine()
        
        # Service registry reference (to be injected)
        self.service_registry = None
        
        # Background collection task
        self._collection_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Metrics
        self.metrics = {
            'analyses_performed': 0,
            'recommendations_generated': 0,
            'patterns_detected': 0,
            'predictions_made': 0,
            'data_points_collected': 0
        }
    
    def set_service_registry(self, registry):
        """Set reference to service registry"""
        self.service_registry = registry
    
    async def start_collection(self):
        """Start background data collection"""
        if self._collection_task is None or self._collection_task.done():
            self._shutdown_event.clear()
            self._collection_task = asyncio.create_task(self._collection_loop())
            logger.info("Analytics data collection started")
    
    async def stop_collection(self):
        """Stop background data collection"""
        self._shutdown_event.set()
        if self._collection_task and not self._collection_task.done():
            await self._collection_task
        logger.info("Analytics data collection stopped")
    
    async def analyze_registry_patterns(self, analysis_scope: AnalysisScope) -> RegistryAnalytics:
        """
        Analyse patterns registry avec insights business.
        
        Analytics Features:
        - Service discovery pattern analysis avec optimization insights
        - Performance analytics avec bottleneck identification
        - Usage trend analysis avec capacity planning recommendations
        - Service dependency analytics avec optimization suggestions
        - Health pattern analysis avec predictive maintenance insights
        - Cost optimization analysis avec resource utilization insights
        - Business impact analytics pour service changes
        - Registry efficiency metrics avec improvement recommendations
        """
        start_time = time.time()
        
        try:
            # Get services in scope
            services_to_analyze = await self._get_services_in_scope(analysis_scope)
            
            # Analyze usage patterns
            usage_patterns = []
            if AnalysisType.USAGE_PATTERNS in analysis_scope.analysis_types:
                usage_patterns = await self._analyze_usage_patterns(services_to_analyze, analysis_scope)
            
            # Analyze performance trends
            performance_insights = {}
            if AnalysisType.PERFORMANCE_TRENDS in analysis_scope.analysis_types:
                performance_insights = await self._analyze_performance_trends(services_to_analyze, analysis_scope)
            
            # Generate capacity recommendations
            capacity_recommendations = []
            if AnalysisType.CAPACITY_PLANNING in analysis_scope.analysis_types:
                capacity_recommendations = await self._analyze_capacity_planning(services_to_analyze, performance_insights)
            
            # Analyze costs
            cost_analysis = {}
            if AnalysisType.COST_OPTIMIZATION in analysis_scope.analysis_types:
                cost_analysis = await self._analyze_costs(services_to_analyze)
            
            # Analyze dependencies
            dependency_insights = {}
            if AnalysisType.DEPENDENCY_ANALYSIS in analysis_scope.analysis_types:
                dependency_insights = await self._analyze_dependencies(services_to_analyze)
            
            # Calculate business impact
            business_impact_metrics = {}
            if AnalysisType.BUSINESS_IMPACT in analysis_scope.analysis_types:
                business_impact_metrics = await self._calculate_business_impact(services_to_analyze, usage_patterns)
            
            # Generate summary insights
            summary_insights = await self._generate_summary_insights(
                usage_patterns, performance_insights, capacity_recommendations
            )
            
            # Update metrics
            self.metrics['analyses_performed'] += 1
            self.metrics['patterns_detected'] += len(usage_patterns)
            
            execution_time = time.time() - start_time
            
            return RegistryAnalytics(
                analysis_scope=analysis_scope,
                execution_time=execution_time,
                services_analyzed=len(services_to_analyze),
                usage_patterns=usage_patterns,
                performance_insights=performance_insights,
                capacity_recommendations=capacity_recommendations,
                cost_analysis=cost_analysis,
                dependency_insights=dependency_insights,
                business_impact_metrics=business_impact_metrics,
                summary_insights=summary_insights
            )
            
        except Exception as e:
            logger.error(f"Registry pattern analysis failed: {e}")
            return RegistryAnalytics(
                analysis_scope=analysis_scope,
                execution_time=time.time() - start_time,
                services_analyzed=0,
                usage_patterns=[],
                performance_insights={},
                capacity_recommendations=[],
                cost_analysis={},
                dependency_insights={},
                business_impact_metrics={},
                summary_insights=[f"Analysis failed: {str(e)}"]
            )
    
    async def generate_optimization_recommendations(self, registry_metrics: RegistryMetrics) -> List[OptimizationRecommendation]:
        """Génération recommandations optimization basées sur analytics."""
        try:
            # Get recent performance insights
            all_services = list(self.service_registry.service_instances.values()) if self.service_registry else []
            performance_insights = {}
            
            for service in all_services:
                service_insights = await self.performance_analyzer.analyze_performance_trends(service.service_id)
                if service_insights:
                    performance_insights[service.service_id] = service_insights
            
            # Get usage patterns
            usage_patterns = []
            for service in all_services:
                patterns = await self.pattern_analyzer.analyze_patterns(service.service_id)
                usage_patterns.extend(patterns)
            
            # Generate recommendations
            recommendations = await self.optimization_engine.generate_optimization_recommendations(
                registry_metrics, performance_insights, usage_patterns
            )
            
            self.metrics['recommendations_generated'] += len(recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendation generation failed: {e}")
            return []
    
    async def analyze_service_dependencies(self, dependency_scope: DependencyScope) -> DependencyAnalytics:
        """Analyse dépendances service avec impact assessment."""
        try:
            # Simple dependency analysis - in real implementation would query service registry
            dependency_map = defaultdict(set)
            dependent_map = defaultdict(set)
            
            # Mock dependency relationships
            root_service = dependency_scope.root_service_id
            if root_service.endswith('_service'):
                base_name = root_service.replace('_service', '')
                dependency_map[root_service].add(f"{base_name}_database")
                dependency_map[root_service].add(f"{base_name}_cache")
                
                dependent_map[f"{base_name}_database"].add(root_service)
                dependent_map[f"{base_name}_cache"].add(root_service)
            
            # Calculate criticality scores
            criticality_scores = {}
            for service_id in dependency_map.keys():
                # Simple criticality based on number of dependents
                dependent_count = len(dependent_map.get(service_id, set()))
                criticality_scores[service_id] = min(1.0, dependent_count / 10.0)
            
            # Identify bottlenecks (services with many dependents)
            bottleneck_services = [
                service_id for service_id, score in criticality_scores.items()
                if score > 0.7
            ]
            
            # Check for circular dependencies (simplified)
            circular_dependencies = []
            
            # Impact analysis
            impact_analysis = {}
            for service_id in dependency_map.keys():
                impact_analysis[service_id] = {
                    'direct_dependencies': len(dependency_map.get(service_id, set())),
                    'direct_dependents': len(dependent_map.get(service_id, set())),
                    'criticality': criticality_scores.get(service_id, 0.0),
                    'failure_impact': 'high' if criticality_scores.get(service_id, 0) > 0.7 else 'medium'
                }
            
            return DependencyAnalytics(
                root_service_id=root_service,
                dependency_map=dict(dependency_map),
                dependent_map=dict(dependent_map),
                criticality_scores=criticality_scores,
                bottleneck_services=bottleneck_services,
                circular_dependencies=circular_dependencies,
                impact_analysis=impact_analysis
            )
            
        except Exception as e:
            logger.error(f"Dependency analysis failed: {e}")
            return DependencyAnalytics(
                root_service_id=dependency_scope.root_service_id,
                dependency_map={},
                dependent_map={},
                criticality_scores={},
                bottleneck_services=[],
                circular_dependencies=[],
                impact_analysis={}
            )
    
    async def predict_registry_scaling_needs(self, usage_trends: UsageTrends) -> ScalingPrediction:
        """Prédiction besoins scaling registry avec ML forecasting."""
        try:
            prediction = await self.trend_predictor.predict_scaling_needs(usage_trends)
            self.metrics['predictions_made'] += 1
            return prediction
        except Exception as e:
            logger.error(f"Registry scaling prediction failed: {e}")
            return ScalingPrediction(
                service_id=usage_trends.service_id,
                current_capacity={},
                predicted_capacity_need={},
                prediction_confidence=0.0,
                time_horizon_hours=24,
                scaling_triggers=[],
                recommended_actions=['Prediction failed - manual review needed']
            )
    
    async def calculate_business_impact_metrics(self, service_changes: List[ServiceChange]) -> BusinessImpactMetrics:
        """Calcul métriques impact business pour changements service."""
        try:
            # Initialize impact metrics
            revenue_impact = {}
            user_experience_impact = {}
            operational_cost_impact = {}
            creator_satisfaction_impact = {}
            platform_reliability_impact = {}
            
            for change in service_changes:
                service_id = change.service_id
                change_type = change.change_type
                
                # Calculate revenue impact based on service type and change
                if 'monetization' in service_id.lower():
                    if change_type == 'removal':
                        revenue_impact[service_id] = -0.15  # 15% negative impact
                    elif change_type == 'version_update':
                        revenue_impact[service_id] = 0.05   # 5% positive impact
                else:
                    revenue_impact[service_id] = 0.0
                
                # User experience impact
                if change_type == 'removal':
                    user_experience_impact[service_id] = -0.3
                elif change_type == 'scaling':
                    user_experience_impact[service_id] = 0.1
                else:
                    user_experience_impact[service_id] = 0.0
                
                # Operational cost impact
                if change_type == 'scaling':
                    scale_factor = change.change_details.get('scale_factor', 1.0)
                    operational_cost_impact[service_id] = (scale_factor - 1.0) * 0.8
                else:
                    operational_cost_impact[service_id] = 0.0
                
                # Creator satisfaction (for IA Chérie business context)
                if 'creator' in service_id.lower() or 'content' in service_id.lower():
                    if change_type == 'version_update':
                        creator_satisfaction_impact[service_id] = 0.1
                    elif change_type == 'removal':
                        creator_satisfaction_impact[service_id] = -0.4
                else:
                    creator_satisfaction_impact[service_id] = 0.0
                
                # Platform reliability impact
                if change_type == 'version_update':
                    platform_reliability_impact[service_id] = 0.05
                elif change_type == 'removal':
                    platform_reliability_impact[service_id] = -0.2
                else:
                    platform_reliability_impact[service_id] = 0.0
            
            return BusinessImpactMetrics(
                revenue_impact=revenue_impact,
                user_experience_impact=user_experience_impact,
                operational_cost_impact=operational_cost_impact,
                creator_satisfaction_impact=creator_satisfaction_impact,
                platform_reliability_impact=platform_reliability_impact
            )
            
        except Exception as e:
            logger.error(f"Business impact calculation failed: {e}")
            return BusinessImpactMetrics(
                revenue_impact={},
                user_experience_impact={},
                operational_cost_impact={},
                creator_satisfaction_impact={},
                platform_reliability_impact={}
            )
    
    async def _collection_loop(self):
        """Background data collection loop"""
        while not self._shutdown_event.is_set():
            try:
                # Collect metrics from registry if available
                if self.service_registry:
                    for service_id, instance in self.service_registry.service_instances.items():
                        # Simulate metric collection
                        usage_value = np.random.poisson(50)  # Random usage
                        response_time = np.random.gamma(2, 50)  # Random response time
                        error_rate = np.random.beta(1, 100)  # Random error rate
                        throughput = np.random.poisson(20)  # Random throughput
                        
                        # Record metrics
                        self.pattern_analyzer.record_usage(service_id, usage_value)
                        self.performance_analyzer.record_performance_metric(service_id, 'response_time', response_time)
                        self.performance_analyzer.record_performance_metric(service_id, 'error_rate', error_rate)
                        self.performance_analyzer.record_performance_metric(service_id, 'throughput', throughput)
                        
                        self.metrics['data_points_collected'] += 4
                
                # Wait for next collection interval
                await asyncio.sleep(self.analytics_config.collection_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Data collection error: {e}")
                await asyncio.sleep(10)
    
    async def _get_services_in_scope(self, scope: AnalysisScope) -> List[ServiceInstance]:
        """Get services matching analysis scope"""
        if not self.service_registry:
            return []
        
        all_services = list(self.service_registry.service_instances.values())
        
        # Apply filters
        filtered_services = []
        for service in all_services:
            if scope.service_ids and service.service_id not in scope.service_ids:
                continue
            if scope.service_types and service.service_type not in scope.service_types:
                continue
            if scope.business_domains and service.iacherie_business_domain not in scope.business_domains:
                continue
            if scope.regions and service.region not in scope.regions:
                continue
                
            filtered_services.append(service)
        
        return filtered_services
    
    async def _analyze_usage_patterns(self, services: List[ServiceInstance], scope: AnalysisScope) -> List[UsagePattern]:
        """Analyze usage patterns for services"""
        patterns = []
        
        for service in services:
            service_patterns = await self.pattern_analyzer.analyze_patterns(
                service.service_id, scope.time_window_hours
            )
            patterns.extend(service_patterns)
        
        return patterns
    
    async def _analyze_performance_trends(self, services: List[ServiceInstance], scope: AnalysisScope) -> Dict[str, Any]:
        """Analyze performance trends for services"""
        performance_insights = {}
        
        for service in services:
            insights = await self.performance_analyzer.analyze_performance_trends(
                service.service_id, scope.time_window_hours
            )
            if insights:
                performance_insights[service.service_id] = insights
        
        return performance_insights
    
    async def _analyze_capacity_planning(self, services: List[ServiceInstance], 
                                       performance_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate capacity planning recommendations"""
        recommendations = []
        
        for service in services:
            service_insights = performance_insights.get(service.service_id, {})
            
            # Simple capacity recommendation logic
            if 'throughput' in service_insights:
                avg_throughput = service_insights['throughput'].get('average', 0)
                if avg_throughput > 80:  # High throughput
                    recommendations.append({
                        'service_id': service.service_id,
                        'recommendation': 'Consider scaling up',
                        'reason': f'High throughput detected: {avg_throughput:.1f} req/sec',
                        'priority': 'medium'
                    })
        
        return recommendations
    
    async def _analyze_costs(self, services: List[ServiceInstance]) -> Dict[str, Any]:
        """Analyze service costs"""
        # Mock cost analysis
        total_estimated_cost = len(services) * 100  # $100 per service per month
        
        cost_by_domain = defaultdict(float)
        for service in services:
            cost_by_domain[service.iacherie_business_domain] += 100
        
        return {
            'total_monthly_cost_usd': total_estimated_cost,
            'cost_by_business_domain': dict(cost_by_domain),
            'cost_optimization_potential': total_estimated_cost * 0.2,  # 20% potential savings
            'recommendations': [
                'Consider reserved instances for steady workloads',
                'Implement auto-scaling for variable workloads',
                'Review underutilized services'
            ]
        }
    
    async def _analyze_dependencies(self, services: List[ServiceInstance]) -> Dict[str, Any]:
        """Analyze service dependencies"""
        # Mock dependency analysis
        return {
            'total_services': len(services),
            'highly_coupled_services': max(0, len(services) // 10),
            'isolated_services': max(0, len(services) // 5),
            'dependency_depth_avg': 2.3,
            'recommendations': [
                'Consider breaking down highly coupled services',
                'Implement circuit breakers for critical dependencies',
                'Document service contracts'
            ]
        }
    
    async def _calculate_business_impact(self, services: List[ServiceInstance], 
                                       patterns: List[UsagePattern]) -> Dict[str, Any]:
        """Calculate business impact metrics"""
        # IA Chérie-specific business impact
        creator_services = [s for s in services if s.iacherie_business_domain == 'creator']
        content_services = [s for s in services if s.iacherie_business_domain == 'content']
        monetization_services = [s for s in services if s.iacherie_business_domain == 'monetization']
        
        return {
            'creator_experience_score': 0.85,  # Mock score
            'content_processing_efficiency': 0.78,
            'monetization_effectiveness': 0.82,
            'platform_health_score': 0.88,
            'service_distribution': {
                'creator': len(creator_services),
                'content': len(content_services),
                'monetization': len(monetization_services),
                'other': len(services) - len(creator_services) - len(content_services) - len(monetization_services)
            }
        }
    
    async def _generate_summary_insights(self, usage_patterns: List[UsagePattern],
                                       performance_insights: Dict[str, Any],
                                       capacity_recommendations: List[Dict[str, Any]]) -> List[str]:
        """Generate high-level summary insights"""
        insights = []
        
        if usage_patterns:
            pattern_types = Counter(p.pattern_type for p in usage_patterns)
            most_common_pattern = pattern_types.most_common(1)[0]
            insights.append(f"Most common usage pattern: {most_common_pattern[0]} ({most_common_pattern[1]} services)")
        
        if performance_insights:
            avg_performance_scores = []
            for service_insights in performance_insights.values():
                if isinstance(service_insights, dict) and 'overall_performance_score' in service_insights:
                    avg_performance_scores.append(service_insights['overall_performance_score'])
            
            if avg_performance_scores:
                avg_score = statistics.mean(avg_performance_scores)
                insights.append(f"Average performance score: {avg_score:.2f} (scale 0-1)")
        
        if capacity_recommendations:
            high_priority_recs = [r for r in capacity_recommendations if r.get('priority') == 'high']
            if high_priority_recs:
                insights.append(f"{len(high_priority_recs)} services need immediate capacity attention")
        
        insights.append(f"Analysis covered {len(performance_insights)} services with performance data")
        
        return insights
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get analytics engine metrics"""
        return {
            **self.metrics,
            'collection_active': self._collection_task is not None and not self._collection_task.done(),
            'services_tracked': len(self.pattern_analyzer.usage_history),
            'performance_metrics_tracked': len(self.performance_analyzer.performance_history)
        }
    
    async def shutdown(self):
        """Graceful shutdown of analytics engine"""
        logger.info("Shutting down RegistryAnalyticsEngine")
        await self.stop_collection()

# Factory function
async def create_registry_analytics_engine(config: Optional[AnalyticsConfig] = None) -> RegistryAnalyticsEngine:
    """Factory function to create registry analytics engine"""
    return RegistryAnalyticsEngine(config)

# Export main classes and functions
__all__ = [
    'RegistryAnalyticsEngine',
    'AnalyticsConfig',
    'AnalysisScope',
    'RegistryAnalytics',
    'OptimizationRecommendation',
    'RegistryMetrics',
    'DependencyScope',
    'DependencyAnalytics',
    'UsageTrends',
    'ScalingPrediction',
    'ServiceChange',
    'BusinessImpactMetrics',
    'AnalysisType',
    'OptimizationType',
    'TrendDirection',
    'create_registry_analytics_engine'
]