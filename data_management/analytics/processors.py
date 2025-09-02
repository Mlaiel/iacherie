"""Analytics Data Processors - Advanced Data Processing Pipeline
============================================================

Comprehensive data processing system for analytics metrics transformation,
aggregation, trend analysis, and predictive modeling.

Features:
- Real-time metrics processing and aggregation
- Trend analysis and pattern recognition
- Anomaly detection using ML algorithms
- Predictive analytics and forecasting
- Performance optimization recommendations

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from ..core.database import get_database_session


class ProcessingType(Enum):
    """
Data processing types."""

    AGGREGATION = "aggregation"
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTION = "prediction"
    OPTIMIZATION = "optimization"


class TimeGranularity(Enum):
    """Time aggregation granularity."""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class ProcessedMetric:
    """Processed analytics metric data."""
    metric_name: str
    original_value: float
    processed_value: float
    processing_type: ProcessingType
    confidence_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """
Trend analysis results."""
    metric_name: str
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: float  # 0-100
    correlation_coefficient: float
    seasonal_pattern: Optional[str]
    forecast_values: List[float]
    anomalies_detected: List[datetime]
    recommendations: List[str]


class MetricsProcessor:
    """
    Advanced metrics processing and transformation engine.
    
    Handles real-time aggregation, cleaning, and preparation
    of analytics data for analysis and reporting.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._processing_cache = {}
        
    async def process_metrics_batch(
        self,
        metrics: List[Dict[str, Any]],
        processing_types: List[ProcessingType]
    ) -> List[ProcessedMetric]:
        """
        Process batch of metrics with specified processing types.
        
        Args:
            metrics: Raw metrics data
            processing_types: Types of processing to apply
            
        Returns:
            List of processed metrics
        """
        try:
            processed_metrics = []
            
            # Convert to DataFrame for efficient processing
            df = pd.DataFrame(metrics)
            
            if df.empty:
                return processed_metrics
                
            # Apply each processing type
            for processing_type in processing_types:
                if processing_type == ProcessingType.AGGREGATION:
                    aggregated = await self._aggregate_metrics(df)
                    processed_metrics.extend(aggregated)
                    
                elif processing_type == ProcessingType.TREND_ANALYSIS:
                    trends = await self._analyze_trends(df)
                    processed_metrics.extend(trends)
                    
                elif processing_type == ProcessingType.ANOMALY_DETECTION:
                    anomalies = await self._detect_anomalies(df)
                    processed_metrics.extend(anomalies)
                    
                elif processing_type == ProcessingType.PREDICTION:
                    predictions = await self._generate_predictions(df)
                    processed_metrics.extend(predictions)
                    
                elif processing_type == ProcessingType.OPTIMIZATION:
                    optimizations = await self._optimize_metrics(df)
                    processed_metrics.extend(optimizations)
                    
            self.logger.info(f"Processed {len(processed_metrics)} metrics")
            return processed_metrics
            
        except Exception as e:
            self.logger.error(f"Error processing metrics batch: {e}")
            raise
            
    async def _aggregate_metrics(self, df: pd.DataFrame) -> List[ProcessedMetric]:
        """Aggregate metrics by time granularity."""
        
        processed = []
        
        if 'timestamp' not in df.columns or 'value' not in df.columns:
            return processed
            
        # Convert timestamp column
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Aggregate by different granularities
        granularities = {
            TimeGranularity.HOUR: 'H',
            TimeGranularity.DAY: 'D', 
            TimeGranularity.WEEK: 'W',
            TimeGranularity.MONTH: 'M'
        }
        
        for granularity, freq in granularities.items():
            try:
                # Group by metric name and time period
                for metric_name in df['metric_name'].unique():
                    metric_data = df[df['metric_name'] == metric_name]
                    
                    # Aggregate by time period
                    aggregated = metric_data.groupby(pd.Grouper(freq=freq)).agg({
                        'value': ['sum', 'mean', 'count', 'std', 'min', 'max']
                    }).fillna(0)
                    
                    # Create processed metrics
                    for timestamp, row in aggregated.iterrows():
                        if pd.notna(timestamp):
                            processed.append(
                                ProcessedMetric(
                                    metric_name=f"{metric_name}_{granularity.value}_sum",
                                    original_value=float(row[('value', 'sum')]),
                                    processed_value=float(row[('value', 'sum')]),
                                    processing_type=ProcessingType.AGGREGATION,
                                    confidence_score=95.0,
                                    timestamp=timestamp.to_pydatetime(),
                                    metadata={
                                        'granularity': granularity.value,
                                        'count': int(row[('value', 'count')]),
                                        'mean': float(row[('value', 'mean')]),
                                        'std': float(row[('value', 'std')]),
                                        'min': float(row[('value', 'min')]),
                                        'max': float(row[('value', 'max')])
                                    }
                                )
                            )
                            
            except Exception as e:
                self.logger.warning(f"Error aggregating {granularity}: {e}")
                continue
                
        return processed
        
    async def _analyze_trends(self, df: pd.DataFrame) -> List[ProcessedMetric]:
        """Analyze trends in metrics data."""
        
        processed = []
        
        if 'timestamp' not in df.columns or 'value' not in df.columns:
            return processed
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Analyze trends for each metric
        for metric_name in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric_name].copy()
            metric_data = metric_data.sort_values('timestamp')
            
            if len(metric_data) < 3:
                continue
                
            try:
                # Calculate trend using linear regression
                X = np.arange(len(metric_data)).reshape(-1, 1)
                y = metric_data['value'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Trend direction and strength
                slope = model.coef_[0]
                r_squared = model.score(X, y)
                
                if slope > 0.1:
                    trend_direction = "increasing"
                elif slope < -0.1:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
                    
                trend_strength = min(abs(slope) * 100, 100)
                
                # Detect seasonality
                seasonal_pattern = self._detect_seasonality(metric_data)
                
                # Generate forecast
                future_periods = 7  # 7 future points
                future_X = np.arange(len(metric_data), len(metric_data) + future_periods).reshape(-1, 1)
                forecast = model.predict(future_X)
                
                processed.append(
                    ProcessedMetric(
                        metric_name=f"{metric_name}_trend_slope",
                        original_value=0.0,
                        processed_value=slope,
                        processing_type=ProcessingType.TREND_ANALYSIS,
                        confidence_score=r_squared * 100,
                        timestamp=datetime.now(),
                        metadata={
                            'trend_direction': trend_direction,
                            'trend_strength': trend_strength,
                            'r_squared': r_squared,
                            'seasonal_pattern': seasonal_pattern,
                            'forecast': forecast.tolist()
                        }
                    )
                )
                
            except Exception as e:
                self.logger.warning(f"Error analyzing trend for {metric_name}: {e}")
                continue
                
        return processed
        
    def _detect_seasonality(self, data: pd.DataFrame) -> Optional[str]:
        """Detect seasonal patterns in time series data."""
        
        if len(data) < 24:  # Need at least 24 points for daily seasonality
            return None
            
        try:
            # Simple seasonality detection using autocorrelation
            values = data['value'].values
            
            # Check for daily pattern (24 points)
            if len(values) >= 24:
                autocorr_24 = np.corrcoef(values[:-24], values[24:])[0, 1]
                if autocorr_24 > 0.7:
                    return "daily"
                    
            # Check for weekly pattern (7 days if daily data)
            if len(values) >= 7:
                autocorr_7 = np.corrcoef(values[:-7], values[7:])[0, 1]
                if autocorr_7 > 0.7:
                    return "weekly"
                    
            return "none"
            
        except Exception:
            return None
            
    async def _detect_anomalies(self, df: pd.DataFrame) -> List[ProcessedMetric]:
        """Detect anomalies in metrics data using ML."""
        
        processed = []
        
        if 'value' not in df.columns:
            return processed
            
        # Detect anomalies for each metric
        for metric_name in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric_name].copy()
            
            if len(metric_data) < 10:  # Need sufficient data
                continue
                
            try:
                # Prepare data for anomaly detection
                values = metric_data['value'].values.reshape(-1, 1)
                
                # Use Isolation Forest for anomaly detection
                iso_forest = IsolationForest(
                    contamination=0.1,  # Expect 10% anomalies
                    random_state=42
                )
                
                anomaly_labels = iso_forest.fit_predict(values)
                anomaly_scores = iso_forest.score_samples(values)
                
                # Create processed metrics for anomalies
                anomaly_count = np.sum(anomaly_labels == -1)
                anomaly_percentage = (anomaly_count / len(values)) * 100
                
                # Find most anomalous points
                anomalous_indices = np.where(anomaly_labels == -1)[0]
                anomalous_values = []
                anomalous_timestamps = []
                
                for idx in anomalous_indices:
                    anomalous_values.append(float(values[idx][0]))
                    anomalous_timestamps.append(
                        metric_data.iloc[idx]['timestamp'].isoformat()
                        if 'timestamp' in metric_data.columns else None
                    )
                    
                processed.append(
                    ProcessedMetric(
                        metric_name=f"{metric_name}_anomaly_score",
                        original_value=0.0,
                        processed_value=anomaly_percentage,
                        processing_type=ProcessingType.ANOMALY_DETECTION,
                        confidence_score=85.0,
                        timestamp=datetime.now(),
                        metadata={
                            'anomaly_count': anomaly_count,
                            'total_points': len(values),
                            'anomalous_values': anomalous_values,
                            'anomalous_timestamps': anomalous_timestamps,
                            'mean_anomaly_score': float(np.mean(anomaly_scores[anomaly_labels == -1]))
                            if anomaly_count > 0 else 0.0
                        }
                    )
                )
                
            except Exception as e:
                self.logger.warning(f"Error detecting anomalies for {metric_name}: {e}")
                continue
                
        return processed
        
    async def _generate_predictions(self, df: pd.DataFrame) -> List[ProcessedMetric]:
        """Generate predictions for metrics using ML models."""
        
        processed = []
        
        if 'timestamp' not in df.columns or 'value' not in df.columns:
            return processed
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Generate predictions for each metric
        for metric_name in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric_name].copy()
            metric_data = metric_data.sort_values('timestamp')
            
            if len(metric_data) < 5:
                continue
                
            try:
                # Prepare features (time-based)
                metric_data['time_numeric'] = (
                    metric_data['timestamp'] - metric_data['timestamp'].min()
                ).dt.total_seconds()
                
                X = metric_data[['time_numeric']].values
                y = metric_data['value'].values
                
                # Train prediction model
                model = LinearRegression()
                model.fit(X, y)
                
                # Generate predictions for next periods
                last_time = metric_data['time_numeric'].iloc[-1]
                time_step = (last_time - metric_data['time_numeric'].iloc[-2]) if len(metric_data) > 1 else 3600
                
                prediction_periods = 5
                future_times = []
                predictions = []
                
                for i in range(1, prediction_periods + 1):
                    future_time = last_time + (time_step * i)
                    future_times.append(future_time)
                    
                prediction_X = np.array(future_times).reshape(-1, 1)
                predictions = model.predict(prediction_X)
                
                # Calculate prediction confidence
                model_score = model.score(X, y)
                confidence = model_score * 100
                
                # Create prediction metric
                next_value_prediction = predictions[0] if len(predictions) > 0 else 0.0
                
                processed.append(
                    ProcessedMetric(
                        metric_name=f"{metric_name}_prediction_next",
                        original_value=metric_data['value'].iloc[-1],
                        processed_value=next_value_prediction,
                        processing_type=ProcessingType.PREDICTION,
                        confidence_score=confidence,
                        timestamp=datetime.now(),
                        metadata={
                            'model_score': model_score,
                            'prediction_horizon': prediction_periods,
                            'all_predictions': predictions.tolist(),
                            'trend_coefficient': float(model.coef_[0])
                        }
                    )
                )
                
            except Exception as e:
                self.logger.warning(f"Error generating predictions for {metric_name}: {e}")
                continue
                
        return processed
        
    async def _optimize_metrics(self, df: pd.DataFrame) -> List[ProcessedMetric]:
        """Generate optimization recommendations for metrics."""
        
        processed = []
        
        if 'value' not in df.columns:
            return processed
            
        # Analyze each metric for optimization opportunities
        for metric_name in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric_name]
            
            if len(metric_data) < 3:
                continue
                
            try:
                values = metric_data['value'].values
                
                # Calculate optimization metrics
                current_value = values[-1] if len(values) > 0 else 0
                mean_value = np.mean(values)
                max_value = np.max(values)
                min_value = np.min(values)
                std_value = np.std(values)
                
                # Performance score (0-100)
                if max_value > min_value:
                    performance_score = ((current_value - min_value) / (max_value - min_value)) * 100
                else:
                    performance_score = 100.0
                    
                # Consistency score (lower std is better)
                consistency_score = max(100 - (std_value / max(mean_value, 1)) * 100, 0)
                
                # Optimization potential
                optimization_potential = max_value - current_value
                optimization_percentage = (optimization_potential / max(current_value, 1)) * 100
                
                # Generate recommendations
                recommendations = []
                if performance_score < 50:
                    recommendations.append("Performance below average - investigate root causes")
                if consistency_score < 70:
                    recommendations.append("High variability detected - stabilize processes")
                if optimization_percentage > 20:
                    recommendations.append("Significant optimization potential available")
                    
                processed.append(
                    ProcessedMetric(
                        metric_name=f"{metric_name}_optimization_score",
                        original_value=current_value,
                        processed_value=performance_score,
                        processing_type=ProcessingType.OPTIMIZATION,
                        confidence_score=90.0,
                        timestamp=datetime.now(),
                        metadata={
                            'performance_score': performance_score,
                            'consistency_score': consistency_score,
                            'optimization_potential': optimization_potential,
                            'optimization_percentage': optimization_percentage,
                            'recommendations': recommendations,
                            'statistics': {
                                'mean': mean_value,
                                'max': max_value,
                                'min': min_value,
                                'std': std_value
                            }
                        }
                    )
                )
                
            except Exception as e:
                self.logger.warning(f"Error optimizing {metric_name}: {e}")
                continue
                
        return processed


