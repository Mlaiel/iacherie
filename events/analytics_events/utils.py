"""Analytics Events Utilities Module

Ultra-advanced utility functions for analytics events processing,
data transformation, statistical analysis, and ML feature engineering.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
# [EMOJI_REMOVED]  WARNING: This code and concept are proprietary to Fahed Mlaiel.
    Any unauthorized use, copying, or distribution without explicit written 
    permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from functools import wraps
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import aioredis
import asyncpg
from pymongo import AsyncMongoClient
import hashids


logger = logging.getLogger(__name__)


class TimeSeriesAnalyzer:
    """
Ultra-advanced time series analysis for analytics events"""
    
    def __init__(self) -> None:
        self.scaler = StandardScaler()
        self.trend_detector = None
        self.seasonality_detector = None
    
    async def analyze_trend(self, data: List[Dict[str, Any]], 
                          time_column: str = 'timestamp',
                          value_column: str = 'value') -> Dict[str, Any]:
        """
        Analyze trend in time series data using advanced statistical methods
        
        Args:
            data: List of data points with timestamp and value
            time_column: Name of timestamp column
            value_column: Name of value column
            
        Returns:
            Dictionary with trend analysis results
        """
        try:
            df = pd.DataFrame(data)
            df[time_column] = pd.to_datetime(df[time_column])
            df = df.sort_values(time_column)
            
            # Extract time features
            df['hour'] = df[time_column].dt.hour
            df['day_of_week'] = df[time_column].dt.dayofweek
            df['day_of_month'] = df[time_column].dt.day
            df['month'] = df[time_column].dt.month
            df['quarter'] = df[time_column].dt.quarter
            
            values = df[value_column].values
            
            # Linear trend analysis
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Seasonal decomposition
            if len(values) >= 24:  # Need at least 24 points for hourly seasonality
                seasonal_component = self._extract_seasonality(values)
            else:
                seasonal_component = np.zeros_like(values)
            
            # Anomaly detection using z-score
            z_scores = np.abs(stats.zscore(values))
            anomalies = np.where(z_scores > 3)[0]
            
            # Moving averages
            ma_7 = df[value_column].rolling(window=min(7, len(df))).mean()
            ma_30 = df[value_column].rolling(window=min(30, len(df))).mean()
            
            # Volatility analysis
            returns = np.diff(values) / values[:-1]
            volatility = np.std(returns) if len(returns) > 0 else 0
            
            # Growth rate calculation
            if len(values) >= 2:
                growth_rate = (values[-1] - values[0]) / values[0] * 100
            else:
                growth_rate = 0
            
            # Forecast next values using simple linear regression
            if len(values) >= 3:
                next_values = []
                for i in range(1, 8):  # Forecast next 7 points
                    predicted = slope * (len(values) + i) + intercept
                    next_values.append(predicted)
            else:
                next_values = []
            
            return {
                'trend': {
                    'slope': float(slope),
                    'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                    'strength': abs(float(r_value)),
                    'p_value': float(p_value),
                    'confidence': 1 - float(p_value)
                },
                'seasonality': {
                    'detected': len(seasonal_component) > 0 and np.std(seasonal_component) > 0,
                    'component': seasonal_component.tolist() if len(seasonal_component) > 0 else [],
                    'strength': float(np.std(seasonal_component)) if len(seasonal_component) > 0 else 0
                },
                'anomalies': {
                    'count': len(anomalies),
                    'indices': anomalies.tolist(),
                    'percentage': len(anomalies) / len(values) * 100 if len(values) > 0 else 0
                },
                'statistics': {
                    'mean': float(np.mean(values)),
                    'median': float(np.median(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'volatility': float(volatility),
                    'growth_rate': float(growth_rate)
                },
                'moving_averages': {
                    'ma_7': ma_7.iloc[-1] if not ma_7.empty else None,
                    'ma_30': ma_30.iloc[-1] if not ma_30.empty else None
                },
                'forecast': {
                    'next_values': next_values,
                    'confidence_interval': [
                        [float(val - 2 * std_err), float(val + 2 * std_err)] 
                        for val in next_values
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            return {'error': str(e)}
    
    def _extract_seasonality(self, values: np.ndarray, period: int = 24) -> np.ndarray:
        """Extract seasonal component from time series"""
        try:
            if len(values) < period * 2:
                return np.zeros_like(values)
            
            # Simple seasonal decomposition
            seasonal = np.zeros_like(values)
            for i in range(len(values)):
                season_values = values[i::period]
                if len(season_values) > 1:
                    seasonal[i] = np.mean(season_values)
            
            # Remove trend from seasonal component
            trend = np.linspace(seasonal[0], seasonal[-1], len(seasonal))
            seasonal = seasonal - trend
            
            return seasonal
            
        except Exception:
            return np.zeros_like(values)


class FeatureEngineering:
    """
