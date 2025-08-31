"""
Revenue Analysis Engine - Advanced revenue data analysis and insights generation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

  STRICT COPYRIGHT WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
import uuid

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN

from ..utils.exceptions import RevenueAnalysisError
from ..utils.validators import validate_analysis_data
from ..utils.cache import cache_revenue_analysis

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Revenue analysis types"""
    TREND_ANALYSIS = "trend_analysis"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    SEASONALITY_ANALYSIS = "seasonality_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    COHORT_ANALYSIS = "cohort_analysis"
    SEGMENTATION_ANALYSIS = "segmentation_analysis"


class TrendDirection(Enum):
    """Trend direction classifications"""
    STRONG_UPWARD = "strong_upward"
    MODERATE_UPWARD = "moderate_upward"
    SLIGHT_UPWARD = "slight_upward"
    STABLE = "stable"
    SLIGHT_DOWNWARD = "slight_downward"
    MODERATE_DOWNWARD = "moderate_downward"
    STRONG_DOWNWARD = "strong_downward"


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    direction: TrendDirection
    slope: float
    r_squared: float
    confidence_level: float
    trend_strength: float
    inflection_points: List[datetime]
    growth_rate: float
    volatility: float
    
    @property
    def is_significant(self) -> bool:
        """Check if trend is statistically significant"""



        return self.confidence_level >= 0.95 and abs(self.slope) > 0.1


@dataclass
class AnalysisReport:
    """Comprehensive analysis report"""
    report_id: str
    analysis_type: AnalysisType
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    key_insights: List[str]
    trends: Dict[str, TrendAnalysis]
    correlations: Dict[str, float]
    anomalies: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SeasonalityPattern:
    """Seasonality pattern analysis"""
    pattern_type: str  # daily, weekly, monthly, yearly
    strength: float
    peak_periods: List[str]
    low_periods: List[str]
    amplitude: float
    phase_shift: float


@dataclass
class PerformanceMetric:
    """Performance metric analysis"""
    metric_name: str
    current_value: float
    baseline_value: float
    change_percentage: float
    percentile_rank: float
    benchmark_comparison: str


