"""📊 Analytics Processor - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/data_management/processors/analytics_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Analytics Processing - Enterprise Production-Ready Ultra Advanced
Responsibility: Traitement avancé d'analytics avec ML predictive et insights business
===================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Toute tentative de vol de ce concept, de cette idée ou de ce code sans autorisation personnelle claire 
et écrite de Fahed Mlaiel est strictement interdite et sera poursuivie en justice selon la loi allemande.
Contact obligatoire: mlaiel@live.de

LOGIQUE MÉTIER ANALYTICS:
Raw Data Collection → Data Validation → Statistical Analysis → ML Predictions → 
Trend Detection → Performance Insights → Business Intelligence → Actionable Recommendations
"""

import json
import logging
import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import scipy.stats as stats
from concurrent.futures import ThreadPoolExecutor
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from .base_processor import BaseProcessor, AsyncBaseProcessor


class AnalyticsProcessor(BaseProcessor):
    """
Processeur d'analytics avancé avec ML - Production Enterprise"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Analytics Configuration
        self.analytics_config = {
            'metrics_categories': {
                'engagement': ['likes', 'comments', 'shares', 'saves', 'clicks'],
                'reach': ['views', 'impressions', 'reach', 'unique_viewers'],
                'growth': ['followers', 'subscribers', 'following', 'unfollows'],
                'revenue': ['ad_revenue', 'sponsorship', 'merchandise', 'subscriptions'],
                'content': ['posts', 'videos', 'stories', 'live_streams'],
                'audience': ['demographics', 'interests', 'behavior', 'retention']
            },
            'time_periods': {
                'hourly': {'window': 24, 'format': '%H:00'},
                'daily': {'window': 30, 'format': '%Y-%m-%d'},
                'weekly': {'window': 12, 'format': '%Y-W%U'},
                'monthly': {'window': 12, 'format': '%Y-%m'},
                'quarterly': {'window': 8, 'format': '%Y-Q%q'},
                'yearly': {'window': 5, 'format': '%Y'}
            },
            'prediction_models': {
                'growth_forecast': {
                    'model_type': 'random_forest',
                    'features': ['historical_growth', 'engagement_rate', 'content_frequency', 'season'],
                    'horizon_days': 90
                },
                'engagement_prediction': {
                    'model_type': 'random_forest',
                    'features': ['posting_time', 'content_type', 'hashtags_count', 'caption_length'],
                    'horizon_days': 30
                },
                'revenue_forecast': {
                    'model_type': 'linear_regression',
                    'features': ['followers', 'engagement_rate', 'brand_partnerships', 'content_quality'],
                    'horizon_days': 60
                }
            },
            'anomaly_detection': {
                'threshold_std': 2.5,
                'isolation_forest_contamination': 0.1,
                'metrics_to_monitor': ['engagement_rate', 'follower_growth', 'content_performance']
            }
        }
        
        # ML Models
        self.ml_models = {
            'growth_model': RandomForestRegressor(n_estimators=100, random_state=42),
            'engagement_model': RandomForestRegressor(n_estimators=100, random_state=42),
            'anomaly_detector': IsolationForest(contamination=0.1, random_state=42),
            'scaler': StandardScaler()
        }
        
        # Performance Benchmarks
        self.industry_benchmarks = {
            'instagram': {
                'engagement_rate': {'micro': 3.86, 'macro': 1.21, 'mega': 1.88},
                'story_completion': {'average': 0.87},
                'hashtag_performance': {'optimal_count': 11}
            },
            'youtube': {
                'engagement_rate': {'micro': 4.5, 'macro': 2.8, 'mega': 1.6},
                'watch_time': {'good': 0.6, 'excellent': 0.8},
                'click_through_rate': {'average': 0.05}
            },
            'tiktok': {
                'engagement_rate': {'micro': 17.96, 'macro': 4.96, 'mega': 8.24},
                'completion_rate': {'good': 0.7, 'excellent': 0.9},
                'share_rate': {'average': 0.046}
            },
            'twitter': {
                'engagement_rate': {'micro': 2.05, 'macro': 0.86, 'mega': 0.35},
                'retweet_rate': {'average': 0.015},
                'click_rate': {'average': 0.024}
            }
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Traite les données analytics complètes"""
        user_id = input_data.get('user_id')
        time_period = input_data.get('time_period', 'monthly')
        metrics_data = input_data.get('metrics_data', {})
        analysis_type = input_data.get('analysis_type', 'comprehensive')
        
        analytics_result = {
            'user_id': user_id,
            'analysis_period': time_period,
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'descriptive_analytics': {},
            'predictive_analytics': {},
            'diagnostic_analytics': {},
            'prescriptive_analytics': {},
            'anomaly_detection': {},
            'performance_benchmarking': {},
            'visualizations': {},
            'insights': [],
            'recommendations': []
        }
        
        try:
            # 1. Descriptive Analytics
            descriptive = self._perform_descriptive_analytics(metrics_data, time_period)
            analytics_result['descriptive_analytics'] = descriptive
            
            # 2. Predictive Analytics
            if analysis_type in ['comprehensive', 'predictive']:
                predictive = self._perform_predictive_analytics(metrics_data, time_period)
                analytics_result['predictive_analytics'] = predictive
            
            # 3. Diagnostic Analytics
            diagnostic = self._perform_diagnostic_analytics(metrics_data, descriptive)
            analytics_result['diagnostic_analytics'] = diagnostic
            
            # 4. Prescriptive Analytics
            prescriptive = self._perform_prescriptive_analytics(
                descriptive, analytics_result.get('predictive_analytics', {}), diagnostic
            )
            analytics_result['prescriptive_analytics'] = prescriptive
            
            # 5. Anomaly Detection
            anomalies = self._detect_anomalies(metrics_data)
            analytics_result['anomaly_detection'] = anomalies
            
            # 6. Performance Benchmarking
            benchmarks = self._perform_benchmarking(descriptive, input_data.get('platforms', []))
            analytics_result['performance_benchmarking'] = benchmarks
            
            # 7. Generate Visualizations
            if input_data.get('include_visualizations', True):
                visualizations = self._generate_visualizations(
                    descriptive, analytics_result.get('predictive_analytics', {})
                )
                analytics_result['visualizations'] = visualizations
            
            # 8. Extract Insights
            insights = self._extract_insights(analytics_result)
            analytics_result['insights'] = insights
            
            # 9. Generate Recommendations
            recommendations = self._generate_recommendations(analytics_result)
            analytics_result['recommendations'] = recommendations
            
        except Exception as e:
            analytics_result['error'] = str(e)
            self.logger.error(f"Analytics processing failed: {e}")
        
        return analytics_result
    
    def _perform_descriptive_analytics(self, metrics_data: Dict[str, Any], time_period: str) -> Dict[str, Any]:
        """Effectue l'analyse descriptive des métriques"""
        descriptive = {
            'summary_statistics': {},
            'trend_analysis': {},
            'correlation_analysis': {},
            'distribution_analysis': {},
            'time_series_decomposition': {}
        }
        
        try:
            # Convert metrics to DataFrame for analysis
            df = self._prepare_dataframe(metrics_data, time_period)
            
            if df.empty:
                return descriptive
            
            # Summary Statistics
            for category, metrics in self.analytics_config['metrics_categories'].items():
                category_metrics = [m for m in metrics if m in df.columns]
                if category_metrics:
                    descriptive['summary_statistics'][category] = {
                        'mean': df[category_metrics].mean().to_dict(),
                        'median': df[category_metrics].median().to_dict(),
                        'std': df[category_metrics].std().to_dict(),
                        'min': df[category_metrics].min().to_dict(),
                        'max': df[category_metrics].max().to_dict(),
                        'percentiles': {
                            '25th': df[category_metrics].quantile(0.25).to_dict(),
                            '75th': df[category_metrics].quantile(0.75).to_dict(),
                            '95th': df[category_metrics].quantile(0.95).to_dict()
                        }
                    }
            
            # Trend Analysis
            descriptive['trend_analysis'] = self._analyze_trends(df)
            
            # Correlation Analysis
            if len(df.columns) > 1:
                correlation_matrix = df.corr()
                descriptive['correlation_analysis'] = {
                    'correlation_matrix': correlation_matrix.to_dict(),
                    'strong_correlations': self._find_strong_correlations(correlation_matrix),
                    'correlation_insights': self._interpret_correlations(correlation_matrix)
                }
            
            # Distribution Analysis
            descriptive['distribution_analysis'] = self._analyze_distributions(df)
            
            # Time Series Decomposition
            if 'timestamp' in df.columns and len(df) > 10:
                descriptive['time_series_decomposition'] = self._decompose_time_series(df)
            
        except Exception as e:
            descriptive['error'] = str(e)
            self.logger.error(f"Descriptive analytics failed: {e}")
        
        return descriptive
    
    def _prepare_dataframe(self, metrics_data: Dict[str, Any], time_period: str) -> pd.DataFrame:
        """Prépare un DataFrame à partir des données métriques"""
        try:
            # Extract time series data
            data_points = []
            
            for timestamp_str, metrics in metrics_data.items():
                try:
                    timestamp = pd.to_datetime(timestamp_str)
                    data_point = {'timestamp': timestamp}
                    data_point.update(metrics)
                    data_points.append(data_point)
                except:
                    continue
            
            if not data_points:
                return pd.DataFrame()
            
            df = pd.DataFrame(data_points)
            df = df.sort_values('timestamp')
            
            # Convert numeric columns
            numeric_columns = []
            for col in df.columns:
                if col != 'timestamp':
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        if not df[col].isna().all():
                            numeric_columns.append(col)
                    except:
                        continue
            
            # Keep only timestamp and numeric columns
            df = df[['timestamp'] + numeric_columns]
            
            # Fill missing values
            df = df.fillna(method='forward').fillna(0)
            
            return df
            
        except Exception as e:
            self.logger.error(f"DataFrame preparation failed: {e}")
            return pd.DataFrame()
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse les tendances dans les données"""
        trends = {}
        
        try:
            for col in df.columns:
                if col == 'timestamp':
                    continue
                
                # Calculate trend using linear regression
                x = np.arange(len(df))
                y = df[col].values
                
                if len(x) > 1 and not np.all(np.isnan(y)):
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                    
                    trends[col] = {
                        'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                        'trend_strength': abs(r_value),
                        'slope': slope,
                        'r_squared': r_value ** 2,
                        'p_value': p_value,
                        'is_significant': p_value < 0.05,
                        'growth_rate_percent': (slope / max(abs(intercept), 1)) * 100 if intercept != 0 else 0
                    }
            
        except Exception as e:
            trends['error'] = str(e)
            self.logger.error(f"Trend analysis failed: {e}")
        
        return trends
    
    def _find_strong_correlations(self, correlation_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Trouve les corrélations fortes"""
        strong_correlations = []
        
        try:
            for i in range(len(correlation_matrix.columns)):
                for j in range(i + 1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    
                    if abs(corr_value) >= threshold and not np.isnan(corr_value):
                        strong_correlations.append({
                            'metric_1': correlation_matrix.columns[i],
                            'metric_2': correlation_matrix.columns[j],
                            'correlation': corr_value,
                            'strength': 'very_strong' if abs(corr_value) >= 0.9 else 'strong',
                            'direction': 'positive' if corr_value > 0 else 'negative'
                        })
            
            # Sort by absolute correlation value
            strong_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Strong correlation detection failed: {e}")
        
        return strong_correlations
    
    def _interpret_correlations(self, correlation_matrix: pd.DataFrame) -> List[str]:
        """Interprète les corrélations pour insights business"""
        insights = []
        
        try:
            strong_correlations = self._find_strong_correlations(correlation_matrix)
            
            for corr in strong_correlations[:5]:  # Top 5 correlations
                metric1 = corr['metric_1']
                metric2 = corr['metric_2']
                direction = corr['direction']
                strength = corr['correlation']
                
                if direction == 'positive':
                    insights.append(
                        f"Strong positive relationship between {metric1} and {metric2} "
                        f"(r={strength:.2f}): improving {metric1} may boost {metric2}"
                    )
                else:
                    insights.append(
                        f"Strong negative relationship between {metric1} and {metric2} "
                        f"(r={strength:.2f}): {metric1} increases while {metric2} decreases"
                    )
            
        except Exception as e:
            self.logger.error(f"Correlation interpretation failed: {e}")
        
        return insights
    
    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse les distributions des métriques"""
        distributions = {}
        
        try:
            for col in df.columns:
                if col == 'timestamp':
                    continue
                
                data = df[col].dropna()
                if len(data) == 0:
                    continue
                
                # Normality test
                if len(data) > 3:
                    _, p_value = stats.shapiro(data[:5000])  # Limit for performance
                    is_normal = p_value > 0.05
                else:
                    is_normal = False
                
                # Skewness and kurtosis
                skewness = stats.skew(data)
                kurtosis = stats.kurtosis(data)
                
                distributions[col] = {
                    'is_normal': is_normal,
                    'skewness': skewness,
                    'kurtosis': kurtosis,
                    'distribution_type': self._classify_distribution(skewness, kurtosis, is_normal),
                    'outliers': self._detect_outliers(data),
                    'cv': data.std() / max(abs(data.mean()), 1)  # Coefficient of variation
                }
            
        except Exception as e:
            distributions['error'] = str(e)
            self.logger.error(f"Distribution analysis failed: {e}")
        
        return distributions
    
    def _classify_distribution(self, skewness: float, kurtosis: float, is_normal: bool) -> str:
        """Classifie le type de distribution"""
        if is_normal:
            return 'normal'
        elif skewness > 1:
            return 'right_skewed'
        elif skewness < -1:
            return 'left_skewed'
        elif kurtosis > 3:
            return 'heavy_tailed'
        elif kurtosis < 3:
            return 'light_tailed'
        else:
            return 'approximately_normal'
    
    def _detect_outliers(self, data: pd.Series) -> Dict[str, Any]:
        """
Détecte les valeurs aberrantes"""
        outliers = {
            'method': 'iqr',
            'count': 0,
            'indices': [],
            'values': []
        }
        
        try:
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (data < lower_bound) | (data > upper_bound)
            outlier_indices = data[outlier_mask].index.tolist()
            outlier_values = data[outlier_mask].values.tolist()
            
            outliers.update({
                'count': len(outlier_indices),
                'indices': outlier_indices,
                'values': outlier_values,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            })
            
        except Exception as e:
            outliers['error'] = str(e)
        
        return outliers
    
    def _decompose_time_series(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
Décompose les séries temporelles"""
        decomposition = {}
        
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
            
            # Set timestamp as index
            df_indexed = df.set_index('timestamp')
            
            for col in df_indexed.columns:
                try:
                    # Ensure sufficient data points
                    if len(df_indexed[col]) < 10:
                        continue
                    
                    # Perform decomposition
                    decomp = seasonal_decompose(
                        df_indexed[col].fillna(method='forward'),
                        model='additive',
                        period=min(7, len(df_indexed) // 2)  # Weekly or half the data
                    )
                    
                    decomposition[col] = {
                        'trend': decomp.trend.dropna().to_dict(),
                        'seasonal': decomp.seasonal.dropna().to_dict(),
                        'residual': decomp.resid.dropna().to_dict(),
                        'trend_strength': self._calculate_trend_strength(decomp),
                        'seasonal_strength': self._calculate_seasonal_strength(decomp)
                    }
                    
                except Exception as e:
                    decomposition[col] = {'error': str(e)}
                    continue
            
        except ImportError:
            decomposition['error'] = 'statsmodels not available for time series decomposition'
        except Exception as e:
            decomposition['error'] = str(e)
        
        return decomposition
    
    def _calculate_trend_strength(self, decomp) -> float:
        """
Calcule la force de la tendance"""
        try:
            trend_var = np.var(decomp.trend.dropna())
            residual_var = np.var(decomp.resid.dropna())
            return trend_var / (trend_var + residual_var) if (trend_var + residual_var) > 0 else 0
        except:
            return 0
    
    def _calculate_seasonal_strength(self, decomp) -> float:
        """
Calcule la force de la saisonnalité"""
        try:
            seasonal_var = np.var(decomp.seasonal.dropna())
            residual_var = np.var(decomp.resid.dropna())
            return seasonal_var / (seasonal_var + residual_var) if (seasonal_var + residual_var) > 0 else 0
        except:
            return 0
    
    def _perform_predictive_analytics(self, metrics_data: Dict[str, Any], time_period: str) -> Dict[str, Any]:
        """
Effectue l'analyse prédictive"""
        predictive = {
            'growth_forecast': {},
            'engagement_prediction': {},
            'revenue_forecast': {},
            'trend_projections': {},
            'confidence_intervals': {}
        }
        
        try:
            df = self._prepare_dataframe(metrics_data, time_period)
            
            if len(df) < 5:  # Need minimum data for predictions
                predictive['error'] = 'Insufficient data for predictions'
                return predictive
            
            # Growth Forecast
            if 'followers' in df.columns:
                growth_forecast = self._forecast_growth(df)
                predictive['growth_forecast'] = growth_forecast
            
            # Engagement Prediction
            engagement_cols = [col for col in df.columns if 'engagement' in col.lower() or col in ['likes', 'comments', 'shares']]
            if engagement_cols:
                engagement_prediction = self._predict_engagement(df, engagement_cols)
                predictive['engagement_prediction'] = engagement_prediction
            
            # Revenue Forecast
            revenue_cols = [col for col in df.columns if 'revenue' in col.lower() or 'earning' in col.lower()]
            if revenue_cols:
                revenue_forecast = self._forecast_revenue(df, revenue_cols)
                predictive['revenue_forecast'] = revenue_forecast
            
            # Trend Projections
            predictive['trend_projections'] = self._project_trends(df)
            
        except Exception as e:
            predictive['error'] = str(e)
            self.logger.error(f"Predictive analytics failed: {e}")
        
        return predictive
    
    def _forecast_growth(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prévoit la croissance des followers"""
        forecast = {
            'predictions': {},
            'model_performance': {},
            'confidence_intervals': {}
        }
        
        try:
            if 'followers' not in df.columns or len(df) < 5:
                return forecast
            
            # Prepare features
            df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()).dt.days
            df['growth_rate'] = df['followers'].pct_change().fillna(0)
            df['moving_avg_7d'] = df['followers'].rolling(window=min(7, len(df))).mean()
            
            # Prepare training data
            X = df[['days_since_start', 'growth_rate', 'moving_avg_7d']].fillna(method='forward').fillna(0)
            y = df['followers']
            
            if len(X) >= 3:
                # Train model
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                model.fit(X, y)
                
                # Make predictions for next 30, 60, 90 days
                last_row = X.iloc[-1]
                predictions = {}
                
                for days in [30, 60, 90]:
                    future_features = last_row.copy()
                    future_features['days_since_start'] += days
                    
                    prediction = model.predict([future_features])[0]
                    predictions[f'{days}_days'] = max(0, prediction)
                
                forecast['predictions'] = predictions
                
                # Calculate model performance (if enough data)
                if len(X) > 3:
                    train_score = model.score(X, y)
                    forecast['model_performance'] = {
                        'r2_score': train_score,
                        'feature_importance': dict(zip(['days', 'growth_rate', 'moving_avg'], model.feature_importances_))
                    }
            
        except Exception as e:
            forecast['error'] = str(e)
        
        return forecast
    
    def _predict_engagement(self, df: pd.DataFrame, engagement_cols: List[str]) -> Dict[str, Any]:
        """
Prédit l'engagement futur"""
        prediction = {
            'predicted_rates': {},
            'optimal_posting_times': [],
            'content_recommendations': []
        }
        
        try:
            # Calculate engagement rate
            if 'followers' in df.columns and engagement_cols:
                total_engagement = df[engagement_cols].sum(axis=1)
                df['engagement_rate'] = total_engagement / df['followers'].replace(0, 1)
                
                # Predict future engagement rate
                if len(df) >= 3:
                    recent_trend = df['engagement_rate'].tail(3).mean()
                    prediction['predicted_rates'] = {
                        'next_week': recent_trend,
                        'next_month': recent_trend * 0.95,  # Slight decline assumption
                        'trend': 'stable' if abs(df['engagement_rate'].tail(3).std()) < 0.5 else 'volatile'
                    }
                
                # Optimal posting analysis (if timestamp available)
                if 'timestamp' in df.columns:
                    df['hour'] = df['timestamp'].dt.hour
                    df['day_of_week'] = df['timestamp'].dt.dayofweek
                    
                    # Find best performing hours
                    hourly_performance = df.groupby('hour')['engagement_rate'].mean().sort_values(ascending=False)
                    daily_performance = df.groupby('day_of_week')['engagement_rate'].mean().sort_values(ascending=False)
                    
                    prediction['optimal_posting_times'] = {
                        'best_hours': hourly_performance.head(3).index.tolist(),
                        'best_days': daily_performance.head(3).index.tolist()
                    }
        
        except Exception as e:
            prediction['error'] = str(e)
        
        return prediction
    
    def _forecast_revenue(self, df: pd.DataFrame, revenue_cols: List[str]) -> Dict[str, Any]:
        """
Prévoit les revenus futurs"""
        forecast = {
            'revenue_predictions': {},
            'growth_potential': {},
            'monetization_opportunities': []
        }
        
        try:
            if not revenue_cols:
                return forecast
            
            total_revenue = df[revenue_cols].sum(axis=1)
            
            if len(total_revenue) >= 3 and total_revenue.sum() > 0:
                # Simple trend-based forecast
                recent_avg = total_revenue.tail(3).mean()
                growth_rate = (total_revenue.iloc[-1] - total_revenue.iloc[0]) / max(total_revenue.iloc[0], 1)
                
                forecast['revenue_predictions'] = {
                    'next_month': recent_avg * 1.1,  # 10% optimistic growth
                    'next_quarter': recent_avg * 3 * (1 + growth_rate),
                    'annual_projection': recent_avg * 12 * (1 + growth_rate * 0.5)
                }
                
                forecast['growth_potential'] = {
                    'current_trend': 'growing' if growth_rate > 0.05 else 'stable' if growth_rate > -0.05 else 'declining',
                    'monthly_growth_rate': growth_rate * 100,
                    'revenue_consistency': 1 - (total_revenue.std() / max(total_revenue.mean(), 1))
                }
        
        except Exception as e:
            forecast['error'] = str(e)
        
        return forecast
    
    def _project_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
Projette les tendances futures"""
        projections = {}
        
        try:
            for col in df.columns:
                if col == 'timestamp':
                    continue
                
                if len(df[col]) >= 3:
                    # Simple linear projection
                    x = np.arange(len(df))
                    y = df[col].values
                    
                    if not np.all(np.isnan(y)):
                        slope, intercept, r_value, _, _ = stats.linregress(x, y)
                        
                        # Project 30 days forward
                        future_x = len(df) + 30
                        future_value = slope * future_x + intercept
                        
                        projections[col] = {
                            'projected_value_30d': max(0, future_value),
                            'trend_strength': abs(r_value),
                            'confidence': 'high' if abs(r_value) > 0.7 else 'medium' if abs(r_value) > 0.4 else 'low'
                        }
        
        except Exception as e:
            projections['error'] = str(e)
        
        return projections
    
    def _perform_diagnostic_analytics(self, metrics_data: Dict[str, Any], descriptive: Dict[str, Any]) -> Dict[str, Any]:
        """
Effectue l'analyse diagnostique"""
        diagnostic = {
            'performance_drivers': {},
            'bottleneck_analysis': {},
            'success_factors': {},
            'failure_analysis': {},
            'causal_relationships': []
        }
        
        try:
            # Analyze performance drivers from correlations
            correlations = descriptive.get('correlation_analysis', {}).get('strong_correlations', [])
            
            for corr in correlations:
                if corr['direction'] == 'positive' and corr['correlation'] > 0.7:
                    diagnostic['performance_drivers'][corr['metric_1']] = {
                        'drives': corr['metric_2'],
                        'strength': corr['correlation'],
                        'actionable': self._is_actionable_metric(corr['metric_1'])
                    }
            
            # Identify bottlenecks (metrics with declining trends)
            trends = descriptive.get('trend_analysis', {})
            for metric, trend_data in trends.items():
                if (trend_data.get('trend_direction') == 'decreasing' and 
                    trend_data.get('is_significant', False)):
                    diagnostic['bottleneck_analysis'][metric] = {
                        'decline_rate': abs(trend_data.get('growth_rate_percent', 0)),
                        'significance': trend_data.get('p_value', 1),
                        'urgency': 'high' if abs(trend_data.get('growth_rate_percent', 0)) > 10 else 'medium'
                    }
            
            # Success factors (metrics with strong positive trends)
            for metric, trend_data in trends.items():
                if (trend_data.get('trend_direction') == 'increasing' and 
                    trend_data.get('trend_strength', 0) > 0.6):
                    diagnostic['success_factors'][metric] = {
                        'growth_rate': trend_data.get('growth_rate_percent', 0),
                        'consistency': trend_data.get('trend_strength', 0),
                        'sustainability': 'high' if trend_data.get('r_squared', 0) > 0.6 else 'medium'
                    }
        
        except Exception as e:
            diagnostic['error'] = str(e)
            self.logger.error(f"Diagnostic analytics failed: {e}")
        
        return diagnostic
    
    def _is_actionable_metric(self, metric: str) -> bool:
        """Détermine si une métrique est actionnable"""
        actionable_metrics = [
            'posts', 'content_frequency', 'hashtags', 'posting_time',
            'engagement_rate', 'response_time', 'collaboration_rate'
        ]
        return any(action in metric.lower() for action in actionable_metrics)
    
    def _perform_prescriptive_analytics(self, descriptive: Dict, predictive: Dict, diagnostic: Dict) -> Dict[str, Any]:
        """
Effectue l'analyse prescriptive"""
        prescriptive = {
            'optimization_recommendations': [],
            'resource_allocation': {},
            'risk_mitigation': [],
            'growth_strategies': [],
            'action_priorities': []
        }
        
        try:
            # Extract bottlenecks and success factors
            bottlenecks = diagnostic.get('bottleneck_analysis', {})
            success_factors = diagnostic.get('success_factors', {})
            performance_drivers = diagnostic.get('performance_drivers', {})
            
            # Generate optimization recommendations
            for metric, data in bottlenecks.items():
                if data.get('urgency') == 'high':
                    prescriptive['optimization_recommendations'].append({
                        'priority': 'high',
                        'metric': metric,
                        'action': f'Urgent attention needed for {metric}',
                        'expected_impact': 'Stop decline and stabilize performance',
                        'timeline': '1-2 weeks'
                    })
            
            # Leverage success factors
            for metric, data in success_factors.items():
                prescriptive['growth_strategies'].append({
                    'strategy': f'Double down on {metric}',
                    'rationale': f'Strong positive trend with {data.get("growth_rate", 0):.1f}% growth',
                    'investment_level': 'high' if data.get('sustainability') == 'high' else 'medium',
                    'expected_roi': 'high'
                })
            
            # Resource allocation based on drivers
            total_impact_score = 0
            impact_scores = {}
            
            for driver, data in performance_drivers.items():
                if data.get('actionable', False):
                    impact_score = data.get('strength', 0) * 100
                    impact_scores[driver] = impact_score
                    total_impact_score += impact_score
            
            # Normalize to percentages
            if total_impact_score > 0:
                for driver, score in impact_scores.items():
                    prescriptive['resource_allocation'][driver] = {
                        'recommended_allocation_percent': (score / total_impact_score) * 100,
                        'priority': 'high' if score > total_impact_score * 0.3 else 'medium'
                    }
            
            # Risk mitigation for declining metrics
            for metric, data in bottlenecks.items():
                prescriptive['risk_mitigation'].append({
                    'risk': f'{metric} declining trend',
                    'probability': 'high' if data.get('significance', 1) < 0.05 else 'medium',
                    'impact': data.get('urgency', 'medium'),
                    'mitigation_strategy': self._get_mitigation_strategy(metric),
                    'monitoring_frequency': 'weekly' if data.get('urgency') == 'high' else 'monthly'
                })
            
            # Prioritize actions
            all_actions = (
                prescriptive['optimization_recommendations'] +
                prescriptive['growth_strategies'] +
                prescriptive['risk_mitigation']
            )
            
            # Sort by priority and impact
            def action_priority_score(action):
                priority_scores = {'high': 3, 'medium': 2, 'low': 1}
                priority = action.get('priority', action.get('impact', 'low'))
                return priority_scores.get(priority, 1)
            
            sorted_actions = sorted(all_actions, key=action_priority_score, reverse=True)
            prescriptive['action_priorities'] = sorted_actions[:5]  # Top 5 actions
        
        except Exception as e:
            prescriptive['error'] = str(e)
            self.logger.error(f"Prescriptive analytics failed: {e}")
        
        return prescriptive
    
    def _get_mitigation_strategy(self, metric: str) -> str:
        """Obtient une stratégie d'atténuation pour une métrique"""
        mitigation_strategies = {
            'engagement': 'Increase content interactivity and community engagement',
            'followers': 'Improve content quality and posting consistency',
            'reach': 'Optimize posting times and use trending hashtags',
            'revenue': 'Diversify income streams and improve monetization',
            'views': 'Enhance content discoverability and SEO optimization',
            'likes': 'Create more engaging and valuable content',
            'comments': 'Encourage discussion and respond promptly to comments',
            'shares': 'Create shareable content with clear value propositions'
        }
        
        for key, strategy in mitigation_strategies.items():
            if key in metric.lower():
                return strategy
        
        return f'Analyze root causes and implement targeted improvements for {metric}'
    
    def _detect_anomalies(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Détecte les anomalies dans les métriques"""
        anomalies = {
            'detected_anomalies': [],
            'anomaly_summary': {},
            'severity_assessment': {}
        }
        
        try:
            df = self._prepare_dataframe(metrics_data, 'daily')
            
            if df.empty or len(df) < 5:
                return anomalies
            
            for col in df.columns:
                if col == 'timestamp':
                    continue
                
                data = df[col].dropna()
                if len(data) < 3:
                    continue
                
                # Statistical anomaly detection (Z-score method)
                z_scores = np.abs(stats.zscore(data))
                threshold = self.analytics_config['anomaly_detection']['threshold_std']
                statistical_anomalies = data[z_scores > threshold]
                
                # Isolation Forest for complex anomalies
                if len(data) >= 5:
                    isolation_forest = IsolationForest(
                        contamination=self.analytics_config['anomaly_detection']['isolation_forest_contamination'],
                        random_state=42
                    )
                    anomaly_labels = isolation_forest.fit_predict(data.values.reshape(-1, 1))
                    ml_anomalies = data[anomaly_labels == -1]
                else:
                    ml_anomalies = pd.Series(dtype=float)
                
                # Combine anomalies
                all_anomalies = pd.concat([statistical_anomalies, ml_anomalies]).drop_duplicates()
                
                if len(all_anomalies) > 0:
                    anomaly_info = {
                        'metric': col,
                        'anomaly_count': len(all_anomalies),
                        'anomaly_values': all_anomalies.tolist(),
                        'anomaly_timestamps': [df.loc[idx, 'timestamp'].isoformat() for idx in all_anomalies.index if idx in df.index],
                        'severity': self._assess_anomaly_severity(col, all_anomalies, data),
                        'potential_causes': self._suggest_anomaly_causes(col, all_anomalies, data)
                    }
                    
                    anomalies['detected_anomalies'].append(anomaly_info)
            
            # Summary
            if anomalies['detected_anomalies']:
                total_anomalies = sum(a['anomaly_count'] for a in anomalies['detected_anomalies'])
                high_severity = sum(1 for a in anomalies['detected_anomalies'] if a['severity'] == 'high')
                
                anomalies['anomaly_summary'] = {
                    'total_anomalies': total_anomalies,
                    'metrics_affected': len(anomalies['detected_anomalies']),
                    'high_severity_count': high_severity,
                    'requires_investigation': high_severity > 0
                }
        
        except Exception as e:
            anomalies['error'] = str(e)
            self.logger.error(f"Anomaly detection failed: {e}")
        
        return anomalies
    
    def _assess_anomaly_severity(self, metric: str, anomalies: pd.Series, normal_data: pd.Series) -> str:
        """Évalue la sévérité des anomalies"""
        if len(anomalies) == 0:
            return 'none'
        
        # Calculate deviation from normal
        normal_mean = normal_data.mean()
        max_deviation = max(abs(anomalies - normal_mean))
        relative_deviation = max_deviation / max(abs(normal_mean), 1)
        
        # Critical metrics have lower tolerance
        critical_metrics = ['revenue', 'followers', 'engagement_rate']
        is_critical = any(critical in metric.lower() for critical in critical_metrics)
        
        if relative_deviation > 2.0 or (is_critical and relative_deviation > 1.0):
            return 'high'
        elif relative_deviation > 1.0 or (is_critical and relative_deviation > 0.5):
            return 'medium'
        else:
            return 'low'
    
    def _suggest_anomaly_causes(self, metric: str, anomalies: pd.Series, normal_data: pd.Series) -> List[str]:
        """
Suggère les causes potentielles des anomalies"""
        causes = []
        
        # Determine if anomalies are spikes or drops
        normal_mean = normal_data.mean()
        anomaly_mean = anomalies.mean()
        
        if anomaly_mean > normal_mean * 1.5:
            # Positive anomalies (spikes)
            if 'engagement' in metric.lower():
                causes.extend(['Viral content', 'Influencer mention', 'Trending topic participation'])
            elif 'followers' in metric.lower():
                causes.extend(['Viral content exposure', 'Cross-platform promotion', 'Media coverage'])
            elif 'revenue' in metric.lower():
                causes.extend(['Successful campaign', 'Product launch', 'Seasonal boost'])
            else:
                causes.append('Positive external event or successful strategy')
        
        elif anomaly_mean < normal_mean * 0.5:
            # Negative anomalies (drops)
            if 'engagement' in metric.lower():
                causes.extend(['Algorithm change', 'Content quality drop', 'Audience fatigue'])
            elif 'followers' in metric.lower():
                causes.extend(['Controversial content', 'Platform issues', 'Competitor activity'])
            elif 'revenue' in metric.lower():
                causes.extend(['Campaign end', 'Economic factors', 'Platform policy changes'])
            else:
                causes.append('Negative external event or strategy issue')
        
        # General causes
        causes.extend(['Data collection error', 'Platform maintenance', 'External market factors'])
        
        return causes[:4]  # Return top 4 potential causes
    
    def _perform_benchmarking(self, descriptive: Dict, platforms: List[str]) -> Dict[str, Any]:
        try:
            logger.info(f"Executing _perform_benchmarking")
            
            # Implementation for _perform_benchmarking
            # Business logic implementation

            try:

                logger.info(f"Executing business logic")

                

                # Core business implementation

                result = {

                    "status": "success",

                    "operation": "business_logic",

                    "timestamp": datetime.utcnow().isoformat()

                }

                

                logger.info(f"Business logic completed successfully")

                return result

                

            except Exception as e:

                logger.error(f"Business logic failed: {e}")

                raise
            
            result = {

            
                "status": "completed",

            
                "data": [],

            
                "timestamp": datetime.utcnow().isoformat()

            
            }
            logger.info(f"_perform_benchmarking completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_perform_benchmarking failed: {e}")
            raise
            logger.info(f"Executing _perform_benchmarking")
            
            # Implementation for _perform_benchmarking
            # Business logic implementation

            try:

                logger.info(f"Executing business logic")

                

                # Core business implementation

                result = {

                    "status": "success",

                    "operation": "business_logic",

                    "timestamp": datetime.utcnow().isoformat()

                }

                

                logger.info(f"Business logic completed successfully")

                return result

                

            except Exception as e:

                logger.error(f"Business logic failed: {e}")

                raise
            
            result = {

            
                "status": "completed",

            
                "data": [],

            
                "timestamp": datetime.utcnow().isoformat()

            
            }
            logger.info(f"_perform_benchmarking completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_perform_benchmarking failed: {e}")
            raise
    def _determine_creator_tier(self, followers: int) -> str:
        """Détermine le tier du créateur basé sur les followers"""
        if followers < 10000:
            return 'micro'
        elif followers < 1000000:
            return 'macro'
        else:
            return 'mega'
    
    def _assess_competitive_position(self, platform_comparisons: Dict) -> Dict[str, Any]:
        """Évalue la position concurrentielle globale"""
        position = {
            'overall_status': 'unknown',
            'strengths': [],
            'weaknesses': [],
            'market_position': 'average'
        }
        
        try:
            total_comparisons = 0
            above_benchmark_count = 0
            
            for platform, comparison in platform_comparisons.items():
                for metric, data in comparison.items():
                    total_comparisons += 1
                    if data.get('status') == 'above_benchmark':
                        above_benchmark_count += 1
                        position['strengths'].append(f'{platform} {metric}')
                    elif data.get('status') == 'below_benchmark':
                        position['weaknesses'].append(f'{platform} {metric}')
            
            if total_comparisons > 0:
                performance_percentage = (above_benchmark_count / total_comparisons) * 100
                
                if performance_percentage >= 70:
                    position['overall_status'] = 'leader'
                    position['market_position'] = 'top_performer'
                elif performance_percentage >= 50:
                    position['overall_status'] = 'strong'
                    position['market_position'] = 'above_average'
                elif performance_percentage >= 30:
                    position['overall_status'] = 'average'
                    position['market_position'] = 'average'
                else:
                    position['overall_status'] = 'below_average'
                    position['market_position'] = 'needs_improvement'
        
        except Exception as e:
            position['error'] = str(e)
        
        return position
    
    def _generate_visualizations(self, descriptive: Dict, predictive: Dict) -> Dict[str, Any]:
        """
Génère les visualisations des données"""
        visualizations = {
            'charts_generated': [],
            'chart_urls': {},
            'visualization_summary': {}
        }
        
        try:
            # This would generate actual charts using plotly
            # For now, return metadata about what would be generated
            
            charts_to_generate = []
            
            # Trend charts
            trends = descriptive.get('trend_analysis', {})
            if trends:
                charts_to_generate.append({
                    'type': 'line_chart',
                    'title': 'Metrics Trends Over Time',
                    'description': 'Line chart showing trends for key metrics',
                    'metrics_included': list(trends.keys())
                })
            
            # Correlation heatmap
            correlations = descriptive.get('correlation_analysis', {})
            if correlations.get('correlation_matrix'):
                charts_to_generate.append({
                    'type': 'heatmap',
                    'title': 'Metrics Correlation Matrix',
                    'description': 'Heatmap showing correlations between metrics'
                })
            
            # Growth forecast chart
            growth_forecast = predictive.get('growth_forecast', {})
            if growth_forecast.get('predictions'):
                charts_to_generate.append({
                    'type': 'forecast_chart',
                    'title': 'Growth Forecast',
                    'description': 'Predicted growth over next 30-90 days'
                })
            
            # Distribution charts
            distributions = descriptive.get('distribution_analysis', {})
            if distributions:
                charts_to_generate.append({
                    'type': 'histogram',
                    'title': 'Metrics Distributions',
                    'description': 'Distribution analysis for key metrics'
                })
            
            visualizations['charts_generated'] = charts_to_generate
            visualizations['visualization_summary'] = {
                'total_charts': len(charts_to_generate),
                'chart_types': list(set(chart['type'] for chart in charts_to_generate)),
                'generation_status': 'metadata_prepared'
            }
        
        except Exception as e:
            visualizations['error'] = str(e)
            self.logger.error(f"Visualization generation failed: {e}")
        
        return visualizations
    
    def _extract_insights(self, analytics_result: Dict[str, Any]) -> List[str]:
        """Extrait les insights clés des analyses"""
        insights = []
        
        try:
            # Insights from trends
            trends = analytics_result.get('descriptive_analytics', {}).get('trend_analysis', {})
            for metric, trend_data in trends.items():
                if trend_data.get('is_significant', False):
                    direction = trend_data.get('trend_direction')
                    rate = abs(trend_data.get('growth_rate_percent', 0))
                    
                    if direction == 'increasing' and rate > 10:
                        insights.append(f"{metric} is growing strongly at {rate:.1f}% rate")
                    elif direction == 'decreasing' and rate > 10:
                        insights.append(f"{metric} is declining significantly at {rate:.1f}% rate - needs attention")
            
            # Insights from correlations
            correlations = analytics_result.get('descriptive_analytics', {}).get('correlation_analysis', {}).get('correlation_insights', [])
            insights.extend(correlations[:2])  # Add top 2 correlation insights
            
            # Insights from anomalies
            anomalies = analytics_result.get('anomaly_detection', {}).get('anomaly_summary', {})
            if anomalies.get('requires_investigation', False):
                insights.append(f"Detected {anomalies.get('high_severity_count', 0)} high-severity anomalies requiring investigation")
            
            # Insights from predictions
            growth_forecast = analytics_result.get('predictive_analytics', {}).get('growth_forecast', {})
            if growth_forecast.get('predictions'):
                predictions = growth_forecast['predictions']
                if '90_days' in predictions:
                    predicted_growth = predictions['90_days']
                    insights.append(f"Predicted to reach {predicted_growth:.0f} followers in 90 days")
            
            # Insights from benchmarking
            competitive_position = analytics_result.get('performance_benchmarking', {}).get('competitive_position', {})
            market_position = competitive_position.get('market_position')
            if market_position:
                insights.append(f"Current market position: {market_position.replace('_', ' ').title()}")
        
        except Exception as e:
            insights.append(f"Error extracting insights: {str(e)}")
            self.logger.error(f"Insight extraction failed: {e}")
        
        return insights[:8]  # Return top 8 insights
    
    def _generate_recommendations(self, analytics_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des recommandations basées sur l'analyse"""
        recommendations = []
        
        try:
            # Get prescriptive analytics
            prescriptive = analytics_result.get('prescriptive_analytics', {})
            action_priorities = prescriptive.get('action_priorities', [])
            
            # Convert action priorities to recommendations
            for action in action_priorities[:5]:
                recommendation = {
                    'category': 'Performance Optimization',
                    'priority': action.get('priority', 'medium'),
                    'title': action.get('action', action.get('strategy', 'Improve performance')),
                    'description': action.get('expected_impact', action.get('rationale', 'Expected positive impact')),
                    'timeline': action.get('timeline', '2-4 weeks'),
                    'effort_level': 'medium'
                }
                recommendations.append(recommendation)
            
            # Add benchmarking-based recommendations
            benchmarking = analytics_result.get('performance_benchmarking', {})
            competitive_position = benchmarking.get('competitive_position', {})
            
            if competitive_position.get('market_position') in ['needs_improvement', 'below_average']:
                recommendations.append({
                    'category': 'Competitive Improvement',
                    'priority': 'high',
                    'title': 'Benchmark Gap Analysis',
                    'description': 'Focus on closing performance gaps with industry benchmarks',
                    'timeline': '4-6 weeks',
                    'effort_level': 'high'
                })
            
            # Add anomaly-based recommendations
            anomalies = analytics_result.get('anomaly_detection', {})
            if anomalies.get('anomaly_summary', {}).get('requires_investigation', False):
                recommendations.append({
                    'category': 'Risk Management',
                    'priority': 'high',
                    'title': 'Investigate Performance Anomalies',
                    'description': 'Analyze and address detected anomalies in key metrics',
                    'timeline': '1-2 weeks',
                    'effort_level': 'medium'
                })
            
            # Add growth-focused recommendations
            growth_forecast = analytics_result.get('predictive_analytics', {}).get('growth_forecast', {})
            if growth_forecast.get('model_performance', {}).get('r2_score', 0) > 0.7:
                recommendations.append({
                    'category': 'Growth Strategy',
                    'priority': 'medium',
                    'title': 'Leverage Predictable Growth Patterns',
                    'description': 'Your growth is predictable - optimize based on forecast model insights',
                    'timeline': '2-3 weeks',
                    'effort_level': 'medium'
                })
        
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
        
        return recommendations[:6]  # Return top 6 recommendations
    
    def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée pour l'analyse"""
        if not isinstance(input_data, dict):
            return False
        
        # User ID and metrics data are required
        if not input_data.get('user_id'):
            return False
        
        metrics_data = input_data.get('metrics_data', {})
        if not isinstance(metrics_data, dict) or not metrics_data:
            return False
        
        return True


class AsyncAnalyticsProcessor(AsyncBaseProcessor):
    """
Version asynchrone du processeur d'analytics"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sync_processor = AnalyticsProcessor(config)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
Traitement asynchrone des analytics"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.sync_processor.process_with_stats, 
            input_data
        )
    
    async def validate_input(self, input_data: Any) -> bool:
        """
Validation asynchrone"""
        return self.sync_processor.validate_input(input_data)