class TrendAnalyzer:
    """
    Advanced trend analysis system for identifying patterns
    and predicting future metric behavior.
    """
    
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
    async def analyze_metric_trends(
        self,
        metrics_data: List[Dict[str, Any]],
        time_window: timedelta = timedelta(days=30)
    ) -> List[TrendAnalysis]:
        """
        Analyze trends in metrics data over specified time window.
        
        Args:
            metrics_data: Historical metrics data
            time_window: Analysis time window
            
        Returns:
            List of trend analysis results
        """
        try:
            df = pd.DataFrame(metrics_data)
            
            if df.empty:
                return []
                
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter by time window
            cutoff_date = datetime.now() - time_window
            df = df[df['timestamp'] >= cutoff_date]
            
            trend_analyses = []
            
            # Analyze trends for each metric
            for metric_name in df['metric_name'].unique():
                analysis = await self._analyze_single_metric_trend(df, metric_name)
                if analysis:
                    trend_analyses.append(analysis)
                    
            self.logger.info(f"Analyzed trends for {len(trend_analyses)} metrics")
            return trend_analyses
            
        except Exception as e:
            self.logger.error(f"Error analyzing metric trends: {e}")
            raise
            
    async def _analyze_single_metric_trend(
        self,
        df: pd.DataFrame,
        metric_name: str
    ) -> Optional[TrendAnalysis]:
        """Analyze trend for a single metric."""
        
        try:
            metric_data = df[df['metric_name'] == metric_name].copy()
            metric_data = metric_data.sort_values('timestamp')
            
            if len(metric_data) < 3:
                return None
                
            # Prepare data for analysis
            metric_data['time_numeric'] = (
                metric_data['timestamp'] - metric_data['timestamp'].min()
            ).dt.total_seconds()
            
            X = metric_data['time_numeric'].values.reshape(-1, 1)
            y = metric_data['value'].values
            
            # Fit trend line
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            r_squared = model.score(X, y)
            
            # Determine trend direction
            if slope > 0.01:
                trend_direction = "increasing"
            elif slope < -0.01:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
                
            # Calculate trend strength
            trend_strength = min(abs(slope) * 100, 100)
            
            # Detect seasonal pattern
            seasonal_pattern = self._detect_advanced_seasonality(metric_data)
            
            # Generate forecast
            forecast_periods = 7
            last_time = metric_data['time_numeric'].iloc[-1]
            time_step = (
                (last_time - metric_data['time_numeric'].iloc[-2])
                if len(metric_data) > 1 else 86400  # 1 day default
            )
            
            future_times = []
            for i in range(1, forecast_periods + 1):
                future_times.append(last_time + (time_step * i))
                
            forecast_X = np.array(future_times).reshape(-1, 1)
            forecast_values = model.predict(forecast_X).tolist()
            
            # Detect anomalies
            anomalies = self._detect_trend_anomalies(metric_data)
            
            # Generate recommendations
            recommendations = self._generate_trend_recommendations(
                trend_direction, trend_strength, r_squared, seasonal_pattern
            )
            
            return TrendAnalysis(
                metric_name=metric_name,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                correlation_coefficient=r_squared,
                seasonal_pattern=seasonal_pattern,
                forecast_values=forecast_values,
                anomalies_detected=anomalies,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.warning(f"Error analyzing trend for {metric_name}: {e}")
            return None
            
    def _detect_advanced_seasonality(self, data: pd.DataFrame) -> Optional[str]:
        """Detect seasonal patterns using advanced methods."""
        
        if len(data) < 14:
            return None
            
        try:
            values = data['value'].values
            
            # Check different seasonal patterns
            patterns = {
                'hourly': 24,
                'daily': 7,
                'weekly': 4,
                'monthly': 12
            }
            
            best_pattern = None
            best_correlation = 0
            
            for pattern_name, period in patterns.items():
                if len(values) >= period * 2:
                    # Calculate autocorrelation at the seasonal lag
                    correlation = np.corrcoef(
                        values[:-period], values[period:]
        try:
            logger.info(f"Executing _detect_trend_anomalies")
            
            # Implementation for _detect_trend_anomalies
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_detect_trend_anomalies completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_detect_trend_anomalies failed: {e}")
            raise
            for i, (value, mean, std) in enumerate(zip(values, rolling_mean, rolling_std)):
                if pd.notna(mean) and pd.notna(std) and std > 0:
                    z_score = abs(value - mean) / std
                    if z_score > 2:
                        anomalies.append(data.iloc[i]['timestamp'])
                        
        except Exception:
            pass
            
        return anomalies
        
    def _generate_trend_recommendations(
        self,
        direction: str,
        strength: float,
        correlation: float,
        seasonality: Optional[str]
    ) -> List[str]:
        """
Generate actionable recommendations based on trend analysis."""
        
        recommendations = []
        
        if direction == "decreasing" and strength > 30:
            recommendations.append("Declining trend detected - investigate causes and implement corrective measures")
            
        if direction == "increasing" and strength > 30:
            recommendations.append("Positive trend identified - capitalize on growth opportunities")
            
        if correlation < 0.5:
            recommendations.append("Low trend predictability - increase data collection frequency")
            
        if seasonality:
            recommendations.append(f"Seasonal {seasonality} pattern detected - plan resource allocation accordingly")
            
        if strength < 10:
            recommendations.append("Stable metric - monitor for unexpected changes")
            
        return recommendations


class AnomalyDetector:
    """
    Advanced anomaly detection system using multiple ML algorithms
    for comprehensive outlier identification.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._models = {}
        
    async def detect_anomalies(
        self,
        metrics_data: List[Dict[str, Any]],
        sensitivity: float = 0.1
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect anomalies in metrics data using ensemble methods.
        
        Args:
            metrics_data: Metrics data to analyze
            sensitivity: Anomaly detection sensitivity (0.0-1.0)
            
        Returns:
            Dictionary of anomalies by metric name
        """
        try:
            df = pd.DataFrame(metrics_data)
            
            if df.empty:
                return {}
                
            anomalies_by_metric = {}
            
            # Detect anomalies for each metric
            for metric_name in df['metric_name'].unique():
                metric_anomalies = await self._detect_metric_anomalies(
                    df, metric_name, sensitivity
                )
                if metric_anomalies:
                    anomalies_by_metric[metric_name] = metric_anomalies
                    
            self.logger.info(f"Detected anomalies in {len(anomalies_by_metric)} metrics")
            return anomalies_by_metric
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            raise
            
    async def _detect_metric_anomalies(
        self,
        df: pd.DataFrame,
        metric_name: str,
        sensitivity: float
    ) -> List[Dict[str, Any]]:
        """Detect anomalies for a specific metric."""
        
        try:
            metric_data = df[df['metric_name'] == metric_name].copy()
            
            if len(metric_data) < 10:
                return []
                
            values = metric_data['value'].values
            timestamps = metric_data.get('timestamp', [])
            
            # Multiple anomaly detection methods
            isolation_anomalies = self._isolation_forest_detection(values, sensitivity)
            statistical_anomalies = self._statistical_detection(values, sensitivity)
            
            # Combine results
            combined_anomalies = []
            
            for i, (iso_anomaly, stat_anomaly) in enumerate(
                zip(isolation_anomalies, statistical_anomalies)
            ):
                if iso_anomaly or stat_anomaly:
                    anomaly_info = {
                        'index': i,
                        'value': float(values[i]),
                        'timestamp': timestamps[i] if len(timestamps) > i else None,
                        'isolation_forest': iso_anomaly,
                        'statistical': stat_anomaly,
                        'confidence': self._calculate_anomaly_confidence(
                            values[i], values, iso_anomaly, stat_anomaly
                        )
                    }
                    combined_anomalies.append(anomaly_info)
                    
            return combined_anomalies
            
        except Exception as e:
            self.logger.warning(f"Error detecting anomalies for {metric_name}: {e}")
            return []
            
    def _isolation_forest_detection(
        self,
        values: np.ndarray,
        sensitivity: float
    ) -> List[bool]:
        """Detect anomalies using Isolation Forest."""
        
        try:
            iso_forest = IsolationForest(
                contamination=sensitivity,
                random_state=42
            )
            
            predictions = iso_forest.fit_predict(values.reshape(-1, 1))
            return [pred == -1 for pred in predictions]
            
        except Exception:
            return [False] * len(values)
            
    def _statistical_detection(
        self,
        values: np.ndarray,
        sensitivity: float
    ) -> List[bool]:
        """
Detect anomalies using statistical methods."""
        
        try:
            # Use modified Z-score method
            median = np.median(values)
            mad = np.median(np.abs(values - median))
            
            if mad == 0:
                return [False] * len(values)
                
            modified_z_scores = 0.6745 * (values - median) / mad
            threshold = 3.5 * (1 - sensitivity)  # Adjust threshold based on sensitivity
            
            return [abs(score) > threshold for score in modified_z_scores]
            
        except Exception:
            return [False] * len(values)
            
    def _calculate_anomaly_confidence(
        self,
        value: float,
        all_values: np.ndarray,
        iso_result: bool,
        stat_result: bool
    ) -> float:
        """
Calculate confidence score for anomaly detection."""
        
        confidence = 0.0
        
        if iso_result:
            confidence += 50.0
        if stat_result:
            confidence += 50.0
            
        # Adjust based on how extreme the value is
        if len(all_values) > 1:
            mean = np.mean(all_values)
            std = np.std(all_values)
            
            if std > 0:
                z_score = abs(value - mean) / std
                extremeness_bonus = min(z_score * 5, 20)
                confidence += extremeness_bonus
                
        return min(confidence, 100.0)