class RevenueAnalyzer:
    """Advanced revenue analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.analysis_history = []
        self.cached_reports = {}
        
    async def initialize(self) -> None:
        """Initialize revenue analyzer"""



        try:
            # Setup analysis configuration
            self.analysis_config = self.config.get('analysis', {
                'confidence_threshold': 0.95,
                'anomaly_threshold': 2.0,
                'trend_window': 30,
                'seasonality_periods': [7, 30, 365]
            })
            
            logger.info("Revenue analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing revenue analyzer: {e}")
            raise
    
    @cache_revenue_analysis
    async def analyze_revenue_trends(self, data: pd.DataFrame, period: str = 'daily') -> TrendAnalysis:
        """Analyze revenue trends"""



        try:
            validate_analysis_data(data)
            
            # Ensure data is sorted by date
            data = data.sort_values('date')
            
            # Prepare time series data
            if period == 'daily':
                time_series = data.groupby('date')['revenue'].sum()
            elif period == 'weekly':
                data['week'] = data['date'].dt.to_period('W')
                time_series = data.groupby('week')['revenue'].sum()
            elif period == 'monthly':
                data['month'] = data['date'].dt.to_period('M')
                time_series = data.groupby('month')['revenue'].sum()
            else:
                time_series = data.groupby('date')['revenue'].sum()
            
            # Convert to numeric array
            revenue_values = time_series.values
            x_values = np.arange(len(revenue_values))
            
            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, revenue_values)
            
            # Determine trend direction
            if slope > 0.1 and r_value ** 2 > 0.7:
                if slope > 0.5:
                    direction = TrendDirection.STRONG_UPWARD
                elif slope > 0.3:
                    direction = TrendDirection.MODERATE_UPWARD
                else:
                    direction = TrendDirection.SLIGHT_UPWARD
            elif slope < -0.1 and r_value ** 2 > 0.7:
                if slope < -0.5:
                    direction = TrendDirection.STRONG_DOWNWARD
                elif slope < -0.3:
                    direction = TrendDirection.MODERATE_DOWNWARD
                else:
                    direction = TrendDirection.SLIGHT_DOWNWARD
            else:
                direction = TrendDirection.STABLE
            
            # Calculate trend strength
            trend_strength = abs(slope) * (r_value ** 2)
            
            # Find inflection points
            inflection_points = await self._find_inflection_points(time_series)
            
            # Calculate growth rate
            if len(revenue_values) > 1:
                growth_rate = ((revenue_values[-1] / revenue_values[0]) ** (1 / len(revenue_values)) - 1) * 100
            else:
                growth_rate = 0.0
            
            # Calculate volatility
            returns = np.diff(revenue_values) / revenue_values[:-1]
            volatility = np.std(returns) * 100 if len(returns) > 0 else 0.0
            
            # Confidence level
            confidence_level = 1 - p_value if p_value < 1 else 0.0
            
            return TrendAnalysis(
                direction=direction,
                slope=slope,
                r_squared=r_value ** 2,
                confidence_level=confidence_level,
                trend_strength=trend_strength,
                inflection_points=inflection_points,
                growth_rate=growth_rate,
                volatility=volatility
            )
            
        except Exception as e:
            logger.error(f"Error analyzing revenue trends: {e}")
            raise RevenueAnalysisError(f"Trend analysis failed: {e}")
    
    async def _find_inflection_points(self, time_series: pd.Series) -> List[datetime]:
        """Find inflection points in time series"""



        try:
            # Calculate second derivative
            values = time_series.values
            first_diff = np.diff(values)
            second_diff = np.diff(first_diff)
            
            # Find sign changes in second derivative
            sign_changes = np.where(np.diff(np.sign(second_diff)))[0]
            
            # Convert to datetime
            inflection_points = []
            for idx in sign_changes:
                if idx + 2 < len(time_series.index):
                    date = time_series.index[idx + 2]
                    if hasattr(date, 'to_timestamp'):
                        date = date.to_timestamp()
                    inflection_points.append(date)
            
            return inflection_points
            
        except Exception as e:
            logger.error(f"Error finding inflection points: {e}")
            return []
    
    async def analyze_seasonality(self, data: pd.DataFrame) -> List[SeasonalityPattern]:
        """Analyze seasonality patterns"""



        try:
            patterns = []
            
            # Ensure datetime index
            data = data.copy()
            data['date'] = pd.to_datetime(data['date'])
            
            # Weekly seasonality
            weekly_pattern = await self._analyze_weekly_seasonality(data)
            if weekly_pattern:
                patterns.append(weekly_pattern)
            
            # Monthly seasonality
            monthly_pattern = await self._analyze_monthly_seasonality(data)
            if monthly_pattern:
                patterns.append(monthly_pattern)
            
            # Yearly seasonality (if enough data)
            if len(data) > 365:
                yearly_pattern = await self._analyze_yearly_seasonality(data)
                if yearly_pattern:
                    patterns.append(yearly_pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing seasonality: {e}")
            raise RevenueAnalysisError(f"Seasonality analysis failed: {e}")
    
    async def _analyze_weekly_seasonality(self, data: pd.DataFrame) -> Optional[SeasonalityPattern]:
        """Analyze weekly seasonality pattern"""



        try:
            data['weekday'] = data['date'].dt.day_name()
            weekly_avg = data.groupby('weekday')['revenue'].mean()
            
            # Calculate seasonality strength
            overall_mean = data['revenue'].mean()
            deviations = abs(weekly_avg - overall_mean)
            strength = (deviations.mean() / overall_mean) if overall_mean > 0 else 0
            
            if strength > 0.1:  # Significant seasonality threshold
                peak_days = weekly_avg.nlargest(2).index.tolist()
                low_days = weekly_avg.nsmallest(2).index.tolist()
                amplitude = (weekly_avg.max() - weekly_avg.min()) / overall_mean
                
                return SeasonalityPattern(
                    pattern_type="weekly",
                    strength=strength,
                    peak_periods=peak_days,
                    low_periods=low_days,
                    amplitude=amplitude,
                    phase_shift=0.0
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing weekly seasonality: {e}")
            return None
    
    async def _analyze_monthly_seasonality(self, data: pd.DataFrame) -> Optional[SeasonalityPattern]:
        """Analyze monthly seasonality pattern"""



        try:
            data['month'] = data['date'].dt.month_name()
            monthly_avg = data.groupby('month')['revenue'].mean()
            
            # Calculate seasonality strength
            overall_mean = data['revenue'].mean()
            deviations = abs(monthly_avg - overall_mean)
            strength = (deviations.mean() / overall_mean) if overall_mean > 0 else 0
            
            if strength > 0.15:  # Significant seasonality threshold
                peak_months = monthly_avg.nlargest(3).index.tolist()
                low_months = monthly_avg.nsmallest(3).index.tolist()
                amplitude = (monthly_avg.max() - monthly_avg.min()) / overall_mean
                
                return SeasonalityPattern(
                    pattern_type="monthly",
                    strength=strength,
                    peak_periods=peak_months,
                    low_periods=low_months,
                    amplitude=amplitude,
                    phase_shift=0.0
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing monthly seasonality: {e}")
            return None
    
    async def _analyze_yearly_seasonality(self, data: pd.DataFrame) -> Optional[SeasonalityPattern]:
        """Analyze yearly seasonality pattern"""



        try:
            data['quarter'] = data['date'].dt.quarter
            quarterly_avg = data.groupby('quarter')['revenue'].mean()
            
            # Calculate seasonality strength
            overall_mean = data['revenue'].mean()
            deviations = abs(quarterly_avg - overall_mean)
            strength = (deviations.mean() / overall_mean) if overall_mean > 0 else 0
            
            if strength > 0.2:  # Significant seasonality threshold
                peak_quarters = [f"Q{q}" for q in quarterly_avg.nlargest(2).index.tolist()]
                low_quarters = [f"Q{q}" for q in quarterly_avg.nsmallest(2).index.tolist()]
                amplitude = (quarterly_avg.max() - quarterly_avg.min()) / overall_mean
                
                return SeasonalityPattern(
                    pattern_type="yearly",
                    strength=strength,
                    peak_periods=peak_quarters,
                    low_periods=low_quarters,
                    amplitude=amplitude,
                    phase_shift=0.0
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing yearly seasonality: {e}")
            return None
    
    async def detect_revenue_anomalies(self, data: pd.DataFrame, method: str = 'iqr') -> List[Dict[str, Any]]:
        """Detect revenue anomalies"""



        try:
            anomalies = []
            
            if method == 'iqr':
                anomalies = await self._detect_iqr_anomalies(data)
            elif method == 'zscore':
                anomalies = await self._detect_zscore_anomalies(data)
            elif method == 'isolation_forest':
                anomalies = await self._detect_isolation_forest_anomalies(data)
            else:
                # Use multiple methods and combine results
                iqr_anomalies = await self._detect_iqr_anomalies(data)
                zscore_anomalies = await self._detect_zscore_anomalies(data)
                
                # Combine and deduplicate
                all_anomalies = iqr_anomalies + zscore_anomalies
                seen_dates = set()
                for anomaly in all_anomalies:
                    date_key = anomaly['date']
                    if date_key not in seen_dates:
                        anomalies.append(anomaly)
                        seen_dates.add(date_key)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise RevenueAnalysisError(f"Anomaly detection failed: {e}")
    
    async def _detect_iqr_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using IQR method"""



        try:
            Q1 = data['revenue'].quantile(0.25)
            Q3 = data['revenue'].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            anomalies = []
            anomaly_mask = (data['revenue'] < lower_bound) | (data['revenue'] > upper_bound)
            
            for idx, row in data[anomaly_mask].iterrows():
                anomaly_type = 'high' if row['revenue'] > upper_bound else 'low'
                severity = 'moderate'
                
                # Calculate severity
                if anomaly_type == 'high':
                    if row['revenue'] > Q3 + 3 * IQR:
                        severity = 'extreme'
                    elif row['revenue'] > Q3 + 2 * IQR:
                        severity = 'high'
                else:
                    if row['revenue'] < Q1 - 3 * IQR:
                        severity = 'extreme'
                    elif row['revenue'] < Q1 - 2 * IQR:
                        severity = 'high'
                
                anomalies.append({
                    'date': row['date'],
                    'revenue': float(row['revenue']),
                    'type': anomaly_type,
                    'severity': severity,
                    'method': 'iqr',
                    'score': abs(row['revenue'] - data['revenue'].median()) / data['revenue'].std()
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in IQR anomaly detection: {e}")
            return []
    
    async def _detect_zscore_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using Z-score method"""



        try:
            mean_revenue = data['revenue'].mean()
            std_revenue = data['revenue'].std()
            
            if std_revenue == 0:
                return []
            
            data['zscore'] = (data['revenue'] - mean_revenue) / std_revenue
            threshold = self.analysis_config.get('anomaly_threshold', 2.0)
            
            anomalies = []
            anomaly_mask = abs(data['zscore']) > threshold
            
            for idx, row in data[anomaly_mask].iterrows():
                anomaly_type = 'high' if row['zscore'] > 0 else 'low'
                
                # Calculate severity based on Z-score
                abs_zscore = abs(row['zscore'])
                if abs_zscore > 3:
                    severity = 'extreme'
                elif abs_zscore > 2.5:
                    severity = 'high'
                else:
                    severity = 'moderate'
                
                anomalies.append({
                    'date': row['date'],
                    'revenue': float(row['revenue']),
                    'type': anomaly_type,
                    'severity': severity,
                    'method': 'zscore',
                    'score': abs_zscore
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in Z-score anomaly detection: {e}")
            return []
    
    async def _detect_isolation_forest_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using Isolation Forest"""



        try:
            from sklearn.ensemble import IsolationForest
            
            # Prepare features
            features = data[['revenue']].values
            
            # Fit Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(features)
            anomaly_scores = iso_forest.score_samples(features)
            
            anomalies = []
            for idx, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
                if label == -1:  # Anomaly
                    row = data.iloc[idx]
                    
                    # Determine type and severity
                    mean_revenue = data['revenue'].mean()
                    anomaly_type = 'high' if row['revenue'] > mean_revenue else 'low'
                    
                    # Convert score to severity
                    if score < -0.2:
                        severity = 'extreme'
                    elif score < -0.1:
                        severity = 'high'
                    else:
                        severity = 'moderate'
                    
                    anomalies.append({
                        'date': row['date'],
                        'revenue': float(row['revenue']),
                        'type': anomaly_type,
                        'severity': severity,
                        'method': 'isolation_forest',
                        'score': abs(score)
                    })
            
            return anomalies
            
        except ImportError:
            logger.warning("Isolation Forest not available, falling back to IQR method")
            return await self._detect_iqr_anomalies(data)
        except Exception as e:
            logger.error(f"Error in Isolation Forest anomaly detection: {e}")
            return []
    
    async def analyze_revenue_correlations(
        self,
        data: pd.DataFrame,
        external_factors: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """Analyze correlations between revenue and other factors"""



        try:
            correlations = {}
            
            # Internal correlations (if multiple revenue sources)
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            revenue_column = 'revenue' if 'revenue' in data.columns else numeric_columns[0]
            
            for col in numeric_columns:
                if col != revenue_column and col != 'date':
                    correlation = data[revenue_column].corr(data[col])
                    if not np.isnan(correlation):
                        correlations[col] = correlation
            
            # External factor correlations
            if external_factors is not None:
                # Merge data by date
                merged_data = pd.merge(data, external_factors, on='date', how='inner')
                
                for col in external_factors.columns:
                    if col != 'date':
                        correlation = merged_data[revenue_column].corr(merged_data[col])
                        if not np.isnan(correlation):
                            correlations[f"external_{col}"] = correlation
            
            # Time-based correlations
            if 'date' in data.columns:
                data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
                data['month'] = pd.to_datetime(data['date']).dt.month
                data['quarter'] = pd.to_datetime(data['date']).dt.quarter
                
                for time_factor in ['day_of_week', 'month', 'quarter']:
                    correlation = data[revenue_column].corr(data[time_factor])
                    if not np.isnan(correlation):
                        correlations[time_factor] = correlation
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
            raise RevenueAnalysisError(f"Correlation analysis failed: {e}")
    
    async def generate_comprehensive_report(
        self,
        data: pd.DataFrame,
        analysis_types: Optional[List[AnalysisType]] = None
    ) -> AnalysisReport:
        """Generate comprehensive revenue analysis report"""



        try:
            validate_analysis_data(data)
            
            if analysis_types is None:
                analysis_types = [
                    AnalysisType.TREND_ANALYSIS,
                    AnalysisType.SEASONALITY_ANALYSIS,
                    AnalysisType.ANOMALY_DETECTION,
                    AnalysisType.CORRELATION_ANALYSIS
                ]
            
            report_id = str(uuid.uuid4())
            period_start = data['date'].min()
            period_end = data['date'].max()
            total_revenue = Decimal(str(data['revenue'].sum()))
            
            # Perform analyses
            trends = {}
            correlations = {}
            anomalies = []
            key_insights = []
            recommendations = []
            
            # Trend analysis
            if AnalysisType.TREND_ANALYSIS in analysis_types:
                trend_analysis = await self.analyze_revenue_trends(data)
                trends['overall'] = trend_analysis
                
                # Generate trend insights
                if trend_analysis.is_significant:
                    direction_text = trend_analysis.direction.value.replace('_', ' ')
                    key_insights.append(
                        f"Revenue shows {direction_text} trend with {trend_analysis.confidence_level:.1%} confidence"
                    )
                    
                    if trend_analysis.direction in [TrendDirection.STRONG_DOWNWARD, TrendDirection.MODERATE_DOWNWARD]:
                        recommendations.append("Investigate causes of declining revenue and implement corrective measures")
                    elif trend_analysis.direction in [TrendDirection.STRONG_UPWARD, TrendDirection.MODERATE_UPWARD]:
                        recommendations.append("Identify success factors and scale effective strategies")
            
            # Seasonality analysis
            if AnalysisType.SEASONALITY_ANALYSIS in analysis_types:
                seasonality_patterns = await self.analyze_seasonality(data)
                for pattern in seasonality_patterns:
                    key_insights.append(
                        f"Strong {pattern.pattern_type} seasonality detected with {pattern.strength:.1%} strength"
                    )
                    if pattern.peak_periods:
                        recommendations.append(
                            f"Optimize marketing and content strategy for {pattern.pattern_type} peak periods: {', '.join(pattern.peak_periods)}"
                        )
            
            # Anomaly detection
            if AnalysisType.ANOMALY_DETECTION in analysis_types:
                anomalies = await self.detect_revenue_anomalies(data)
                
                if anomalies:
                    extreme_anomalies = [a for a in anomalies if a['severity'] == 'extreme']
                    if extreme_anomalies:
                        key_insights.append(
                            f"Detected {len(extreme_anomalies)} extreme revenue anomalies requiring investigation"
                        )
                        recommendations.append("Investigate extreme anomalies to understand underlying causes")
            
            # Correlation analysis
            if AnalysisType.CORRELATION_ANALYSIS in analysis_types:
                correlations = await self.analyze_revenue_correlations(data)
                
                # Find strong correlations
                strong_correlations = {k: v for k, v in correlations.items() if abs(v) > 0.7}
                if strong_correlations:
                    key_insights.append(
                        f"Found strong correlations with: {', '.join(strong_correlations.keys())}"
                    )
                    recommendations.append("Leverage strongly correlated factors to optimize revenue")
            
            # Calculate overall confidence score
            confidence_scores = []
            if trends:
                confidence_scores.append(trends['overall'].confidence_level)
            if correlations:
                confidence_scores.append(0.8)  # Default correlation confidence
            
            confidence_score = np.mean(confidence_scores) if confidence_scores else 0.5
            
            # Create report
            report = AnalysisReport(
                report_id=report_id,
                analysis_type=AnalysisType.COMPARATIVE_ANALYSIS,  # Comprehensive analysis
                period_start=period_start,
                period_end=period_end,
                total_revenue=total_revenue,
                key_insights=key_insights,
                trends=trends,
                correlations=correlations,
                anomalies=anomalies,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
            # Cache report
            self.cached_reports[report_id] = report
            self.analysis_history.append(report)
            
            logger.info(f"Comprehensive analysis report generated: {report_id}")
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            raise RevenueAnalysisError(f"Report generation failed: {e}")
    
    async def compare_revenue_periods(
        self,
        current_data: pd.DataFrame,
        previous_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Compare revenue between two periods"""



        try:
            # Calculate basic metrics
            current_total = current_data['revenue'].sum()
            previous_total = previous_data['revenue'].sum()
            
            change_amount = current_total - previous_total
            change_percentage = (change_amount / previous_total * 100) if previous_total > 0 else 0
            
            # Calculate daily averages
            current_daily_avg = current_data['revenue'].mean()
            previous_daily_avg = previous_data['revenue'].mean()
            daily_change_percentage = ((current_daily_avg - previous_daily_avg) / previous_daily_avg * 100) if previous_daily_avg > 0 else 0
            
            # Statistical comparison
            t_stat, p_value = stats.ttest_ind(current_data['revenue'], previous_data['revenue'])
            is_significant = p_value < 0.05
            
            # Volatility comparison
            current_volatility = current_data['revenue'].std()
            previous_volatility = previous_data['revenue'].std()
            volatility_change = ((current_volatility - previous_volatility) / previous_volatility * 100) if previous_volatility > 0 else 0
            
            # Trend comparison
            current_trend = await self.analyze_revenue_trends(current_data)
            previous_trend = await self.analyze_revenue_trends(previous_data)
            
            comparison = {
                'period_comparison': {
                    'current_total': float(current_total),
                    'previous_total': float(previous_total),
                    'change_amount': float(change_amount),
                    'change_percentage': change_percentage,
                    'daily_average_change': daily_change_percentage,
                    'is_statistically_significant': is_significant,
                    'p_value': p_value
                },
                'volatility_analysis': {
                    'current_volatility': float(current_volatility),
                    'previous_volatility': float(previous_volatility),
                    'volatility_change_percentage': volatility_change
                },
                'trend_comparison': {
                    'current_trend': {
                        'direction': current_trend.direction.value,
                        'strength': current_trend.trend_strength,
                        'growth_rate': current_trend.growth_rate
                    },
                    'previous_trend': {
                        'direction': previous_trend.direction.value,
                        'strength': previous_trend.trend_strength,
                        'growth_rate': previous_trend.growth_rate
                    }
                },
                'insights': await self._generate_comparison_insights(
                    change_percentage, daily_change_percentage, 
                    current_trend, previous_trend, is_significant
                )
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing revenue periods: {e}")
            raise RevenueAnalysisError(f"Period comparison failed: {e}")
    
    async def _generate_comparison_insights(
        self,
        change_percentage: float,
        daily_change_percentage: float,
        current_trend: TrendAnalysis,
        previous_trend: TrendAnalysis,
        is_significant: bool
    ) -> List[str]:
        """Generate insights from period comparison"""
        insights = []
        
        # Revenue change insights
        if abs(change_percentage) > 20:
            if change_percentage > 0:
                insights.append(f"Significant revenue increase of {change_percentage:.1f}%")
            else:
                insights.append(f"Significant revenue decrease of {abs(change_percentage):.1f}%")
        elif abs(change_percentage) > 10:
            if change_percentage > 0:
                insights.append(f"Moderate revenue increase of {change_percentage:.1f}%")
            else:
                insights.append(f"Moderate revenue decrease of {abs(change_percentage):.1f}%")
        else:
            insights.append("Revenue remained relatively stable between periods")
        
        # Statistical significance
        if is_significant:
            insights.append("The revenue change is statistically significant")
        else:
            insights.append("The revenue change is not statistically significant")
        
        # Trend insights
        if current_trend.direction != previous_trend.direction:
            insights.append(f"Trend direction changed from {previous_trend.direction.value} to {current_trend.direction.value}")
        
        # Growth rate insights
        growth_diff = current_trend.growth_rate - previous_trend.growth_rate
        if abs(growth_diff) > 5:
            if growth_diff > 0:
                insights.append(f"Growth rate accelerated by {growth_diff:.1f} percentage points")
            else:
                insights.append(f"Growth rate decelerated by {abs(growth_diff):.1f} percentage points")
        
        return insights
    
    async def export_analysis_report(self, report_id: str, format: str = 'json') -> Dict[str, Any]:
        """Export analysis report in specified format"""



        try:
            if report_id not in self.cached_reports:
                raise RevenueAnalysisError(f"Report not found: {report_id}")
            
            report = self.cached_reports[report_id]
            
            export_data = {
                'report_info': {
                    'id': report.report_id,
                    'analysis_type': report.analysis_type.value,
                    'period_start': report.period_start.isoformat(),
                    'period_end': report.period_end.isoformat(),
                    'total_revenue': str(report.total_revenue),
                    'confidence_score': report.confidence_score,
                    'created_at': report.created_at.isoformat()
                },
                'key_insights': report.key_insights,
                'trend_analysis': {
                    name: {
                        'direction': trend.direction.value,
                        'slope': trend.slope,
                        'r_squared': trend.r_squared,
                        'confidence_level': trend.confidence_level,
                        'growth_rate': trend.growth_rate,
                        'volatility': trend.volatility,
                        'is_significant': trend.is_significant
                    }
                    for name, trend in report.trends.items()
                },
                'correlations': report.correlations,
                'anomalies': report.anomalies,
                'recommendations': report.recommendations
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting analysis report: {e}")
            raise RevenueAnalysisError(f"Report export failed: {e}")