Advanced feature engineering for analytics events"""
    
    def __init__(self) -> None:
        self.scalers = {}
        self.encoders = {}
        self.feature_stats = {}
    
    async def engineer_features(self, data: Dict[str, Any], 
                              feature_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Engineer features from raw analytics data
        
        Args:
            data: Raw analytics data
            feature_config: Configuration for feature engineering
            
        Returns:
            Dictionary with engineered features
        """
        try:
            features = {}
            
            # Temporal features
            if 'timestamp' in data:
                timestamp = pd.to_datetime(data['timestamp'])
                features.update(self._extract_temporal_features(timestamp))
            
            # Numerical features
            if 'numerical_features' in feature_config:
                for feature_name in feature_config['numerical_features']:
                    if feature_name in data:
                        features.update(
                            self._engineer_numerical_features(
                                data[feature_name], feature_name
                            )
                        )
            
            # Categorical features
            if 'categorical_features' in feature_config:
                for feature_name in feature_config['categorical_features']:
                    if feature_name in data:
                        features.update(
                            self._engineer_categorical_features(
                                data[feature_name], feature_name
                            )
                        )
            
            # Text features
            if 'text_features' in feature_config:
                for feature_name in feature_config['text_features']:
                    if feature_name in data:
                        features.update(
                            self._engineer_text_features(
                                data[feature_name], feature_name
                            )
                        )
            
            # Interaction features
            if 'interaction_features' in feature_config:
                features.update(
                    self._create_interaction_features(
                        features, feature_config['interaction_features']
                    )
                )
            
            # Statistical aggregations
            if 'aggregation_features' in feature_config:
                features.update(
                    self._create_aggregation_features(
                        data, feature_config['aggregation_features']
                    )
                )
            
            return features
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {str(e)}")
            return {}
    
    def _extract_temporal_features(self, timestamp: pd.Timestamp) -> Dict[str, Any]:
        """Extract temporal features from timestamp"""
        return {
            'hour': timestamp.hour,
            'day_of_week': timestamp.dayofweek,
            'day_of_month': timestamp.day,
            'month': timestamp.month,
            'quarter': timestamp.quarter,
            'year': timestamp.year,
            'is_weekend': timestamp.dayofweek >= 5,
            'is_business_hour': 9 <= timestamp.hour <= 17,
            'is_evening': 18 <= timestamp.hour <= 23,
            'is_night': timestamp.hour <= 6 or timestamp.hour >= 22,
            'week_of_year': timestamp.isocalendar()[1],
            'day_of_year': timestamp.dayofyear,
            'seconds_since_midnight': timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
        }
    
    def _engineer_numerical_features(self, value: Union[int, float], 
                                   feature_name: str) -> Dict[str, Any]:
        """
Engineer features from numerical values"""
        features = {
            f"{feature_name}_original": value,
            f"{feature_name}_log": np.log1p(abs(value)) if value != 0 else 0,
            f"{feature_name}_sqrt": np.sqrt(abs(value)),
            f"{feature_name}_squared": value ** 2,
            f"{feature_name}_is_zero": 1 if value == 0 else 0,
            f"{feature_name}_is_positive": 1 if value > 0 else 0,
            f"{feature_name}_is_negative": 1 if value < 0 else 0,
            f"{feature_name}_abs": abs(value)
        }
        
        # Binning
        if value != 0:
            features[f"{feature_name}_bin_low"] = 1 if value < np.percentile([value], 25) else 0
            features[f"{feature_name}_bin_mid"] = 1 if np.percentile([value], 25) <= value < np.percentile([value], 75) else 0
            features[f"{feature_name}_bin_high"] = 1 if value >= np.percentile([value], 75) else 0
        
        return features
    
    def _engineer_categorical_features(self, value: str, 
                                     feature_name: str) -> Dict[str, Any]:
        """Engineer features from categorical values"""
        features = {
            f"{feature_name}_original": value,
            f"{feature_name}_length": len(str(value)),
            f"{feature_name}_word_count": len(str(value).split()),
            f"{feature_name}_has_numbers": 1 if any(c.isdigit() for c in str(value)) else 0,
            f"{feature_name}_has_special_chars": 1 if any(not c.isalnum() and not c.isspace() for c in str(value)) else 0,
            f"{feature_name}_uppercase_ratio": sum(1 for c in str(value) if c.isupper()) / len(str(value)) if str(value) else 0
        }
        
        # One-hot encoding for common values
        common_values = ['unknown', 'none', 'null', 'empty', 'default']
        for common_value in common_values:
            features[f"{feature_name}_is_{common_value}"] = 1 if str(value).lower() == common_value else 0
        
        return features
    
    def _engineer_text_features(self, text: str, feature_name: str) -> Dict[str, Any]:
        """Engineer features from text data"""
        features = {
            f"{feature_name}_length": len(text),
            f"{feature_name}_word_count": len(text.split()),
            f"{feature_name}_char_count": len(text),
            f"{feature_name}_sentence_count": len([s for s in text.split('.') if s.strip()]),
            f"{feature_name}_avg_word_length": np.mean([len(word) for word in text.split()]) if text.split() else 0,
            f"{feature_name}_uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            f"{feature_name}_digit_ratio": sum(1 for c in text if c.isdigit()) / len(text) if text else 0,
            f"{feature_name}_special_char_ratio": sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0,
            f"{feature_name}_exclamation_count": text.count('!'),
            f"{feature_name}_question_count": text.count('?'),
            f"{feature_name}_hashtag_count": text.count('#'),
            f"{feature_name}_mention_count": text.count('@'),
            f"{feature_name}_url_count": len([word for word in text.split() if 'http' in word or 'www' in word])
        }
        
        return features
    
    def _create_interaction_features(self, features: Dict[str, Any], 
                                   interaction_config: List[List[str]]) -> Dict[str, Any]:
        """Create interaction features between existing features"""
        interaction_features = {}
        
        for feature_pair in interaction_config:
            if len(feature_pair) == 2 and all(f in features for f in feature_pair):
                f1, f2 = feature_pair
                try:
                    # Multiplicative interaction
                    interaction_features[f"{f1}_x_{f2}"] = features[f1] * features[f2]
                    
                    # Additive interaction
                    interaction_features[f"{f1}_plus_{f2}"] = features[f1] + features[f2]
                    
                    # Ratio interaction (if denominator is not zero)
                    if features[f2] != 0:
                        interaction_features[f"{f1}_div_{f2}"] = features[f1] / features[f2]
                    
                    # Difference interaction
                    interaction_features[f"{f1}_minus_{f2}"] = features[f1] - features[f2]
                    
                except (TypeError, ZeroDivisionError):
                    continue
        
        return interaction_features
    
    def _create_aggregation_features(self, data: Dict[str, Any], 
                                   aggregation_config: Dict[str, List[str]]) -> Dict[str, Any]:
        """Create aggregation features from grouped data"""
        aggregation_features = {}
        
        for group_key, numeric_columns in aggregation_config.items():
            if group_key in data and isinstance(data[group_key], list):
                group_data = pd.DataFrame(data[group_key])
                
                for column in numeric_columns:
                    if column in group_data.columns:
                        values = pd.to_numeric(group_data[column], errors='coerce').dropna()
                        
                        if not values.empty:
                            aggregation_features.update({
                                f"{group_key}_{column}_mean": float(values.mean()),
                                f"{group_key}_{column}_median": float(values.median()),
                                f"{group_key}_{column}_std": float(values.std()),
                                f"{group_key}_{column}_min": float(values.min()),
                                f"{group_key}_{column}_max": float(values.max()),
                                f"{group_key}_{column}_sum": float(values.sum()),
                                f"{group_key}_{column}_count": len(values),
                                f"{group_key}_{column}_skew": float(values.skew()),
                                f"{group_key}_{column}_kurtosis": float(values.kurtosis())
                            })
        
        return aggregation_features


