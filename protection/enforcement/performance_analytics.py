"""Performance Analytics and Reporting System
Advanced analytics for copyright enforcement performance monitoring
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict
import pandas as pd
import numpy as np

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics"""    COUNT = "count"
    RATE = "rate"
    PERCENTAGE = "percentage"
    DURATION = "duration"
    COST = "cost"
    SCORE = "score"


class TimePeriod(Enum):
    """Time periods for analytics"""    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class ReportFormat(Enum):
    """Report output formats"""    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    HTML = "html"
    EXCEL = "xlsx"


@dataclass
class MetricDefinition:
    """Definition of a performance metric"""    id: str
    name: str
    description: str
    metric_type: MetricType
    category: str
    
    # Calculation details
    data_source: str
    aggregation_method: str  # sum, avg, count, rate, etc.
    filter_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Display settings
    unit: str = ""
    decimal_places: int = 2
    format_string: str = "{value}"
    
    # Thresholds for alerting
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    target_value: Optional[float] = None
    
    # Metadata
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MetricValue:
    """A calculated metric value"""    metric_id: str
    timestamp: datetime
    value: float
    period: TimePeriod
    
    # Additional context
    breakdown: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def format_value(self, metric_def: MetricDefinition) -> str:
        """Format value according to metric definition"""        formatted_value = round(self.value, metric_def.decimal_places)
        return metric_def.format_string.format(value=formatted_value, unit=metric_def.unit)


@dataclass
class PerformanceReport:
    """Complete performance report"""    id: str
    title: str
    description: str
    report_type: str
    
    # Time range
    start_date: datetime
    end_date: datetime
    period: TimePeriod
    
    # Content
    metrics: List[MetricValue] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generated_by: str = "automated_system"
    format: ReportFormat = ReportFormat.JSON
    
    def add_metric(self, metric: MetricValue):
        """Add metric to report"""        self.metrics.append(metric)
    
    def add_insight(self, insight: str):
        """Add insight to report"""        self.insights.append(insight)
    
    def add_recommendation(self, recommendation: str):
        """Add recommendation to report"""        self.recommendations.append(recommendation)


