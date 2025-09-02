"""Advanced Fingerprint Analytics Engine

Comprehensive analytics and reporting system for fingerprint data with statistical
analysis, trend detection, and business intelligence capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from sqlalchemy import and_, or_, func, text, select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats

from backend.core.database import DatabaseManager
from backend.core.config import settings
from backend.core.exceptions import DatabaseError, ValidationError
from backend.database.fingerprinting.fingerprint_storage import (
    FingerprintStorageModel, FingerprintMatchModel
)
from backend.utils.performance import PerformanceMonitor
from backend.utils.visualization import ChartGenerator

logger = logging.getLogger(__name__)


class AnalyticsTimeframe(Enum):
    """
Analytics timeframe options"""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"


class MetricType(Enum):
    """Types of metrics to analyze"""

    CREATION_RATE = "creation_rate"
    MATCH_RATE = "match_rate"
    QUALITY_DISTRIBUTION = "quality_distribution"
    CONTENT_TYPE_DISTRIBUTION = "content_type_distribution"
    USER_ACTIVITY = "user_activity"
    STORAGE_USAGE = "storage_usage"
    PERFORMANCE_METRICS = "performance_metrics"
    SIMILARITY_PATTERNS = "similarity_patterns"


@dataclass
class AnalyticsQuery:
    """Configuration for analytics queries"""
    timeframe: AnalyticsTimeframe
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Filters
    user_ids: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    quality_levels: Optional[List[str]] = None
    
    # Grouping and aggregation
    group_by: Optional[List[str]] = None
    metrics: List[MetricType] = None
    
    # Advanced options
    include_trends: bool = True
    include_predictions: bool = False
    confidence_level: float = 0.95
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = [MetricType.CREATION_RATE, MetricType.QUALITY_DISTRIBUTION]
        
        # Set default date range based on timeframe
        if self.start_date is None or self.end_date is None:
            now = datetime.now(timezone.utc)
            
            if self.timeframe == AnalyticsTimeframe.HOUR:
                self.start_date = now - timedelta(hours=24)
                self.end_date = now
            elif self.timeframe == AnalyticsTimeframe.DAY:
                self.start_date = now - timedelta(days=30)
                self.end_date = now
            elif self.timeframe == AnalyticsTimeframe.WEEK:
                self.start_date = now - timedelta(weeks=12)
                self.end_date = now
            elif self.timeframe == AnalyticsTimeframe.MONTH:
                self.start_date = now - timedelta(days=365)
                self.end_date = now
            else:
                self.end_date = now


@dataclass
class TrendAnalysis:
    """
Results of trend analysis"""
    metric_name: str
    timeframe: AnalyticsTimeframe
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0-1 scale
    slope: float
    r_squared: float
    p_value: float
    confidence_interval: Tuple[float, float]
    seasonal_component: Optional[Dict[str, float]] = None
    anomalies: List[Dict[str, Any]] = None


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    query: AnalyticsQuery
    generated_at: datetime
    
    # Core metrics
    summary_metrics: Dict[str, Any]
    time_series_data: Dict[str, List[Dict[str, Any]]]
    distribution_data: Dict[str, Dict[str, Any]]
    
    # Advanced analytics
    trend_analyses: List[TrendAnalysis]
    correlations: Dict[str, Dict[str, float]]
    predictions: Optional[Dict[str, Any]] = None
    
    # Insights and recommendations
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    
    # Metadata
    data_quality_score: float
    processing_time_seconds: float


class StatisticalAnalyzer:
    """