class EventHasher:
    """Advanced event hashing and ID generation utilities"""
    
    def __init__(self, salt -> None: str = "ia_influencer_2025") -> None:
        self.salt = salt
        self.hashids = hashids.Hashids(salt=salt, min_length=8)
    
    def generate_event_id(self, event_data: Dict[str, Any]) -> str:
        """Generate unique event ID based on event data"""
        # Create deterministic hash from event data
        event_string = json.dumps(event_data, sort_keys=True, default=str)
        event_hash = hashlib.sha256(f"{event_string}{self.salt}".encode()).hexdigest()
        
        # Convert to shorter hashid
        timestamp = int(time.time() * 1000)  # milliseconds
        hash_int = int(event_hash[:8], 16)  # Use first 8 chars of hash
        
        return self.hashids.encode(timestamp, hash_int)
    
    def generate_session_id(self, user_id: str, platform: str) -> str:
        """Generate session ID for user and platform"""
        timestamp = int(time.time())
        session_string = f"{user_id}_{platform}_{timestamp}"
        session_hash = hashlib.md5(session_string.encode()).hexdigest()
        
        return f"session_{session_hash[:16]}"
    
    def generate_fingerprint(self, content_data: Dict[str, Any]) -> str:
        """Generate content fingerprint for protection"""
        content_string = json.dumps(content_data, sort_keys=True)
        fingerprint = hashlib.sha512(content_string.encode()).hexdigest()
        
        return f"fp_{fingerprint[:32]}"
    
    def validate_event_id(self, event_id: str) -> bool:
        """Validate if event ID is properly formatted"""
        try:
            decoded = self.hashids.decode(event_id)
            return len(decoded) == 2 and all(isinstance(x, int) for x in decoded)
        except Exception:
            return False