class PerformanceAnalytics:
    """Advanced performance analytics engine"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.metric_cache: Dict[str, List[MetricValue]] = defaultdict(list)
        
        # Cache settings
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour
        self.max_cache_size = self.config.get('max_cache_size', 10000)
        
        # Calculation settings
        self.calculation_batch_size = self.config.get('calculation_batch_size', 1000)
        self.parallel_calculations = self.config.get('parallel_calculations', True)
        
        self._setup_default_metrics()
        logger.info("Performance analytics engine initialized")
    
    def _setup_default_metrics(self):
        """Setup default performance metrics"""        default_metrics = [
            # Content Detection Metrics
            MetricDefinition(
                id="total_violations_detected",
                name="Total Violations Detected",
                description="Total number of copyright violations detected",
                metric_type=MetricType.COUNT,
                category="detection",
                data_source="enforcement_cases",
                aggregation_method="count",
                unit="violations"
            ),
            MetricDefinition(
                id="detection_accuracy",
                name="Detection Accuracy",
                description="Percentage of accurately detected violations",
                metric_type=MetricType.PERCENTAGE,
                category="detection",
                data_source="enforcement_cases",
                aggregation_method="rate",
                unit="%",
                target_value=95.0,
                warning_threshold=90.0,
                critical_threshold=85.0
            ),
            MetricDefinition(
                id="false_positive_rate",
                name="False Positive Rate",
                description="Percentage of incorrectly flagged content",
                metric_type=MetricType.PERCENTAGE,
                category="detection",
                data_source="enforcement_cases",
                aggregation_method="rate",
                filter_conditions={"status": "false_positive"},
                unit="%",
                target_value=5.0,
                warning_threshold=10.0,
                critical_threshold=15.0
            ),
            
            # Enforcement Metrics
            MetricDefinition(
                id="successful_takedowns",
                name="Successful Takedowns",
                description="Number of successfully removed infringing content",
                metric_type=MetricType.COUNT,
                category="enforcement",
                data_source="enforcement_cases",
                aggregation_method="count",
                filter_conditions={"outcome": "content_removed"},
                unit="takedowns"
            ),
            MetricDefinition(
                id="takedown_success_rate",
                name="Takedown Success Rate",
                description="Percentage of successful takedown requests",
                metric_type=MetricType.PERCENTAGE,
                category="enforcement",
                data_source="enforcement_cases",
                aggregation_method="rate",
                unit="%",
                target_value=80.0,
                warning_threshold=70.0,
                critical_threshold=60.0
            ),
            MetricDefinition(
                id="average_takedown_time",
                name="Average Takedown Time",
                description="Average time from detection to content removal",
                metric_type=MetricType.DURATION,
                category="enforcement",
                data_source="enforcement_cases",
                aggregation_method="avg",
                unit="hours",
                target_value=24.0,
                warning_threshold=48.0,
                critical_threshold=72.0
            ),
            
            # Platform Performance
            MetricDefinition(
                id="youtube_response_rate",
                name="YouTube Response Rate",
                description="Percentage of YouTube takedown requests responded to",
                metric_type=MetricType.PERCENTAGE,
                category="platform",
                data_source="enforcement_cases",
                aggregation_method="rate",
                filter_conditions={"platform": "youtube"},
                unit="%"
            ),
            MetricDefinition(
                id="spotify_response_rate",
                name="Spotify Response Rate",
                description="Percentage of Spotify takedown requests responded to",
                metric_type=MetricType.PERCENTAGE,
                category="platform",
                data_source="enforcement_cases",
                aggregation_method="rate",
                filter_conditions={"platform": "spotify"},
                unit="%"
            ),
            MetricDefinition(
                id="instagram_response_rate",
                name="Instagram Response Rate",
                description="Percentage of Instagram takedown requests responded to",
                metric_type=MetricType.PERCENTAGE,
                category="platform",
                data_source="enforcement_cases",
                aggregation_method="rate",
                filter_conditions={"platform": "instagram"},
                unit="%"
            ),
            
            # Financial Metrics
            MetricDefinition(
                id="revenue_protected",
                name="Revenue Protected",
                description="Estimated revenue protected through enforcement",
                metric_type=MetricType.COST,
                category="financial",
                data_source="enforcement_cases",
                aggregation_method="sum",
                unit="USD",
                format_string="${value:,.2f}"
            ),
            MetricDefinition(
                id="enforcement_cost",
                name="Enforcement Cost",
                description="Total cost of enforcement activities",
                metric_type=MetricType.COST,
                category="financial",
                data_source="enforcement_cases",
                aggregation_method="sum",
                unit="USD",
                format_string="${value:,.2f}"
            ),
            MetricDefinition(
                id="roi_enforcement",
                name="Enforcement ROI",
                description="Return on investment for enforcement activities",
                metric_type=MetricType.PERCENTAGE,
                category="financial",
                data_source="calculated",
                aggregation_method="calculated",
                unit="%",
                target_value=300.0,
                warning_threshold=200.0,
                critical_threshold=100.0
            ),
            
            # Legal Metrics
            MetricDefinition(
                id="dmca_notices_sent",
                name="DMCA Notices Sent",
                description="Number of DMCA takedown notices sent",
                metric_type=MetricType.COUNT,
                category="legal",
                data_source="legal_documents",
                aggregation_method="count",
                filter_conditions={"document_type": "dmca_notice"},
                unit="notices"
            ),
            MetricDefinition(
                id="legal_escalations",
                name="Legal Escalations",
                description="Number of cases escalated to legal action",
                metric_type=MetricType.COUNT,
                category="legal",
                data_source="escalations",
                aggregation_method="count",
                filter_conditions={"escalation_level": "attorney_review"},
                unit="cases"
            ),
            MetricDefinition(
                id="settlement_rate",
                name="Settlement Rate",
                description="Percentage of legal cases resulting in settlement",
                metric_type=MetricType.PERCENTAGE,
                category="legal",
                data_source="escalations",
                aggregation_method="rate",
                filter_conditions={"outcome": "settlement_reached"},
                unit="%"
            ),
            
            # Quality Metrics
            MetricDefinition(
                id="evidence_quality_score",
                name="Evidence Quality Score",
                description="Average quality score of collected evidence",
                metric_type=MetricType.SCORE,
                category="quality",
                data_source="evidence_packages",
                aggregation_method="avg",
                unit="score",
                target_value=8.5,
                warning_threshold=7.0,
                critical_threshold=6.0
            ),
            MetricDefinition(
                id="similarity_score_avg",
                name="Average Similarity Score",
                description="Average content similarity score for detected violations",
                metric_type=MetricType.SCORE,
                category="quality",
                data_source="content_matches",
                aggregation_method="avg",
                unit="score",
                target_value=0.85,
                warning_threshold=0.75,
                critical_threshold=0.65
            )
        ]
        
        for metric in default_metrics:
            self.metric_definitions[metric.id] = metric
    
    async def calculate_metric(
        self,
        metric_id: str,
        start_date: datetime,
        end_date: datetime,
        period: TimePeriod = TimePeriod.DAY
    ) -> List[MetricValue]:
        """Calculate metric values for time period"""        try:
            metric_def = self.metric_definitions.get(metric_id)
            if not metric_def or not metric_def.enabled:
                logger.error(f"Metric definition not found or disabled: {metric_id}")
                return []
            
            logger.debug(f"Calculating metric {metric_id} from {start_date} to {end_date}")
            
            # Check cache first
            cache_key = f"{metric_id}_{start_date.isoformat()}_{end_date.isoformat()}_{period.value}"
            cached_values = self._get_cached_values(cache_key)
            if cached_values:
                return cached_values
            
            # Generate time buckets
            time_buckets = self._generate_time_buckets(start_date, end_date, period)
            
            # Calculate values for each time bucket
            metric_values = []
            
            if self.parallel_calculations and len(time_buckets) > 1:
                # Calculate in parallel
                tasks = [
                    self._calculate_metric_for_period(metric_def, bucket_start, bucket_end, period)
                    for bucket_start, bucket_end in time_buckets
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Error calculating metric for bucket {i}: {result}")
                        continue
                    if result:
                        metric_values.append(result)
            else:
                # Calculate sequentially
                for bucket_start, bucket_end in time_buckets:
                    value = await self._calculate_metric_for_period(metric_def, bucket_start, bucket_end, period)
                    if value:
                        metric_values.append(value)
            
            # Cache results
            self._cache_values(cache_key, metric_values)
            
            return metric_values
            
        except Exception as e:
            logger.error(f"Error calculating metric {metric_id}: {e}")
            return []
    
    def _generate_time_buckets(
        self,
        start_date: datetime,
        end_date: datetime,
        period: TimePeriod
    ) -> List[Tuple[datetime, datetime]]:
        """Generate time buckets for metric calculation"""        buckets = []
        current = start_date
        
        while current < end_date:
            if period == TimePeriod.HOUR:
                next_time = current + timedelta(hours=1)
            elif period == TimePeriod.DAY:
                next_time = current + timedelta(days=1)
            elif period == TimePeriod.WEEK:
                next_time = current + timedelta(weeks=1)
            elif period == TimePeriod.MONTH:
                # Approximate month as 30 days
                next_time = current + timedelta(days=30)
            elif period == TimePeriod.QUARTER:
                next_time = current + timedelta(days=90)
            elif period == TimePeriod.YEAR:
                next_time = current + timedelta(days=365)
            else:
                next_time = current + timedelta(days=1)
            
            bucket_end = min(next_time, end_date)
            buckets.append((current, bucket_end))
            current = next_time
        
        return buckets
    
    async def _calculate_metric_for_period(
        self,
        metric_def: MetricDefinition,
        start_time: datetime,
        end_time: datetime,
        period: TimePeriod
    ) -> Optional[MetricValue]:
        """Calculate metric value for specific time period"""        try:
            # Get raw data based on data source
            raw_data = await self._get_raw_data(
                metric_def.data_source,
                start_time,
                end_time,
                metric_def.filter_conditions
            )
            
            if not raw_data:
                # Return zero value for empty data
                return MetricValue(
                    metric_id=metric_def.id,
                    timestamp=start_time,
                    value=0.0,
                    period=period
                )
            
            # Apply aggregation method
            value = self._apply_aggregation(raw_data, metric_def.aggregation_method)
            
            # Calculate breakdown if possible
            breakdown = self._calculate_breakdown(raw_data, metric_def)
            
            # Create metric value
            metric_value = MetricValue(
                metric_id=metric_def.id,
                timestamp=start_time,
                value=value,
                period=period,
                breakdown=breakdown,
                metadata={
                    'data_points': len(raw_data),
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                }
            )
            
            return metric_value
            
        except Exception as e:
            logger.error(f"Error calculating metric for period: {e}")
            return None
    
    async def _get_raw_data(
        self,
        data_source: str,
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get raw data from data source"""        try:
            # In real implementation, would query actual databases
            # For now, simulate with empty data
            
            if data_source == "enforcement_cases":
                return await self._get_enforcement_cases_data(start_time, end_time, filters)
            elif data_source == "legal_documents":
                return await self._get_legal_documents_data(start_time, end_time, filters)
            elif data_source == "escalations":
                return await self._get_escalations_data(start_time, end_time, filters)
            elif data_source == "evidence_packages":
                return await self._get_evidence_packages_data(start_time, end_time, filters)
            elif data_source == "content_matches":
                return await self._get_content_matches_data(start_time, end_time, filters)
            else:
                logger.warning(f"Unknown data source: {data_source}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting raw data from {data_source}: {e}")
            return []
    
    async def _get_enforcement_cases_data(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get enforcement cases data"""        # Simulate with sample data
        sample_data = []
        return sample_data
    
    async def _get_legal_documents_data(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get legal documents data"""        # Simulate with sample data
        sample_data = []
        return sample_data
    
    async def _get_escalations_data(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get escalations data"""        # Simulate with sample data
        sample_data = []
        return sample_data
    
    async def _get_evidence_packages_data(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get evidence packages data"""        # Simulate with sample data
        sample_data = []
        return sample_data
    
    async def _get_content_matches_data(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get content matches data"""        # Simulate with sample data
        sample_data = []
        return sample_data
    
    def _apply_aggregation(self, data: List[Dict[str, Any]], method: str) -> float:
        """Apply aggregation method to data"""        try:
            if not data:
                return 0.0
            
            if method == "count":
                return float(len(data))
            
            elif method == "sum":
                # Sum numeric values
                values = [item.get('value', 0) for item in data if isinstance(item.get('value'), (int, float))]
                return sum(values)
            
            elif method == "avg":
                # Average numeric values
                values = [item.get('value', 0) for item in data if isinstance(item.get('value'), (int, float))]
                return statistics.mean(values) if values else 0.0
            
            elif method == "rate":
                # Calculate rate (successes / total)
                total = len(data)
                successes = len([item for item in data if item.get('success', False)])
                return (successes / total * 100) if total > 0 else 0.0
            
            elif method == "calculated":
                # For complex calculations
                return self._perform_complex_calculation(data)
            
            else:
                logger.warning(f"Unknown aggregation method: {method}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error applying aggregation {method}: {e}")
            return 0.0
    
    def _perform_complex_calculation(self, data: List[Dict[str, Any]]) -> float:
        """Perform complex calculations for special metrics"""        # Example: ROI calculation
        try:
            revenue_protected = sum(item.get('revenue_protected', 0) for item in data)
            enforcement_cost = sum(item.get('enforcement_cost', 0) for item in data)
            
            if enforcement_cost > 0:
                roi = (revenue_protected - enforcement_cost) / enforcement_cost * 100
                return roi
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in complex calculation: {e}")
            return 0.0
    
    def _calculate_breakdown(
        self,
        data: List[Dict[str, Any]],
        metric_def: MetricDefinition
    ) -> Dict[str, float]:
        """Calculate breakdown of metric by category"""        try:
            breakdown = {}
            
            # Group by common breakdown categories
            for item in data:
                platform = item.get('platform', 'unknown')
                if platform not in breakdown:
                    breakdown[platform] = 0
                breakdown[platform] += 1
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error calculating breakdown: {e}")
            return {}
    
    def _get_cached_values(self, cache_key: str) -> Optional[List[MetricValue]]:
        """Get cached metric values"""        try:
            # Simple in-memory cache
            # In real implementation, would use Redis or similar
            return None
        except Exception as e:
            logger.error(f"Error getting cached values: {e}")
            return None
    
    def _cache_values(self, cache_key: str, values: List[MetricValue]):
        """Cache metric values"""        try:
            # Simple in-memory cache
            # In real implementation, would use Redis or similar
            pass
        except Exception as e:
            logger.error(f"Error caching values: {e}")
    
    async def generate_performance_report(
        self,
        report_type: str,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None,
        period: TimePeriod = TimePeriod.DAY
    ) -> PerformanceReport:
        """Generate comprehensive performance report"""        try:
            report_id = f"PERF-{report_type}-{int(datetime.utcnow().timestamp())}"
            
            report = PerformanceReport(
                id=report_id,
                title=f"Performance Report - {report_type.title()}",
                description=f"Performance analytics report for {start_date.date()} to {end_date.date()}",
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
                period=period
            )
            
            # Use default metrics if none specified
            if not metrics:
                metrics = list(self.metric_definitions.keys())
            
            # Calculate all requested metrics
            for metric_id in metrics:
                if metric_id not in self.metric_definitions:
                    logger.warning(f"Unknown metric: {metric_id}")
                    continue
                
                metric_values = await self.calculate_metric(metric_id, start_date, end_date, period)
                report.metrics.extend(metric_values)
            
            # Generate insights
            insights = await self._generate_insights(report.metrics)
            for insight in insights:
                report.add_insight(insight)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(report.metrics)
            for recommendation in recommendations:
                report.add_recommendation(recommendation)
            
            # Generate charts data
            charts = await self._generate_charts_data(report.metrics)
            report.charts.extend(charts)
            
            logger.info(f"Generated performance report: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            raise
    
    async def _generate_insights(self, metrics: List[MetricValue]) -> List[str]:
        """Generate insights from metric data"""        insights = []
        
        try:
            # Group metrics by category
            by_category = defaultdict(list)
            for metric in metrics:
                metric_def = self.metric_definitions.get(metric.metric_id)
                if metric_def:
                    by_category[metric_def.category].append(metric)
            
            # Detection insights
            if 'detection' in by_category:
                detection_metrics = by_category['detection']
                total_violations = sum(m.value for m in detection_metrics if 'total_violations' in m.metric_id)
                if total_violations > 1000:
                    insights.append(f"High violation detection rate: {total_violations:,.0f} violations detected")
                
                accuracy_metrics = [m for m in detection_metrics if 'accuracy' in m.metric_id]
                if accuracy_metrics:
                    avg_accuracy = statistics.mean(m.value for m in accuracy_metrics)
                    if avg_accuracy < 90:
                        insights.append(f"Detection accuracy below target: {avg_accuracy:.1f}%")
            
            # Enforcement insights
            if 'enforcement' in by_category:
                enforcement_metrics = by_category['enforcement']
                success_rate_metrics = [m for m in enforcement_metrics if 'success_rate' in m.metric_id]
                if success_rate_metrics:
                    avg_success_rate = statistics.mean(m.value for m in success_rate_metrics)
                    if avg_success_rate > 85:
                        insights.append(f"Excellent enforcement success rate: {avg_success_rate:.1f}%")
                    elif avg_success_rate < 70:
                        insights.append(f"Low enforcement success rate requires attention: {avg_success_rate:.1f}%")
            
            # Financial insights
            if 'financial' in by_category:
                financial_metrics = by_category['financial']
                revenue_metrics = [m for m in financial_metrics if 'revenue' in m.metric_id]
                if revenue_metrics:
                    total_revenue = sum(m.value for m in revenue_metrics)
                    insights.append(f"Total revenue protected: ${total_revenue:,.2f}")
                
                roi_metrics = [m for m in financial_metrics if 'roi' in m.metric_id]
                if roi_metrics:
                    avg_roi = statistics.mean(m.value for m in roi_metrics)
                    if avg_roi > 200:
                        insights.append(f"Strong ROI on enforcement activities: {avg_roi:.1f}%")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
        
        return insights
    
    async def _generate_recommendations(self, metrics: List[MetricValue]) -> List[str]:
        """Generate recommendations based on metric data"""        recommendations = []
        
        try:
            # Analyze metric trends and thresholds
            for metric in metrics:
                metric_def = self.metric_definitions.get(metric.metric_id)
                if not metric_def:
                    continue
                
                # Check against thresholds
                if metric_def.critical_threshold and metric.value <= metric_def.critical_threshold:
                    recommendations.append(
                        f"CRITICAL: {metric_def.name} is below critical threshold "
                        f"({metric.value:.1f} vs {metric_def.critical_threshold:.1f})"
                    )
                elif metric_def.warning_threshold and metric.value <= metric_def.warning_threshold:
                    recommendations.append(
                        f"WARNING: {metric_def.name} is below warning threshold "
                        f"({metric.value:.1f} vs {metric_def.warning_threshold:.1f})"
                    )
                
                # Check against targets
                if metric_def.target_value:
                    if metric.value < metric_def.target_value * 0.9:  # 10% below target
                        recommendations.append(
                            f"Consider improving {metric_def.name} to reach target "
                            f"({metric.value:.1f} vs target {metric_def.target_value:.1f})"
                        )
            
            # General recommendations
            recommendations.extend([
                "Monitor false positive rates to maintain detection quality",
                "Review platform-specific performance for optimization opportunities",
                "Consider escalating repeat infringers for stronger deterrent effect",
                "Analyze high-value content protection for revenue impact"
            ])
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    async def _generate_charts_data(self, metrics: List[MetricValue]) -> List[Dict[str, Any]]:
        """Generate chart data for visualization"""        charts = []
        
        try:
            # Group metrics by metric type for different chart types
            by_metric_id = defaultdict(list)
            for metric in metrics:
                by_metric_id[metric.metric_id].append(metric)
            
            for metric_id, metric_values in by_metric_id.items():
                metric_def = self.metric_definitions.get(metric_id)
                if not metric_def:
                    continue
                
                # Time series chart data
                time_series_data = {
                    'type': 'line',
                    'title': metric_def.name,
                    'metric_id': metric_id,
                    'data': {
                        'labels': [m.timestamp.isoformat() for m in metric_values],
                        'values': [m.value for m in metric_values],
                        'unit': metric_def.unit
                    }
                }
                charts.append(time_series_data)
                
                # Breakdown pie chart if breakdown data available
                if metric_values and metric_values[0].breakdown:
                    breakdown_data = {
                        'type': 'pie',
                        'title': f"{metric_def.name} - Breakdown",
                        'metric_id': f"{metric_id}_breakdown",
                        'data': {
                            'labels': list(metric_values[0].breakdown.keys()),
                            'values': list(metric_values[0].breakdown.values())
                        }
                    }
                    charts.append(breakdown_data)
            
        except Exception as e:
            logger.error(f"Error generating charts data: {e}")
        
        return charts
    
    async def export_report(
        self,
        report: PerformanceReport,
        format: ReportFormat,
        output_path: Optional[str] = None
    ) -> str:
        """Export report to specified format"""        try:
            if not output_path:
                output_path = f"reports/{report.id}.{format.value}"
            
            if format == ReportFormat.JSON:
                return await self._export_json(report, output_path)
            elif format == ReportFormat.CSV:
                return await self._export_csv(report, output_path)
            elif format == ReportFormat.HTML:
                return await self._export_html(report, output_path)
            elif format == ReportFormat.PDF:
                return await self._export_pdf(report, output_path)
            elif format == ReportFormat.EXCEL:
                return await self._export_excel(report, output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            raise
    
    async def _export_json(self, report: PerformanceReport, output_path: str) -> str:
        """Export report as JSON"""        try:
            # Convert to JSON-serializable format
            report_data = {
                'id': report.id,
                'title': report.title,
                'description': report.description,
                'report_type': report.report_type,
                'start_date': report.start_date.isoformat(),
                'end_date': report.end_date.isoformat(),
                'period': report.period.value,
                'generated_at': report.generated_at.isoformat(),
                'generated_by': report.generated_by,
                'metrics': [
                    {
                        'metric_id': m.metric_id,
                        'timestamp': m.timestamp.isoformat(),
                        'value': m.value,
                        'period': m.period.value,
                        'breakdown': m.breakdown,
                        'metadata': m.metadata
                    }
                    for m in report.metrics
                ],
                'charts': report.charts,
                'insights': report.insights,
                'recommendations': report.recommendations
            }
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"Report exported to JSON: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            raise
    
    async def _export_csv(self, report: PerformanceReport, output_path: str) -> str:
        """Export report as CSV"""        try:
            # Create DataFrame from metrics
            rows = []
            for metric in report.metrics:
                metric_def = self.metric_definitions.get(metric.metric_id)
                rows.append({
                    'Metric ID': metric.metric_id,
                    'Metric Name': metric_def.name if metric_def else metric.metric_id,
                    'Category': metric_def.category if metric_def else 'unknown',
                    'Timestamp': metric.timestamp.isoformat(),
                    'Value': metric.value,
                    'Unit': metric_def.unit if metric_def else '',
                    'Period': metric.period.value,
                    'Data Points': metric.metadata.get('data_points', 0)
                })
            
            df = pd.DataFrame(rows)
            df.to_csv(output_path, index=False)
            
            logger.info(f"Report exported to CSV: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            raise
    
    async def _export_html(self, report: PerformanceReport, output_path: str) -> str:
        """Export report as HTML"""        try:
            html_content = f"""            <!DOCTYPE html>
            <html>
            <head>
                <title>{report.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .metric {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .insights {{ background-color: #e8f4fd; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                    .recommendations {{ background-color: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{report.title}</h1>
                    <p>{report.description}</p>
                    <p><strong>Period:</strong> {report.start_date.date()} to {report.end_date.date()}</p>
                    <p><strong>Generated:</strong> {report.generated_at.isoformat()}</p>
                </div>
                
                <h2>Key Metrics</h2>
            """            
            # Add metrics
            for metric in report.metrics[:10]:  # Limit to first 10 for HTML
                metric_def = self.metric_definitions.get(metric.metric_id)
                if metric_def:
                    formatted_value = metric.format_value(metric_def)
                    html_content += f"""                    <div class="metric">
                        <h3>{metric_def.name}</h3>
                        <p><strong>Value:</strong> {formatted_value}</p>
                        <p><strong>Description:</strong> {metric_def.description}</p>
                    </div>
                    """            
            # Add insights
            if report.insights:
                html_content += '<div class="insights"><h2>Key Insights</h2><ul>'
                for insight in report.insights:
                    html_content += f'<li>{insight}</li>'
                html_content += '</ul></div>'
            
            # Add recommendations
            if report.recommendations:
                html_content += '<div class="recommendations"><h2>Recommendations</h2><ul>'
                for recommendation in report.recommendations:
                    html_content += f'<li>{recommendation}</li>'
                html_content += '</ul></div>'
            
            html_content += """            </body>
            </html>
            """            
            with open(output_path, 'w') as f:
                f.write(html_content)
            
            logger.info(f"Report exported to HTML: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting HTML: {e}")
            raise
    
    async def _export_pdf(self, report: PerformanceReport, output_path: str) -> str:
        """Export report as PDF"""        try:
            # In real implementation, would use libraries like reportlab or weasyprint
            # For now, create a simple text file with PDF extension
            
            text_content = f"""            {report.title}
            {report.description}
            
            Period: {report.start_date.date()} to {report.end_date.date()}
            Generated: {report.generated_at.isoformat()}
            
            KEY METRICS:
            """            
            for metric in report.metrics[:10]:
                metric_def = self.metric_definitions.get(metric.metric_id)
                if metric_def:
                    formatted_value = metric.format_value(metric_def)
                    text_content += f"\n{metric_def.name}: {formatted_value}"
            
            if report.insights:
                text_content += "\n\nKEY INSIGHTS:\n"
                for insight in report.insights:
                    text_content += f"• {insight}\n"
            
            if report.recommendations:
                text_content += "\nRECOMMENDATIONS:\n"
                for recommendation in report.recommendations:
                    text_content += f"• {recommendation}\n"
            
            with open(output_path, 'w') as f:
                f.write(text_content)
            
            logger.info(f"Report exported to PDF: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            raise
    
    async def _export_excel(self, report: PerformanceReport, output_path: str) -> str:
        """Export report as Excel file"""        try:
            # Create workbook with multiple sheets
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Metrics sheet
                metrics_data = []
                for metric in report.metrics:
                    metric_def = self.metric_definitions.get(metric.metric_id)
                    metrics_data.append({
                        'Metric ID': metric.metric_id,
                        'Metric Name': metric_def.name if metric_def else metric.metric_id,
                        'Category': metric_def.category if metric_def else 'unknown',
                        'Timestamp': metric.timestamp,
                        'Value': metric.value,
                        'Unit': metric_def.unit if metric_def else '',
                        'Period': metric.period.value
                    })
                
                metrics_df = pd.DataFrame(metrics_data)
                metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
                
                # Summary sheet
                summary_data = {
                    'Report Information': [
                        f"Title: {report.title}",
                        f"Description: {report.description}",
                        f"Period: {report.start_date.date()} to {report.end_date.date()}",
                        f"Generated: {report.generated_at.isoformat()}",
                        f"Total Metrics: {len(report.metrics)}"
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            logger.info(f"Report exported to Excel: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting Excel: {e}")
            raise
    
    async def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """Get data for analytics dashboard"""        try:
            # Calculate key metrics for dashboard
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)  # Last 7 days
            
            dashboard_metrics = [
                'total_violations_detected',
                'takedown_success_rate',
                'average_takedown_time',
                'revenue_protected',
                'enforcement_cost'
            ]
            
            # Calculate metrics
            metrics_data = {}
            for metric_id in dashboard_metrics:
                values = await self.calculate_metric(metric_id, start_date, end_date, TimePeriod.DAY)
                if values:
                    latest_value = values[-1] if values else None
                    trend = self._calculate_trend(values)
                    
                    metrics_data[metric_id] = {
                        'current_value': latest_value.value if latest_value else 0,
                        'trend': trend,
                        'values': [v.value for v in values]
                    }
            
            # Platform breakdown
            platform_data = await self._get_platform_breakdown()
            
            # Recent alerts
            alerts = await self._get_recent_alerts()
            
            dashboard_data = {
                'metrics': metrics_data,
                'platform_breakdown': platform_data,
                'alerts': alerts,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}
    
    def _calculate_trend(self, values: List[MetricValue]) -> str:
        """Calculate trend direction from metric values"""        try:
            if len(values) < 2:
                return 'stable'
            
            recent_avg = statistics.mean(v.value for v in values[-3:])
            older_avg = statistics.mean(v.value for v in values[:-3]) if len(values) > 3 else values[0].value
            
            if recent_avg > older_avg * 1.05:  # 5% increase
                return 'increasing'
            elif recent_avg < older_avg * 0.95:  # 5% decrease
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return 'stable'
    
    async def _get_platform_breakdown(self) -> Dict[str, float]:
        """Get breakdown by platform"""        try:
            # In real implementation, would query actual data
            return {
                'youtube': 45.2,
                'spotify': 28.7,
                'instagram': 15.8,
                'tiktok': 10.3
            }
        except Exception as e:
            logger.error(f"Error getting platform breakdown: {e}")
            return {}
    
    async def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""        try:
            # In real implementation, would check metrics against thresholds
            return [
                {
                    'level': 'warning',
                    'message': 'YouTube response rate below threshold',
                    'timestamp': datetime.utcnow().isoformat()
                }
            ]
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []


# Global instance
performance_analytics = PerformanceAnalytics()


async def get_performance_analytics() -> PerformanceAnalytics:
    """Get the global performance analytics instance"""    return performance_analytics


__all__ = [
    'PerformanceAnalytics',
    'MetricDefinition',
    'MetricValue',
    'PerformanceReport',
    'MetricType',
    'TimePeriod',
    'ReportFormat',
    'get_performance_analytics'
]