Statistical analysis component for fingerprint data"""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def detect_trend(
        self,
        time_series: List[Tuple[datetime, float]],
        confidence_level: float = 0.95
    ) -> TrendAnalysis:
        """Detect trends in time series data"""
        try:
            if len(time_series) < 3:
                return TrendAnalysis(
                    metric_name="unknown",
                    timeframe=AnalyticsTimeframe.DAY,
                    trend_direction="stable",
                    trend_strength=0.0,
                    slope=0.0,
                    r_squared=0.0,
                    p_value=1.0,
                    confidence_interval=(0.0, 0.0)
                )
            
            # Convert to numpy arrays
            timestamps = np.array([t.timestamp() for t, _ in time_series])
            values = np.array([v for _, v in time_series])
            
            # Normalize timestamps to start from 0
            timestamps = timestamps - timestamps[0]
            
            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
            
            # Determine trend direction
            if p_value < (1 - confidence_level):
                if slope > 0:
                    trend_direction = "increasing"
                else:
                    trend_direction = "decreasing"
                trend_strength = abs(r_value)
            else:
                trend_direction = "stable"
                trend_strength = 0.0
            
            # Calculate confidence interval
            t_val = stats.t.ppf((1 + confidence_level) / 2, len(values) - 2)
            margin_error = t_val * std_err
            confidence_interval = (slope - margin_error, slope + margin_error)
            
            # Detect anomalies using z-score
            residuals = values - (slope * timestamps + intercept)
            z_scores = np.abs(stats.zscore(residuals))
            anomaly_threshold = 2.0
            
            anomalies = []
            for i, (timestamp, value) in enumerate(time_series):
                if z_scores[i] > anomaly_threshold:
                    anomalies.append({
                        'timestamp': timestamp.isoformat(),
                        'value': float(value),
                        'z_score': float(z_scores[i]),
                        'residual': float(residuals[i])
                    })
            
            return TrendAnalysis(
                metric_name="unknown",
                timeframe=AnalyticsTimeframe.DAY,
                trend_direction=trend_direction,
                trend_strength=float(trend_strength),
                slope=float(slope),
                r_squared=float(r_value ** 2),
                p_value=float(p_value),
                confidence_interval=(float(confidence_interval[0]), float(confidence_interval[1])),
                anomalies=anomalies
            )
            
        except Exception as e:
            self.logger.error(f"Trend detection failed: {e}")
            return TrendAnalysis(
                metric_name="error",
                timeframe=AnalyticsTimeframe.DAY,
                trend_direction="stable",
                trend_strength=0.0,
                slope=0.0,
                r_squared=0.0,
                p_value=1.0,
                confidence_interval=(0.0, 0.0)
            )
    
    def calculate_correlations(
        self,
        metrics_data: Dict[str, List[float]]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate correlations between different metrics"""
        try:
            if len(metrics_data) < 2:
                return {}
            
            # Convert to DataFrame for easier correlation calculation
            df = pd.DataFrame(metrics_data)
            
            # Calculate correlation matrix
            correlation_matrix = df.corr()
            
            # Convert to nested dictionary
            correlations = {}
            for metric1 in correlation_matrix.index:
                correlations[metric1] = {}
                for metric2 in correlation_matrix.columns:
                    if metric1 != metric2:
                        correlations[metric1][metric2] = float(correlation_matrix.loc[metric1, metric2])
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Correlation calculation failed: {e}")
            return {}
    
    def detect_seasonality(
        """Execute business logic for {func_name}"""
                try:
                    logger.info(f"Executing {func_name}")
            
                    # Input validation
                    if data is None:
                        raise ValueError("Input data is required")
            
                    # Initialize execution context
                    execution_start = datetime.utcnow()
            
                    # Core business logic execution
                    result = {
                        "status": "success",
                        "data": data,
                        "processed_at": execution_start.isoformat(),
                        "function": "{func_name}"
                    }
            
                    # Apply business rules if available
                    if hasattr(self, 'business_rules'):
                        for rule in self.business_rules:
                            result = self._apply_business_rule(result, rule)
            
                    # Log execution metrics
                    execution_time = (datetime.utcnow() - execution_start).total_seconds()
                    result["execution_time"] = execution_time
            
                    logger.info(f"{func_name} completed successfully in {execution_time:.3f}s")
                    return result
            
                except Exception as e:
                    logger.error(f"{func_name} failed: {e}")
                    raise
    ) -> Optional[Dict[str, float]]:
        """Detect seasonal patterns in time series data"""
        try:
            if len(time_series) < period * 2:
                return None
            
            values = np.array([v for _, v in time_series])
            
            # Calculate seasonal components
            seasonal_means = {}
            for i in range(period):
                period_values = values[i::period]
                if len(period_values) > 0:
                    seasonal_means[str(i)] = float(np.mean(period_values))
            
            return seasonal_means
            
        except Exception as e:
            self.logger.error(f"Seasonality detection failed: {e}")
            return None
    
    def cluster_analysis(
        self,
        feature_data: np.ndarray,
        n_clusters: int = 5
    ) -> Dict[str, Any]:
        """Perform cluster analysis on fingerprint features"""
        try:
            if len(feature_data) < n_clusters:
                return {"error": "Insufficient data for clustering"}
            
            # Standardize features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(feature_data)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(scaled_features)
            
            # Calculate cluster statistics
            cluster_stats = {}
            for i in range(n_clusters):
                cluster_mask = cluster_labels == i
                cluster_data = feature_data[cluster_mask]
                
                cluster_stats[f"cluster_{i}"] = {
                    "size": int(np.sum(cluster_mask)),
                    "percentage": float(np.sum(cluster_mask) / len(feature_data) * 100),
                    "centroid": kmeans.cluster_centers_[i].tolist(),
                    "inertia": float(np.sum((cluster_data - kmeans.cluster_centers_[i]) ** 2))
                }
            
            return {
                "n_clusters": n_clusters,
                "total_inertia": float(kmeans.inertia_),
                "cluster_stats": cluster_stats,
                "labels": cluster_labels.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Cluster analysis failed: {e}")
            return {"error": str(e)}


class FingerprintAnalyticsEngine:
    """
    Comprehensive analytics engine for fingerprint data with statistical analysis,
    trend detection, and business intelligence capabilities.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.statistical_analyzer = StatisticalAnalyzer()
        self.chart_generator = ChartGenerator()
        self.performance_monitor = PerformanceMonitor()
        self.logger = logging.getLogger(__name__)
    
    async def generate_analytics_report(
        self,
        query: AnalyticsQuery
    ) -> AnalyticsReport:
        """
        Generate comprehensive analytics report
        
        Args:
            query: AnalyticsQuery with analysis parameters
            
        Returns:
            AnalyticsReport with all analytics results
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            self.logger.info(f"Generating analytics report for timeframe: {query.timeframe}")
            
            # Initialize report structure
            report = AnalyticsReport(
                query=query,
                generated_at=start_time,
                summary_metrics={},
                time_series_data={},
                distribution_data={},
                trend_analyses=[],
                correlations={},
                insights=[],
                recommendations=[],
                data_quality_score=0.0,
                processing_time_seconds=0.0
            )
            
            # Generate summary metrics
            report.summary_metrics = await self._generate_summary_metrics(query)
            
            # Generate time series data for requested metrics
            report.time_series_data = await self._generate_time_series_data(query)
            
            # Generate distribution data
            report.distribution_data = await self._generate_distribution_data(query)
            
            # Perform trend analyses
            if query.include_trends:
                report.trend_analyses = await self._analyze_trends(query, report.time_series_data)
            
            # Calculate correlations
            report.correlations = await self._calculate_metric_correlations(report.time_series_data)
            
            # Generate predictions
            if query.include_predictions:
                report.predictions = await self._generate_predictions(query, report.time_series_data)
            
            # Generate insights and recommendations
            report.insights = await self._generate_insights(report)
            report.recommendations = await self._generate_recommendations(report)
            
            # Calculate data quality score
            report.data_quality_score = await self._calculate_data_quality_score(query)
            
            # Calculate processing time
            end_time = datetime.now(timezone.utc)
            report.processing_time_seconds = (end_time - start_time).total_seconds()
            
            self.logger.info(f"Analytics report generated in {report.processing_time_seconds:.2f}s")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Analytics report generation failed: {e}")
            raise DatabaseError(f"Analytics report generation failed: {e}")
    
    async def _generate_summary_metrics(
        self,
        query: AnalyticsQuery
    ) -> Dict[str, Any]:
        """Generate summary metrics for the specified timeframe"""
        try:
            async with self.db_manager.get_session() as session:
                # Build base conditions
                conditions = self._build_query_conditions(query)
                
                # Total fingerprints
                total_query = select(func.count()).select_from(FingerprintStorageModel)
                if conditions:
                    total_query = total_query.where(and_(*conditions))
                
                total_result = await session.execute(total_query)
                total_fingerprints = total_result.scalar()
                
                # Active fingerprints
                active_conditions = conditions + [FingerprintStorageModel.status == 'active']
                active_query = select(func.count()).select_from(FingerprintStorageModel).where(and_(*active_conditions))
                active_result = await session.execute(active_query)
                active_fingerprints = active_result.scalar()
                
                # Average confidence score
                confidence_query = select(func.avg(FingerprintStorageModel.confidence_score)).select_from(FingerprintStorageModel)
                if conditions:
                    confidence_query = confidence_query.where(and_(*conditions))
                
                confidence_result = await session.execute(confidence_query)
                avg_confidence = confidence_result.scalar() or 0.0
                
                # Total storage size
                storage_query = select(func.sum(FingerprintStorageModel.storage_size)).select_from(FingerprintStorageModel)
                if conditions:
                    storage_query = storage_query.where(and_(*conditions))
                
                storage_result = await session.execute(storage_query)
                total_storage = storage_result.scalar() or 0
                
                # Unique users
                user_query = select(func.count(func.distinct(FingerprintStorageModel.user_id))).select_from(FingerprintStorageModel)
                if conditions:
                    user_query = user_query.where(and_(*conditions))
                
                user_result = await session.execute(user_query)
                unique_users = user_result.scalar()
                
                # Match statistics
                match_conditions = []
                if query.start_date:
                    match_conditions.append(FingerprintMatchModel.detected_at >= query.start_date)
                if query.end_date:
                    match_conditions.append(FingerprintMatchModel.detected_at <= query.end_date)
                
                match_query = select(
                    func.count().label('total_matches'),
                    func.avg(FingerprintMatchModel.similarity_score).label('avg_similarity')
                ).select_from(FingerprintMatchModel)
                
                if match_conditions:
                    match_query = match_query.where(and_(*match_conditions))
                
                match_result = await session.execute(match_query)
                match_stats = match_result.first()
                
                return {
                    'total_fingerprints': total_fingerprints,
                    'active_fingerprints': active_fingerprints,
                    'unique_users': unique_users,
                    'average_confidence_score': float(avg_confidence),
                    'total_storage_bytes': total_storage,
                    'total_storage_gb': total_storage / (1024**3) if total_storage else 0.0,
                    'total_matches': match_stats.total_matches if match_stats else 0,
                    'average_match_similarity': float(match_stats.avg_similarity) if match_stats and match_stats.avg_similarity else 0.0,
                    'activity_rate': active_fingerprints / total_fingerprints if total_fingerprints > 0 else 0.0
                }
                
        except Exception as e:
            self.logger.error(f"Summary metrics generation failed: {e}")
            return {}
    
    async def _generate_time_series_data(
        self,
        query: AnalyticsQuery
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate time series data for requested metrics"""
        try:
            time_series_data = {}
            
            # Generate time intervals based on timeframe
            intervals = self._generate_time_intervals(query)
            
            async with self.db_manager.get_session() as session:
                for metric in query.metrics:
                    if metric == MetricType.CREATION_RATE:
                        time_series_data['creation_rate'] = await self._get_creation_rate_series(
                            session, query, intervals
                        )
                    
                    elif metric == MetricType.MATCH_RATE:
                        time_series_data['match_rate'] = await self._get_match_rate_series(
                            session, query, intervals
                        )
                    
                    elif metric == MetricType.QUALITY_DISTRIBUTION:
                        time_series_data['average_quality'] = await self._get_quality_series(
                            session, query, intervals
                        )
                    
                    elif metric == MetricType.STORAGE_USAGE:
                        time_series_data['storage_usage'] = await self._get_storage_usage_series(
                            session, query, intervals
                        )
                    
                    elif metric == MetricType.USER_ACTIVITY:
                        time_series_data['user_activity'] = await self._get_user_activity_series(
                            session, query, intervals
                        )
            
            return time_series_data
            
        except Exception as e:
            self.logger.error(f"Time series data generation failed: {e}")
            return {}
    
    async def _generate_distribution_data(
        self,
        query: AnalyticsQuery
    ) -> Dict[str, Dict[str, Any]]:
        """Generate distribution data for various dimensions"""
        try:
            distribution_data = {}
            
            async with self.db_manager.get_session() as session:
                conditions = self._build_query_conditions(query)
                
                # Content type distribution
                content_type_query = select(
                    FingerprintStorageModel.content_type,
                    func.count().label('count')
                ).group_by(FingerprintStorageModel.content_type)
                
                if conditions:
                    content_type_query = content_type_query.where(and_(*conditions))
                
                content_type_result = await session.execute(content_type_query)
                content_type_dist = {row.content_type: row.count for row in content_type_result.fetchall()}
                
                distribution_data['content_type'] = {
                    'data': content_type_dist,
                    'total': sum(content_type_dist.values())
                }
                
                # Quality level distribution
                quality_query = select(
                    FingerprintStorageModel.quality_level,
                    func.count().label('count')
                ).group_by(FingerprintStorageModel.quality_level)
                
                if conditions:
                    quality_query = quality_query.where(and_(*conditions))
                
                quality_result = await session.execute(quality_query)
                quality_dist = {row.quality_level: row.count for row in quality_result.fetchall()}
                
                distribution_data['quality_level'] = {
                    'data': quality_dist,
                    'total': sum(quality_dist.values())
                }
                
                # Confidence score distribution (bucketed)
                confidence_buckets = await self._get_confidence_distribution(session, conditions)
                distribution_data['confidence_score'] = {
                    'data': confidence_buckets,
                    'total': sum(confidence_buckets.values())
                }
                
                # User activity distribution
                user_activity_query = select(
                    FingerprintStorageModel.user_id,
                    func.count().label('fingerprint_count')
                ).group_by(FingerprintStorageModel.user_id)
                
                if conditions:
                    user_activity_query = user_activity_query.where(and_(*conditions))
                
                user_activity_result = await session.execute(user_activity_query)
                user_activity_raw = {row.user_id: row.fingerprint_count for row in user_activity_result.fetchall()}
                
                # Bucket user activity
                user_activity_buckets = self._bucket_user_activity(user_activity_raw)
                distribution_data['user_activity'] = {
                    'data': user_activity_buckets,
                    'total': len(user_activity_raw)
                }
            
            return distribution_data
            
        except Exception as e:
            self.logger.error(f"Distribution data generation failed: {e}")
            return {}
    
    async def _analyze_trends(
        self,
        query: AnalyticsQuery,
        time_series_data: Dict[str, List[Dict[str, Any]]]
    ) -> List[TrendAnalysis]:
        """Analyze trends in time series data"""
        try:
            trend_analyses = []
            
            for metric_name, data_points in time_series_data.items():
                if not data_points:
                    continue
                
                # Convert to format suitable for trend analysis
                time_series = []
                for point in data_points:
                    timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                    value = point['value']
                    time_series.append((timestamp, value))
                
                # Perform trend analysis
                trend_analysis = self.statistical_analyzer.detect_trend(
                    time_series, query.confidence_level
                )
                trend_analysis.metric_name = metric_name
                trend_analysis.timeframe = query.timeframe
                
                # Detect seasonality if enough data points
                if len(time_series) >= 48:  # At least 2 days of hourly data
                    seasonal_component = self.statistical_analyzer.detect_seasonality(time_series)
                    trend_analysis.seasonal_component = seasonal_component
                
                trend_analyses.append(trend_analysis)
            
            return trend_analyses
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            return []
    
    async def _calculate_metric_correlations(
        self,
        time_series_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate correlations between different metrics"""
        try:
            if len(time_series_data) < 2:
                return {}
            
            # Align time series data by timestamp
            aligned_data = {}
            
            # Get common timestamps
            all_timestamps = set()
            for metric_data in time_series_data.values():
                for point in metric_data:
                    all_timestamps.add(point['timestamp'])
            
            common_timestamps = sorted(all_timestamps)
            
            # Build aligned data structure
            for metric_name, data_points in time_series_data.items():
                values = []
                data_dict = {point['timestamp']: point['value'] for point in data_points}
                
                for timestamp in common_timestamps:
                    values.append(data_dict.get(timestamp, 0.0))
                
                aligned_data[metric_name] = values
            
            # Calculate correlations
            correlations = self.statistical_analyzer.calculate_correlations(aligned_data)
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Correlation calculation failed: {e}")
            return {}
    
    async def _generate_predictions(
        self,
        query: AnalyticsQuery,
        time_series_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Generate predictions based on historical data"""
        try:
            predictions = {}
            
            for metric_name, data_points in time_series_data.items():
                if len(data_points) < 10:  # Need sufficient data for prediction
                    continue
                
                # Simple linear regression-based prediction
                time_series = []
                for point in data_points:
                    timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                    value = point['value']
                    time_series.append((timestamp, value))
                
                # Use trend analysis for prediction
                trend_analysis = self.statistical_analyzer.detect_trend(time_series)
                
                if trend_analysis.p_value < 0.05:  # Statistically significant trend
                    # Predict next period
                    last_timestamp = time_series[-1][0]
                    
                    if query.timeframe == AnalyticsTimeframe.HOUR:
                        next_timestamp = last_timestamp + timedelta(hours=1)
                    elif query.timeframe == AnalyticsTimeframe.DAY:
                        next_timestamp = last_timestamp + timedelta(days=1)
                    elif query.timeframe == AnalyticsTimeframe.WEEK:
                        next_timestamp = last_timestamp + timedelta(weeks=1)
                    else:
                        next_timestamp = last_timestamp + timedelta(days=30)
                    
                    # Calculate prediction
                    time_delta = (next_timestamp - time_series[0][0]).total_seconds()
                    predicted_value = time_series[0][1] + (trend_analysis.slope * time_delta)
                    
                    # Calculate confidence interval
                    margin = abs(predicted_value * 0.1)  # Simple 10% margin
                    
                    predictions[metric_name] = {
                        'predicted_value': float(predicted_value),
                        'prediction_timestamp': next_timestamp.isoformat(),
                        'confidence_interval': [
                            float(predicted_value - margin),
                            float(predicted_value + margin)
                        ],
                        'trend_strength': trend_analysis.trend_strength,
                        'trend_direction': trend_analysis.trend_direction
                    }
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Prediction generation failed: {e}")
            return {}
    
    async def _generate_insights(
        self,
        report: AnalyticsReport
    ) -> List[Dict[str, Any]]:
        """Generate insights based on analytics results"""
        try:
            insights = []
            
            # Analyze summary metrics for insights
            summary = report.summary_metrics
            
            # Quality insights
            avg_confidence = summary.get('average_confidence_score', 0.0)
            if avg_confidence < 0.5:
                insights.append({
                    'type': 'quality_concern',
                    'priority': 'high',
                    'title': 'Low Average Confidence Score',
                    'description': f'Average confidence score is {avg_confidence:.2f}, indicating potential quality issues.',
                    'metric_value': avg_confidence,
                    'threshold': 0.5
                })
            
            # Activity insights
            activity_rate = summary.get('activity_rate', 0.0)
            if activity_rate < 0.7:
                insights.append({
                    'type': 'activity_concern',
                    'priority': 'medium',
                    'title': 'Low Activity Rate',
                    'description': f'Only {activity_rate:.1%} of fingerprints are active.',
                    'metric_value': activity_rate,
                    'threshold': 0.7
                })
            
            # Storage insights
            storage_gb = summary.get('total_storage_gb', 0.0)
            if storage_gb > 100:  # Example threshold
                insights.append({
                    'type': 'storage_warning',
                    'priority': 'medium',
                    'title': 'High Storage Usage',
                    'description': f'Storage usage is {storage_gb:.2f} GB, consider cleanup policies.',
                    'metric_value': storage_gb,
                    'threshold': 100
                })
            
            # Trend insights
            for trend in report.trend_analyses:
                if trend.trend_strength > 0.7 and trend.p_value < 0.05:
                    insights.append({
                        'type': 'trend_significant',
                        'priority': 'low',
                        'title': f'Strong {trend.trend_direction.title()} Trend in {trend.metric_name.title()}',
                        'description': f'{trend.metric_name} shows a {trend.trend_direction} trend with {trend.trend_strength:.1%} strength.',
                        'metric_value': trend.trend_strength,
                        'trend_direction': trend.trend_direction
                    })
            
            # Correlation insights
            for metric1, correlations in report.correlations.items():
                for metric2, correlation in correlations.items():
                    if abs(correlation) > 0.8:
                        insights.append({
                            'type': 'strong_correlation',
                            'priority': 'low',
                            'title': f'Strong Correlation: {metric1} and {metric2}',
                            'description': f'Strong {"positive" if correlation > 0 else "negative"} correlation ({correlation:.2f}) detected.',
                            'metric_value': correlation,
                            'metrics': [metric1, metric2]
                        })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {e}")
            return []
    
    async def _generate_recommendations(
        self,
        report: AnalyticsReport
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analytics"""
        try:
            recommendations = []
            
            # Quality-based recommendations
            avg_confidence = report.summary_metrics.get('average_confidence_score', 0.0)
            if avg_confidence < 0.5:
                recommendations.append({
                    'type': 'quality_improvement',
                    'priority': 'high',
                    'title': 'Improve Fingerprint Quality',
                    'description': 'Implement quality checks and regenerate low-confidence fingerprints.',
                    'actions': [
                        'Review fingerprint generation algorithms',
                        'Implement quality validation rules',
                        'Consider reprocessing content with low confidence scores'
                    ],
                    'expected_impact': 'Improved match accuracy and system reliability'
                })
            
            # Storage optimization recommendations
            storage_gb = report.summary_metrics.get('total_storage_gb', 0.0)
            if storage_gb > 50:
                recommendations.append({
                    'type': 'storage_optimization',
                    'priority': 'medium',
                    'title': 'Optimize Storage Usage',
                    'description': 'Implement storage optimization strategies to reduce costs.',
                    'actions': [
                        'Enable data compression for old fingerprints',
                        'Archive inactive fingerprints to cold storage',
                        'Implement retention policies for temporary data'
                    ],
                    'expected_impact': f'Potential storage reduction of 20-40% ({storage_gb * 0.3:.1f} GB)'
                })
            
            # Performance recommendations based on trends
            for trend in report.trend_analyses:
                if trend.metric_name == 'creation_rate' and trend.trend_direction == 'increasing' and trend.trend_strength > 0.6:
                    recommendations.append({
                        'type': 'scaling_preparation',
                        'priority': 'medium',
                        'title': 'Prepare for Increased Load',
                        'description': 'Fingerprint creation rate is increasing significantly.',
                        'actions': [
                            'Scale processing infrastructure',
                            'Optimize fingerprint generation algorithms',
                            'Implement caching strategies',
                            'Consider load balancing improvements'
                        ],
                        'expected_impact': 'Maintained performance under increased load'
                    })
            
            # User engagement recommendations
            unique_users = report.summary_metrics.get('unique_users', 0)
            total_fingerprints = report.summary_metrics.get('total_fingerprints', 0)
            
            if unique_users > 0 and total_fingerprints / unique_users < 10:
                recommendations.append({
                    'type': 'user_engagement',
                    'priority': 'low',
                    'title': 'Increase User Engagement',
                    'description': 'Users have relatively few fingerprints on average.',
                    'actions': [
                        'Implement user onboarding improvements',
                        'Add features to encourage content uploads',
                        'Provide analytics dashboard for users',
                        'Implement gamification elements'
                    ],
                    'expected_impact': 'Increased user engagement and platform value'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return []
    
    async def _calculate_data_quality_score(
        self,
        query: AnalyticsQuery
    ) -> float:
        """Calculate overall data quality score"""
        try:
            async with self.db_manager.get_session() as session:
                conditions = self._build_query_conditions(query)
                
                # Total fingerprints
                total_query = select(func.count()).select_from(FingerprintStorageModel)
                if conditions:
                    total_query = total_query.where(and_(*conditions))
                
                total_result = await session.execute(total_query)
                total_fingerprints = total_result.scalar()
                
                if total_fingerprints == 0:
                    return 0.0
                
                quality_score = 0.0
                max_score = 100.0
                
                # Completeness score (40 points)
                completeness_query = select(
                    func.count().label('total'),
                    func.sum(func.case((FingerprintStorageModel.primary_hash.isnot(None), 1), else_=0)).label('has_primary'),
                    func.sum(func.case((FingerprintStorageModel.perceptual_hash.isnot(None), 1), else_=0)).label('has_perceptual'),
                    func.sum(func.case((FingerprintStorageModel.structural_hash.isnot(None), 1), else_=0)).label('has_structural'),
                    func.sum(func.case((FingerprintStorageModel.feature_vector.isnot(None), 1), else_=0)).label('has_vectors')
                ).select_from(FingerprintStorageModel)
                
                if conditions:
                    completeness_query = completeness_query.where(and_(*conditions))
                
                completeness_result = await session.execute(completeness_query)
                completeness_data = completeness_result.first()
                
                if completeness_data and completeness_data.total > 0:
                    completeness_score = (
                        (completeness_data.has_primary / completeness_data.total * 10) +
                        (completeness_data.has_perceptual / completeness_data.total * 10) +
                        (completeness_data.has_structural / completeness_data.total * 10) +
                        (completeness_data.has_vectors / completeness_data.total * 10)
                    )
                    quality_score += completeness_score
                
                # Confidence score (30 points)
                confidence_query = select(func.avg(FingerprintStorageModel.confidence_score)).select_from(FingerprintStorageModel)
                if conditions:
                    confidence_query = confidence_query.where(and_(*conditions))
                
                confidence_result = await session.execute(confidence_query)
                avg_confidence = confidence_result.scalar() or 0.0
                quality_score += avg_confidence * 30
                
                # Freshness score (20 points)
                now = datetime.now(timezone.utc)
                freshness_query = select(
                    func.avg(
                        func.extract('epoch', now - FingerprintStorageModel.created_at) / 86400
                    )
                ).select_from(FingerprintStorageModel)
                
                if conditions:
                    freshness_query = freshness_query.where(and_(*conditions))
                
                freshness_result = await session.execute(freshness_query)
                avg_age_days = freshness_result.scalar() or 0.0
                
                # Fresher data gets higher score (max 20 points for data < 30 days old)
                freshness_score = max(20 - (avg_age_days / 30 * 20), 0)
                quality_score += freshness_score
                
                # Activity score (10 points)
                activity_query = select(func.count()).select_from(FingerprintStorageModel).where(
                    and_(
                        FingerprintStorageModel.status == 'active',
                        *(conditions if conditions else [])
                    )
                )
                
                activity_result = await session.execute(activity_query)
                active_count = activity_result.scalar()
                
                activity_score = (active_count / total_fingerprints) * 10
                quality_score += activity_score
                
                return min(quality_score / max_score, 1.0)
                
        except Exception as e:
            self.logger.error(f"Data quality score calculation failed: {e}")
            return 0.0
    
    # Helper methods
    
    def _build_query_conditions(self, query: AnalyticsQuery) -> List:
        """Build query conditions from AnalyticsQuery"""
        conditions = []
        
        if query.start_date:
            conditions.append(FingerprintStorageModel.created_at >= query.start_date)
        
        if query.end_date:
            conditions.append(FingerprintStorageModel.created_at <= query.end_date)
        
        if query.user_ids:
            conditions.append(FingerprintStorageModel.user_id.in_(query.user_ids))
        
        if query.content_types:
            conditions.append(FingerprintStorageModel.content_type.in_(query.content_types))
        
        if query.quality_levels:
            conditions.append(FingerprintStorageModel.quality_level.in_(query.quality_levels))
        
        return conditions
    
    def _generate_time_intervals(self, query: AnalyticsQuery) -> List[Tuple[datetime, datetime]]:
        """
Generate time intervals for time series analysis"""
        intervals = []
        
        if not query.start_date or not query.end_date:
            return intervals
        
        current = query.start_date
        
        while current < query.end_date:
            if query.timeframe == AnalyticsTimeframe.HOUR:
                next_interval = current + timedelta(hours=1)
            elif query.timeframe == AnalyticsTimeframe.DAY:
                next_interval = current + timedelta(days=1)
            elif query.timeframe == AnalyticsTimeframe.WEEK:
                next_interval = current + timedelta(weeks=1)
            elif query.timeframe == AnalyticsTimeframe.MONTH:
                next_interval = current + timedelta(days=30)
            else:
                next_interval = current + timedelta(days=1)
            
            intervals.append((current, min(next_interval, query.end_date)))
            current = next_interval
        
        return intervals
    
    async def _get_creation_rate_series(
        self,
        session: AsyncSession,
        query: AnalyticsQuery,
        intervals: List[Tuple[datetime, datetime]]
    ) -> List[Dict[str, Any]]:
        """
Get creation rate time series data"""
        series_data = []
        
        for start_time, end_time in intervals:
            conditions = self._build_query_conditions(query)
            conditions.extend([
                FingerprintStorageModel.created_at >= start_time,
                FingerprintStorageModel.created_at < end_time
            ])
            
            count_query = select(func.count()).select_from(FingerprintStorageModel).where(and_(*conditions))
            result = await session.execute(count_query)
            count = result.scalar()
            
            series_data.append({
                'timestamp': start_time.isoformat(),
                'value': count,
                'interval_start': start_time.isoformat(),
                'interval_end': end_time.isoformat()
            })
        
        return series_data
    
    async def _get_match_rate_series(
        self,
        session: AsyncSession,
        query: AnalyticsQuery,
        intervals: List[Tuple[datetime, datetime]]
    ) -> List[Dict[str, Any]]:
        """
Get match rate time series data"""
        series_data = []
        
        for start_time, end_time in intervals:
            match_query = select(func.count()).select_from(FingerprintMatchModel).where(
                and_(
                    FingerprintMatchModel.detected_at >= start_time,
                    FingerprintMatchModel.detected_at < end_time
                )
            )
            
            result = await session.execute(match_query)
            match_count = result.scalar()
            
            series_data.append({
                'timestamp': start_time.isoformat(),
                'value': match_count,
                'interval_start': start_time.isoformat(),
                'interval_end': end_time.isoformat()
            })
        
        return series_data
    
    async def _get_quality_series(
        self,
        session: AsyncSession,
        query: AnalyticsQuery,
        intervals: List[Tuple[datetime, datetime]]
    ) -> List[Dict[str, Any]]:
        """
Get average quality time series data"""
        series_data = []
        
        for start_time, end_time in intervals:
            conditions = self._build_query_conditions(query)
            conditions.extend([
                FingerprintStorageModel.created_at >= start_time,
                FingerprintStorageModel.created_at < end_time
            ])
            
            avg_query = select(func.avg(FingerprintStorageModel.confidence_score)).select_from(FingerprintStorageModel).where(and_(*conditions))
            result = await session.execute(avg_query)
            avg_quality = result.scalar() or 0.0
            
            series_data.append({
                'timestamp': start_time.isoformat(),
                'value': float(avg_quality),
                'interval_start': start_time.isoformat(),
                'interval_end': end_time.isoformat()
            })
        
        return series_data
    
    async def _get_storage_usage_series(
        self,
        session: AsyncSession,
        query: AnalyticsQuery,
        intervals: List[Tuple[datetime, datetime]]
    ) -> List[Dict[str, Any]]:
        """
Get storage usage time series data"""
        series_data = []
        
        for start_time, end_time in intervals:
            conditions = self._build_query_conditions(query)
            conditions.extend([
                FingerprintStorageModel.created_at >= start_time,
                FingerprintStorageModel.created_at < end_time
            ])
            
            size_query = select(func.sum(FingerprintStorageModel.storage_size)).select_from(FingerprintStorageModel).where(and_(*conditions))
            result = await session.execute(size_query)
            total_size = result.scalar() or 0
            
            series_data.append({
                'timestamp': start_time.isoformat(),
                'value': total_size / (1024**3),  # Convert to GB
                'interval_start': start_time.isoformat(),
                'interval_end': end_time.isoformat()
            })
        
        return series_data
    
    async def _get_user_activity_series(
        self,
        session: AsyncSession,
        query: AnalyticsQuery,
        intervals: List[Tuple[datetime, datetime]]
    ) -> List[Dict[str, Any]]:
        """
Get user activity time series data"""
        series_data = []
        
        for start_time, end_time in intervals:
            conditions = self._build_query_conditions(query)
            conditions.extend([
                FingerprintStorageModel.created_at >= start_time,
                FingerprintStorageModel.created_at < end_time
            ])
            
            user_query = select(func.count(func.distinct(FingerprintStorageModel.user_id))).select_from(FingerprintStorageModel).where(and_(*conditions))
            result = await session.execute(user_query)
            active_users = result.scalar()
            
            series_data.append({
                'timestamp': start_time.isoformat(),
                'value': active_users,
                'interval_start': start_time.isoformat(),
                'interval_end': end_time.isoformat()
            })
        
        return series_data
    
    async def _get_confidence_distribution(
        self,
        session: AsyncSession,
        conditions: List
    ) -> Dict[str, int]:
        """
Get confidence score distribution in buckets"""
        # Define confidence buckets
        buckets = {
            '0.0-0.2': 0,
            '0.2-0.4': 0,
            '0.4-0.6': 0,
            '0.6-0.8': 0,
            '0.8-1.0': 0
        }
        
        # Query confidence scores
        confidence_query = select(FingerprintStorageModel.confidence_score).select_from(FingerprintStorageModel)
        if conditions:
            confidence_query = confidence_query.where(and_(*conditions))
        
        result = await session.execute(confidence_query)
        scores = [row[0] for row in result.fetchall() if row[0] is not None]
        
        # Bucket the scores
        for score in scores:
            if score < 0.2:
                buckets['0.0-0.2'] += 1
            elif score < 0.4:
                buckets['0.2-0.4'] += 1
            elif score < 0.6:
                buckets['0.4-0.6'] += 1
            elif score < 0.8:
                buckets['0.6-0.8'] += 1
            else:
                buckets['0.8-1.0'] += 1
        
        return buckets
    
    def _bucket_user_activity(self, user_activity: Dict[str, int]) -> Dict[str, int]:
        """
Bucket user activity into ranges"""
        buckets = {
            '1-5': 0,
            '6-20': 0,
            '21-50': 0,
            '51-100': 0,
            '100+': 0
        }
        
        for count in user_activity.values():
            if count <= 5:
                buckets['1-5'] += 1
            elif count <= 20:
                buckets['6-20'] += 1
            elif count <= 50:
                buckets['21-50'] += 1
            elif count <= 100:
                buckets['51-100'] += 1
            else:
                buckets['100+'] += 1
        
        return buckets
    
    async def health_check(self) -> Dict[str, Any]:
        """
Perform health check on analytics engine"""
        try:
            health = {
                "status": "healthy",
                "components": {},
                "capabilities": []
            }
            
            # Test database connectivity
            try:
                async with self.db_manager.get_session() as session:
                    result = await session.execute(text("SELECT 1"))
                    result.scalar()
                health["components"]["database"] = "healthy"
            except Exception as e:
                health["components"]["database"] = f"unhealthy: {e}"
                health["status"] = "degraded"
            
            # Test statistical analyzer
            try:
                test_series = [(datetime.now(), 1.0), (datetime.now(), 2.0)]
                self.statistical_analyzer.detect_trend(test_series)
                health["components"]["statistical_analyzer"] = "healthy"
            except Exception as e:
                health["components"]["statistical_analyzer"] = f"unhealthy: {e}"
                health["status"] = "degraded"
            
            # List capabilities
            health["capabilities"] = [
                "trend_analysis",
                "correlation_analysis",
                "prediction_generation",
                "quality_scoring",
                "insight_generation",
                "recommendation_engine"
            ]
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
