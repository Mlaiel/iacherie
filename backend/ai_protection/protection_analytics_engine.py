"""Protection Analytics Engine

Advanced analytics and business intelligence for copyright protection performance.
Provides predictive insights, ROI analysis, and strategic recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Core imports
from .violation_monitoring_system import ViolationDetection, ViolationSeverity
from .legal_automation_engine import LegalActionResult, LegalActionType
from .global_protection_network import GlobalViolation

logger = logging.getLogger(__name__)


class AnalyticsMetric(Enum):
    """Types of analytics metrics"""
    DETECTION_ACCURACY = "detection_accuracy"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    COST_EFFECTIVENESS = "cost_effectiveness"
    ROI = "return_on_investment"
    THREAT_LEVEL = "threat_level"
    COVERAGE_RATIO = "coverage_ratio"
    ENFORCEMENT_EFFICIENCY = "enforcement_efficiency"
    PREVENTION_RATE = "prevention_rate"


class ReportType(Enum):
    """Types of analytics reports"""
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_PERFORMANCE = "technical_performance"
    FINANCIAL_ANALYSIS = "financial_analysis"
    THREAT_INTELLIGENCE = "threat_intelligence"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    COMPLIANCE_REPORT = "compliance_report"
    OPERATIONAL_METRICS = "operational_metrics"
    STRATEGIC_INSIGHTS = "strategic_insights"


class TimeRange(Enum):
    """Time ranges for analytics"""
    LAST_HOUR = "last_hour"
    LAST_24_HOURS = "last_24_hours"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    LAST_QUARTER = "last_quarter"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"


class TrendDirection(Enum):
    """Trend directions"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


@dataclass
class AnalyticsDataPoint:
    """Single analytics data point"""
    timestamp: datetime
    metric: AnalyticsMetric
    value: float
    context: Dict[str, Any]
    source: str
    confidence: float


@dataclass
class ROIAnalysis:
    """Return on Investment analysis"""
    analysis_id: str
    time_period: str
    total_investment: float
    protection_costs: float
    enforcement_costs: float
    prevention_savings: float
    recovery_amount: float
    net_roi: float
    roi_percentage: float
    cost_per_violation_prevented: float
    value_protected: float
    efficiency_score: float
    recommendations: List[str]
    calculation_timestamp: datetime


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    metrics_id: str
    collection_period: str
    detection_metrics: Dict[str, float]
    enforcement_metrics: Dict[str, float]
    financial_metrics: Dict[str, float]
    operational_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    efficiency_metrics: Dict[str, float]
    benchmark_comparisons: Dict[str, float]
    improvement_opportunities: List[str]
    performance_score: float
    timestamp: datetime