class DataValidator:
    """
Advanced data validation for analytics events"""
    
    @staticmethod
    def validate_event_schema(event: Dict[str, Any], 
                            required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
Validate event against required schema"""
        errors = []
        
        # Check required fields
        for field in required_fields:
            if field not in event:
                errors.append(f"Missing required field: {field}")
        
        # Validate timestamp format
        if 'timestamp' in event:
            try:
                pd.to_datetime(event['timestamp'])
            except Exception:
                errors.append("Invalid timestamp format")
        
        # Validate numeric fields
        numeric_fields = ['user_id', 'content_id', 'value', 'score']
        for field in numeric_fields:
            if field in event and not isinstance(event[field], (int, float)):
                try:
                    float(event[field])
                except (ValueError, TypeError):
                    errors.append(f"Invalid numeric value for field: {field}")
        
        # Validate string fields
        string_fields = ['event_type', 'platform', 'category']
        for field in string_fields:
            if field in event and not isinstance(event[field], str):
                errors.append(f"Invalid string value for field: {field}")
        
        # Validate email format
        if 'email' in event:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(event['email'])):
                errors.append("Invalid email format")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_event_data(event: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Executing sanitize_event_data")
            
            # Implementation for sanitize_event_data
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"sanitize_event_data completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"sanitize_event_data failed: {e}")
            raise
class PerformanceOptimizer:
    """Performance optimization utilities for analytics processing"""
    
    @staticmethod
    def batch_process(items: List[Any], batch_size: int = 100) -> List[List[Any]]:
        """
Split items into batches for efficient processing"""
        batches = []
        for i in range(0, len(items), batch_size):
            batches.append(items[i:i + batch_size])
        return batches
    
    @staticmethod
    async def parallel_execute(coroutines: List[Callable], 
                             max_concurrency: int = 10) -> List[Any]:
        """
Execute coroutines in parallel with concurrency limit"""
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def execute_with_semaphore(coro) -> None:
            async with semaphore:
                return await coro
        
        tasks = [execute_with_semaphore(coro) for coro in coroutines]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    @staticmethod
    def memoize(func: Callable) -> Callable:
        """
Memoization decorator for expensive computations"""
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
        try:
            logger.info(f"Executing execute_with_semaphore")
            
            # Implementation for execute_with_semaphore
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"execute_with_semaphore completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"execute_with_semaphore failed: {e}")
            raise
                cache[key] = func(*args, **kwargs)
            return cache[key]
        
        return wrapper
    
    @staticmethod
    def rate_limit(calls_per_second -> None: int) -> None:
        """
Rate limiting decorator"""
        min_interval = 1.0 / calls_per_second
        last_called = [0.0]
        
        def decorator(func) -> None:
            @wraps(func)
            def wrapper(*args, **kwargs) -> None:
                elapsed = time.time() - last_called[0]
                left_to_wait = min_interval - elapsed
                if left_to_wait > 0:
                    time.sleep(left_to_wait)
                ret = func(*args, **kwargs)
                last_called[0] = time.time()
                return ret
            return wrapper
        return decorator


class StatisticalAnalyzer:
    """
Advanced statistical analysis utilities"""
    
    @staticmethod
    def calculate_correlation_matrix(data: pd.DataFrame) -> Dict[str, Any]:
        """
Calculate correlation matrix with statistical significance"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        corr_matrix = data[numeric_cols].corr()
        
        # Calculate p-values for correlations
        p_values = np.zeros_like(corr_matrix)
        n = len(data)
        
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i != j:
                    corr_coef = corr_matrix.iloc[i, j]
                    # Calculate t-statistic and p-value
                    t_stat = corr_coef * np.sqrt((n - 2) / (1 - corr_coef**2))
                    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
                    p_values[i, j] = p_value
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'p_values': pd.DataFrame(p_values, 
                                   index=numeric_cols, 
                                   columns=numeric_cols).to_dict(),
            'significant_correlations': [
                {'feature1': col1, 'feature2': col2, 'correlation': corr_matrix.loc[col1, col2]}
                for col1 in numeric_cols
                for col2 in numeric_cols
                if col1 != col2 and abs(corr_matrix.loc[col1, col2]) > 0.5
            ]
        }
    
    @staticmethod
    def detect_outliers(data: np.ndarray, method: str = 'iqr') -> Dict[str, Any]:
        """
Detect outliers using various statistical methods"""
        outliers = {}
        
        if method == 'iqr':
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outlier_indices = np.where((data < lower_bound) | (data > upper_bound))[0]
            
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(data))
            outlier_indices = np.where(z_scores > 3)[0]
            
        elif method == 'isolation_forest':
            from sklearn.ensemble import IsolationForest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outlier_labels = iso_forest.fit_predict(data.reshape(-1, 1))
            outlier_indices = np.where(outlier_labels == -1)[0]
        
        outliers = {
            'method': method,
            'outlier_indices': outlier_indices.tolist(),
            'outlier_values': data[outlier_indices].tolist(),
            'outlier_count': len(outlier_indices),
            'outlier_percentage': len(outlier_indices) / len(data) * 100 if len(data) > 0 else 0
        }
        
        return outliers
    
    @staticmethod
    def hypothesis_test(sample1: np.ndarray, sample2: np.ndarray, 
                       test_type: str = 'ttest') -> Dict[str, Any]:
        """
Perform hypothesis testing between two samples"""
        results = {}
        
        if test_type == 'ttest':
            # Independent t-test
            t_stat, p_value = stats.ttest_ind(sample1, sample2)
            results = {
                'test_type': 'Independent t-test',
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'effect_size': (np.mean(sample1) - np.mean(sample2)) / np.sqrt((np.var(sample1) + np.var(sample2)) / 2)
            }
            
        elif test_type == 'mannwhitney':
            # Mann-Whitney U test
            u_stat, p_value = stats.mannwhitneyu(sample1, sample2)
            results = {
                'test_type': 'Mann-Whitney U test',
                'u_statistic': float(u_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
            
        elif test_type == 'ks':
            # Kolmogorov-Smirnov test
            ks_stat, p_value = stats.ks_2samp(sample1, sample2)
            results = {
                'test_type': 'Kolmogorov-Smirnov test',
                'ks_statistic': float(ks_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
        
        return results


# Utility functions for common analytics tasks
async def calculate_engagement_metrics(events: List[Dict[str, Any]]) -> Dict[str, float]:
    """
Calculate comprehensive engagement metrics from events"""
    if not events:
        return {}
    
    df = pd.DataFrame(events)
    
    metrics = {
        'total_events': len(events),
        'unique_users': df['user_id'].nunique() if 'user_id' in df.columns else 0,
        'avg_events_per_user': len(events) / df['user_id'].nunique() if 'user_id' in df.columns and df['user_id'].nunique() > 0 else 0,
        'event_rate_per_hour': len(events) / 24 if len(events) > 0 else 0  # Assuming events are from last 24h
    }
    
    # Calculate engagement scores if available
    if 'engagement_score' in df.columns:
        metrics.update({
            'avg_engagement_score': float(df['engagement_score'].mean()),
            'median_engagement_score': float(df['engagement_score'].median()),
            'max_engagement_score': float(df['engagement_score'].max()),
            'min_engagement_score': float(df['engagement_score'].min()),
            'engagement_score_std': float(df['engagement_score'].std())
        })
    
    return metrics


async def calculate_revenue_metrics(transactions: List[Dict[str, Any]]) -> Dict[str, float]:
    """
Calculate comprehensive revenue metrics from transaction data"""
    if not transactions:
        return {}
    
    df = pd.DataFrame(transactions)
    
    if 'amount' not in df.columns:
        return {}
    
    amounts = df['amount'].astype(float)
    
    metrics = {
        'total_revenue': float(amounts.sum()),
        'avg_transaction_amount': float(amounts.mean()),
        'median_transaction_amount': float(amounts.median()),
        'max_transaction_amount': float(amounts.max()),
        'min_transaction_amount': float(amounts.min()),
        'transaction_count': len(transactions),
        'revenue_std': float(amounts.std())
    }
    
    # Calculate additional metrics if user data is available
    if 'user_id' in df.columns:
        user_revenues = df.groupby('user_id')['amount'].sum()
        metrics.update({
            'unique_paying_users': df['user_id'].nunique(),
            'avg_revenue_per_user': float(user_revenues.mean()),
            'median_revenue_per_user': float(user_revenues.median()),
            'top_10_percent_revenue_share': float(user_revenues.nlargest(int(len(user_revenues) * 0.1)).sum() / amounts.sum()) if len(user_revenues) > 0 else 0
        })
    
    return metrics

# File has syntax issues - needs manual review