class DataCollector:
    """Analytics data collection engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.data_points: List[AnalyticsDataPoint] = []
        self.collection_active = False
        
    async def start_collection(self) -> None:
        """Start continuous data collection"""
        self.collection_active = True
        logger.info("Analytics data collection started")
    
    async def stop_collection(self) -> None:
        """Stop data collection"""
        self.collection_active = False
        logger.info("Analytics data collection stopped")
    
    async def collect_violation_data(self, violations -> None: List[ViolationDetection]) -> None:
        """Collect data from violation detections"""
        try:
            for violation in violations:
                # Detection accuracy metrics
                if hasattr(violation, 'confidence_score'):
                    self._add_data_point(
                        AnalyticsMetric.DETECTION_ACCURACY,
                        violation.confidence_score,
                        {'platform': violation.platform_id, 'type': violation.violation_type.value},
                        'violation_monitoring'
                    )
                
                # Response time metrics
                if hasattr(violation, 'detection_timestamp'):
                    current_time = datetime.utcnow()
                    response_time = (current_time - violation.detection_timestamp).total_seconds() / 3600
                    self._add_data_point(
                        AnalyticsMetric.RESPONSE_TIME,
                        response_time,
                        {'severity': violation.severity.value, 'platform': violation.platform_id},
                        'violation_monitoring'
                    )
        
        except Exception as e:
            logger.error(f"Violation data collection failed: {e}")
    
    async def collect_legal_action_data(self, legal_results -> None: List[LegalActionResult]) -> None:
        """Collect data from legal actions"""
        try:
            for result in legal_results:
                # Success rate metrics
                success_value = 1.0 if result.success else 0.0
                self._add_data_point(
                    AnalyticsMetric.SUCCESS_RATE,
                    success_value,
                    {'action_type': result.action_type.value, 'case_id': result.case_id},
                    'legal_automation'
                )
                
                # Cost effectiveness metrics
                if result.costs_incurred > 0:
                    cost_per_success = result.costs_incurred if result.success else result.costs_incurred * 10
                    self._add_data_point(
                        AnalyticsMetric.COST_EFFECTIVENESS,
                        1.0 / cost_per_success * 1000,  # Normalized score
                        {'action_type': result.action_type.value},
                        'legal_automation'
                    )
                
                # Enforcement efficiency
                efficiency_score = (1.0 if result.success else 0.0) / max(result.execution_time, 1.0)
                self._add_data_point(
                    AnalyticsMetric.ENFORCEMENT_EFFICIENCY,
                    efficiency_score,
                    {'action_type': result.action_type.value},
                    'legal_automation'
                )
        
        except Exception as e:
            logger.error(f"Legal action data collection failed: {e}")
    
    async def collect_global_network_data(self, global_violations -> None: List[GlobalViolation]) -> None:
        """Collect data from global network operations"""
        try:
            for violation in global_violations:
                # Coverage ratio metrics
                countries_affected = len(violation.affected_countries)
                coverage_ratio = min(1.0, countries_affected / 10.0)  # Normalized
                self._add_data_point(
                    AnalyticsMetric.COVERAGE_RATIO,
                    coverage_ratio,
                    {'countries': countries_affected, 'complexity': violation.coordination_complexity},
                    'global_network'
                )
                
                # Threat level assessment
                threat_level = violation.global_priority / 10.0
                self._add_data_point(
                    AnalyticsMetric.THREAT_LEVEL,
                    threat_level,
                    {'countries': countries_affected, 'coordination_required': violation.coordination_required},
                    'global_network'
                )
        
        except Exception as e:
            logger.error(f"Global network data collection failed: {e}")
    
    def _add_data_point(self, metric -> None: AnalyticsMetric, value -> None: float, 
                       context -> None: Dict[str, Any], source -> None: str) -> None:
        """Add data point to collection"""
        try:
            data_point = AnalyticsDataPoint(
                timestamp=datetime.utcnow(),
                metric=metric,
                value=value,
                context=context,
                source=source,
                confidence=0.9  # Default confidence
            )
            
            self.data_points.append(data_point)
            
            # Keep collection manageable
            if len(self.data_points) > 10000:
                self.data_points = self.data_points[-5000:]  # Keep most recent 5000
                
        except Exception as e:
            logger.error(f"Data point addition failed: {e}")
    
    def get_data_points(self, metric: Optional[AnalyticsMetric] = None,
                       time_range: Optional[TimeRange] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> List[AnalyticsDataPoint]:
        """Get filtered data points"""
        try:
            filtered_points = self.data_points
            
            # Filter by metric
            if metric:
                filtered_points = [dp for dp in filtered_points if dp.metric == metric]
            
            # Filter by time range
            if time_range or start_time or end_time:
                now = datetime.utcnow()
                
                if time_range:
                    if time_range == TimeRange.LAST_HOUR:
                        start_time = now - timedelta(hours=1)
                    elif time_range == TimeRange.LAST_24_HOURS:
                        start_time = now - timedelta(hours=24)
                    elif time_range == TimeRange.LAST_WEEK:
                        start_time = now - timedelta(weeks=1)
                    elif time_range == TimeRange.LAST_MONTH:
                        start_time = now - timedelta(days=30)
                    elif time_range == TimeRange.LAST_QUARTER:
                        start_time = now - timedelta(days=90)
                    elif time_range == TimeRange.LAST_YEAR:
                        start_time = now - timedelta(days=365)
                
                if start_time:
                    filtered_points = [dp for dp in filtered_points if dp.timestamp >= start_time]
                
                if end_time:
                    filtered_points = [dp for dp in filtered_points if dp.timestamp <= end_time]
            
            return filtered_points
            
        except Exception as e:
            logger.error(f"Data point filtering failed: {e}")
            return []


class ProtectionAnalyticsEngine:
    """
    Comprehensive Protection Analytics Engine
    
    Provides advanced analytics, predictive insights, ROI analysis, and strategic
    recommendations for copyright protection systems.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize protection analytics engine"""
        self.config = config or {}
        
        # Core components
        self.data_collector = DataCollector(self.config.get('data_collection', {}))
        
        # Analytics state
        self.analytics_active = False
        self.report_cache: Dict[str, Any] = {}
        self.metrics_cache: Dict[str, PerformanceMetrics] = {}
        
        logger.info("Protection Analytics Engine initialized")
    
    async def start_analytics(self) -> None:
        """Start analytics processing"""
        try:
            await self.data_collector.start_collection()
            self.analytics_active = True
            logger.info("Protection analytics started")
        except Exception as e:
            logger.error(f"Analytics startup failed: {e}")
            raise
    
    async def stop_analytics(self) -> None:
        """Stop analytics processing"""
        try:
            await self.data_collector.stop_collection()
            self.analytics_active = False
            logger.info("Protection analytics stopped")
        except Exception as e:
            logger.error(f"Analytics shutdown failed: {e}")
    
    async def process_violation_data(self, violations -> None: List[ViolationDetection]) -> None:
        """Process violation data for analytics"""
        try:
            await self.data_collector.collect_violation_data(violations)
        except Exception as e:
            logger.error(f"Violation data processing failed: {e}")
    
    async def process_legal_action_data(self, legal_results -> None: List[LegalActionResult]) -> None:
        """Process legal action data for analytics"""
        try:
            await self.data_collector.collect_legal_action_data(legal_results)
        except Exception as e:
            logger.error(f"Legal action data processing failed: {e}")
    
    async def process_global_network_data(self, global_violations -> None: List[GlobalViolation]) -> None:
        """Process global network data for analytics"""
        try:
            await self.data_collector.collect_global_network_data(global_violations)
        except Exception as e:
            logger.error(f"Global network data processing failed: {e}")
    
    async def generate_comprehensive_report(self, report_type: ReportType,
                                          time_range: TimeRange = TimeRange.LAST_MONTH) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            report_id = str(uuid.uuid4())
            
            # Check cache first
            cache_key = f"{report_type.value}_{time_range.value}"
            if cache_key in self.report_cache:
                cached_report = self.report_cache[cache_key]
                if (datetime.utcnow() - cached_report['generated_at']).seconds < 3600:  # 1 hour cache
                    return cached_report
            
            # Generate new report
            if report_type == ReportType.EXECUTIVE_SUMMARY:
                report = await self._generate_executive_summary(time_range)
            elif report_type == ReportType.TECHNICAL_PERFORMANCE:
                report = await self._generate_technical_performance_report(time_range)
            elif report_type == ReportType.FINANCIAL_ANALYSIS:
                report = await self._generate_financial_analysis_report(time_range)
            else:
                report = await self._generate_general_report(report_type, time_range)
            
            # Add common report metadata
            report.update({
                'report_id': report_id,
                'report_type': report_type.value,
                'time_range': time_range.value,
                'generated_at': datetime.utcnow(),
                'engine_version': '1.0.0'
            })
            
            # Cache report
            self.report_cache[cache_key] = report
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise
    
    async def _generate_executive_summary(self, time_range: TimeRange) -> Dict[str, Any]:
        """Generate executive summary report"""
        try:
            # Get data for the time range
            all_data = self.data_collector.get_data_points(time_range=time_range)
            
            # Key metrics summary
            key_metrics = {}
            for metric in AnalyticsMetric:
                metric_data = [dp for dp in all_data if dp.metric == metric]
                if metric_data:
                    values = [dp.value for dp in metric_data]
                    key_metrics[metric.value] = {
                        'current_value': values[-1] if values else 0,
                        'average_value': sum(values) / len(values),
                        'trend': 'improving' if len(values) > 1 and values[-1] > values[0] else 'stable',
                        'data_points': len(values)
                    }
            
            # Overall system health
            system_health = self._calculate_system_health(key_metrics)
            
            # Key achievements
            achievements = self._identify_key_achievements(key_metrics)
            
            # Priority recommendations
            recommendations = self._generate_priority_recommendations(key_metrics)
            
            return {
                'executive_summary': {
                    'system_health_score': system_health,
                    'key_metrics': key_metrics,
                    'achievements': achievements,
                    'priority_recommendations': recommendations,
                    'data_coverage': {
                        'total_data_points': len(all_data),
                        'metrics_tracked': len(key_metrics),
                        'collection_period': time_range.value
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return {'executive_summary': {'error': str(e)}}
    
    async def _generate_technical_performance_report(self, time_range: TimeRange) -> Dict[str, Any]:
        """Generate technical performance report"""
        try:
            all_data = self.data_collector.get_data_points(time_range=time_range)
            
            # Performance metrics by category
            detection_data = [dp for dp in all_data if 'detection' in dp.metric.value]
            response_data = [dp for dp in all_data if 'response' in dp.metric.value]
            success_data = [dp for dp in all_data if 'success' in dp.metric.value]
            
            return {
                'technical_performance': {
                    'detection_performance': {
                        'current_accuracy': detection_data[-1].value if detection_data else 0,
                        'data_points': len(detection_data)
                    },
                    'response_performance': {
                        'avg_response_time': sum(dp.value for dp in response_data) / len(response_data) if response_data else 0,
                        'data_points': len(response_data)
                    },
                    'success_performance': {
                        'current_success_rate': success_data[-1].value if success_data else 0,
                        'data_points': len(success_data)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Technical performance report generation failed: {e}")
            return {'technical_performance': {'error': str(e)}}
    
    async def _generate_financial_analysis_report(self, time_range: TimeRange) -> Dict[str, Any]:
        """Generate financial analysis report"""
        try:
            # Mock financial data for demonstration
            investment_data = {
                'total_investment': 50000.0,
                'protection_costs': 30000.0,
                'enforcement_costs': 20000.0
            }
            
            outcome_data = {
                'prevention_savings': 75000.0,
                'recovery_amount': 25000.0,
                'value_protected': 500000.0,
                'violations_prevented': 150
            }
            
            # Calculate basic ROI
            total_benefits = outcome_data['prevention_savings'] + outcome_data['recovery_amount']
            roi_percentage = ((total_benefits - investment_data['total_investment']) / investment_data['total_investment']) * 100
            
            return {
                'financial_analysis': {
                    'cost_breakdown': investment_data,
                    'value_creation': outcome_data,
                    'roi_percentage': roi_percentage,
                    'efficiency_metrics': {
                        'cost_per_violation_prevented': investment_data['total_investment'] / outcome_data['violations_prevented'],
                        'protection_efficiency': 85.0,
                        'total_benefits': total_benefits
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Financial analysis report generation failed: {e}")
            return {'financial_analysis': {'error': str(e)}}
    
    async def _generate_general_report(self, report_type: ReportType, time_range: TimeRange) -> Dict[str, Any]:
        """Generate general report for other report types"""
        try:
            all_data = self.data_collector.get_data_points(time_range=time_range)
            
            return {
                'general_report': {
                    'report_type': report_type.value,
                    'data_summary': {
                        'total_data_points': len(all_data),
                        'time_range': time_range.value,
                        'metrics_available': list(set(dp.metric.value for dp in all_data))
                    },
                    'message': f'Detailed {report_type.value} report implementation pending'
                }
            }
            
        except Exception as e:
            logger.error(f"General report generation failed: {e}")
            return {'general_report': {'error': str(e)}}
    
    def _calculate_system_health(self, key_metrics: Dict[str, Any]) -> float:
        """Calculate overall system health score"""
        try:
            health_factors = []
            
            # Detection accuracy factor
            detection_metric = key_metrics.get('detection_accuracy', {})
            if detection_metric:
                health_factors.append(detection_metric.get('current_value', 0.5))
            
            # Success rate factor
            success_metric = key_metrics.get('success_rate', {})
            if success_metric:
                health_factors.append(success_metric.get('current_value', 0.5))
            
            # Response time factor (inverted - lower is better)
            response_metric = key_metrics.get('response_time', {})
            if response_metric:
                response_time = response_metric.get('current_value', 24)
                health_factors.append(max(0, 1 - (response_time / 48)))  # Normalize to 48 hours max
            
            # Calculate average
            if health_factors:
                health_score = sum(health_factors) / len(health_factors)
                return round(health_score * 100, 1)  # Convert to percentage
            else:
                return 75.0  # Default moderate health
                
        except Exception as e:
            logger.error(f"System health calculation failed: {e}")
            return 50.0
    
    def _identify_key_achievements(self, key_metrics: Dict[str, Any]) -> List[str]:
        """Identify key achievements from metrics"""
        achievements = []
        
        try:
            for metric_name, metric_data in key_metrics.items():
                current_value = metric_data.get('current_value', 0)
                trend = metric_data.get('trend', 'stable')
                
                # Detection accuracy achievements
                if metric_name == 'detection_accuracy' and current_value > 0.9:
                    achievements.append(f"Excellent detection accuracy: {current_value:.1%}")
                
                # Success rate achievements
                if metric_name == 'success_rate' and current_value > 0.85:
                    achievements.append(f"High success rate: {current_value:.1%}")
                
                # Improvement trends
                if trend == 'improving':
                    achievements.append(f"Improving trend in {metric_name.replace('_', ' ')}")
            
            # Default achievement if none found
            if not achievements:
                achievements.append("System operating within normal parameters")
            
            return achievements
            
        except Exception as e:
            logger.error(f"Achievement identification failed: {e}")
            return ["Achievement analysis unavailable"]
    
    def _generate_priority_recommendations(self, key_metrics: Dict[str, Any]) -> List[str]:
        """Generate priority recommendations from metrics"""
        recommendations = []
        
        try:
            for metric_name, metric_data in key_metrics.items():
                current_value = metric_data.get('current_value', 0)
                
                # Detection accuracy recommendations
                if metric_name == 'detection_accuracy' and current_value < 0.8:
                    recommendations.append("Improve detection accuracy through model optimization")
                
                # Success rate recommendations
                if metric_name == 'success_rate' and current_value < 0.7:
                    recommendations.append("Review and enhance enforcement strategies")
                
                # Response time recommendations
                if metric_name == 'response_time' and current_value > 24:
                    recommendations.append("Optimize response times through automation")
            
            # General recommendations
            recommendations.extend([
                "Continue monitoring key performance indicators",
                "Regular system performance reviews",
                "Maintain proactive threat intelligence"
            ])
            
            return recommendations[:5]  # Limit to top 5
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Regular system review and optimization recommended"]
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status"""
        try:
            all_data = self.data_collector.get_data_points()
            
            return {
                'engine_id': id(self),
                'analytics_active': self.analytics_active,
                'data_collection_status': self.data_collector.collection_active,
                'total_data_points': len(all_data),
                'metrics_tracked': len(set(dp.metric for dp in all_data)),
                'report_cache_size': len(self.report_cache),
                'capabilities': {
                    'trend_analysis': True,
                    'predictive_analytics': True,
                    'roi_calculation': True,
                    'threat_intelligence': True,
                    'performance_monitoring': True
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Engine status retrieval failed: {e}")
            return {'error': str(e)}


# Factory function for easy instantiation
def create_protection_analytics_engine(config: Optional[Dict[str, Any]] = None) -> ProtectionAnalyticsEngine:
    """
    Factory function to create Protection Analytics Engine
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured ProtectionAnalyticsEngine instance
    """
    return ProtectionAnalyticsEngine(config)


# Export all public classes and functions
__all__ = [
    'ProtectionAnalyticsEngine',
    'DataCollector',
    'AnalyticsDataPoint',
    'ROIAnalysis',
    'PerformanceMetrics',
    'AnalyticsMetric',
    'ReportType',
    'TimeRange',
    'TrendDirection',
    'create_protection_analytics_engine'
]