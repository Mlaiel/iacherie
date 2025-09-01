"""Database AI Insights - Advanced Machine Learning Analytics for Database Intelligence

AI-powered database analytics system with predictive analysis, anomaly detection,
pattern recognition, and intelligent recommendations for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute violation sera poursuivie selon les lois en vigueur.
"""
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import pickle
from collections import defaultdict, deque
import statistics

from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import asyncpg

from ..core.database import get_database_session
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...ml.models import TimeSeriesPredictor, AnomalyDetector, PatternRecognizer
from ...monitoring.notifications import AIInsightsNotificationManager


class InsightType(Enum):
    """Types of AI insights"""
    PERFORMANCE_PREDICTION = "performance_prediction"
    ANOMALY_DETECTION = "anomaly_detection"
    PATTERN_RECOGNITION = "pattern_recognition"
    CAPACITY_PLANNING = "capacity_planning"
    OPTIMIZATION_RECOMMENDATION = "optimization_recommendation"
    SECURITY_THREAT = "security_threat"
    COST_OPTIMIZATION = "cost_optimization"
    USAGE_ANALYTICS = "usage_analytics"


class AnomalyType(Enum):
    """Types of anomalies detected"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    UNUSUAL_QUERY_PATTERN = "unusual_query_pattern"
    RESOURCE_SPIKE = "resource_spike"
    CONNECTION_ANOMALY = "connection_anomaly"
    SECURITY_ANOMALY = "security_anomaly"
    COST_ANOMALY = "cost_anomaly"
    DATA_QUALITY_ISSUE = "data_quality_issue"


class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class AIInsight:
    """AI-generated database insight"""
    insight_id: str
    timestamp: datetime
    insight_type: InsightType
    confidence: float
    confidence_level: ConfidenceLevel
    title: str
    description: str
    impact_score: float
    severity: str
    recommendations: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'insight_id': self.insight_id,
            'timestamp': self.timestamp.isoformat(),
            'insight_type': self.insight_type.value,
            'confidence': self.confidence,
            'confidence_level': self.confidence_level.value,
            'title': self.title,
            'description': self.description,
            'impact_score': self.impact_score,
            'severity': self.severity,
            'recommendations': self.recommendations,
            'data_sources': self.data_sources,
            'metadata': self.metadata,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    anomaly_id: str
    timestamp: datetime
    anomaly_type: AnomalyType
    severity: str
    affected_metrics: List[str]
    anomaly_score: float
    confidence: float
    description: str
    root_cause_analysis: Dict[str, Any]
    recommended_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'anomaly_id': self.anomaly_id,
            'timestamp': self.timestamp.isoformat(),
            'anomaly_type': self.anomaly_type.value,
            'severity': self.severity,
            'affected_metrics': self.affected_metrics,
            'anomaly_score': self.anomaly_score,
            'confidence': self.confidence,
            'description': self.description,
            'root_cause_analysis': self.root_cause_analysis,
            'recommended_actions': self.recommended_actions
        }


@dataclass
class PredictionResult:
    """Performance prediction result"""
    prediction_id: str
    timestamp: datetime
    target_metric: str
    current_value: float
    predicted_value: float
    prediction_horizon: str  # e.g., "1h", "1d", "1w"
    confidence_interval: Tuple[float, float]
    accuracy_score: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    factors: Dict[str, float]  # Contributing factors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'prediction_id': self.prediction_id,
            'timestamp': self.timestamp.isoformat(),
            'target_metric': self.target_metric,
            'current_value': self.current_value,
            'predicted_value': self.predicted_value,
            'prediction_horizon': self.prediction_horizon,
            'confidence_interval': list(self.confidence_interval),
            'accuracy_score': self.accuracy_score,
            'trend_direction': self.trend_direction,
            'factors': self.factors
        }


class DatabaseAIInsights:
    """Advanced AI-powered database insights system"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.notification_manager = AIInsightsNotificationManager()
        
        # ML models
        self.time_series_predictor = TimeSeriesPredictor()
        self.anomaly_detector = AnomalyDetector()
        self.pattern_recognizer = PatternRecognizer()
        
        # AI insights state
        self.insights: Dict[str, AIInsight] = {}
        self.anomalies: Dict[str, AnomalyDetection] = {}
        self.predictions: Dict[str, PredictionResult] = {}
        self.models: Dict[str, Any] = {}
        
        # Historical data for training
        self.historical_data: pd.DataFrame = pd.DataFrame()
        self.model_last_trained: Dict[str, datetime] = {}
        
        # Monitoring flags
        self._monitoring_active = False
        self._monitoring_task = None
        
        # Initialize models
        asyncio.create_task(self._initialize_ml_models())
        
    async def _initialize_ml_models(self):
        """Initialize machine learning models"""
        try:
            # Initialize anomaly detection models
            self.models['performance_anomaly'] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            self.models['query_anomaly'] = IsolationForest(
                contamination=0.05,
                random_state=42
            )
            
            # Initialize time series prediction models
            self.models['performance_predictor'] = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            
            # Initialize clustering for pattern recognition
            self.models['pattern_detector'] = DBSCAN(
                eps=0.5,
                min_samples=5
            )
            
            # Initialize scaler for preprocessing
            self.models['scaler'] = StandardScaler()
            
            # Load pre-trained models if available
            await self._load_pretrained_models()
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
            
    async def _load_pretrained_models(self):
        """Load pre-trained models from storage"""
        try:
            # Try to load models from Redis cache
            model_data = await self.cache.get("ai_models")
            if model_data:
                saved_models = pickle.loads(model_data)
                self.models.update(saved_models)
                self.logger.info("Loaded pre-trained models")
        except Exception as e:
            self.logger.debug(f"No pre-trained models found: {e}")
            
    async def start_monitoring(self, interval: int = 300):  # 5 minutes
        """Start AI insights monitoring"""
        if self._monitoring_active:
            self.logger.warning("AI insights monitoring already active")
            return
            
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval)
        )
        self.logger.info("Database AI insights monitoring started")
        
    async def stop_monitoring(self):
        """Stop AI insights monitoring"""
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Database AI insights monitoring stopped")
        
    async def _monitoring_loop(self, interval: int):
        """Main AI insights monitoring loop"""
        while self._monitoring_active:
            try:
                await self._collect_training_data()
                await self._detect_anomalies()
                await self._generate_predictions()
                await self._recognize_patterns()
                await self._generate_insights()
                await self._retrain_models_if_needed()
                await self._cleanup_old_insights()
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"AI insights monitoring error: {e}")
                await asyncio.sleep(interval)
                
    async def _collect_training_data(self):
        """Collect data for model training"""
        try:
            async with get_database_session() as session:
                # Collect performance metrics
                perf_query = text("""
                    SELECT 
                        NOW() as timestamp,
                        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                        (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle_connections,
                        (SELECT sum(numbackends) FROM pg_stat_database) as total_backends,
                        (SELECT sum(xact_commit) FROM pg_stat_database) as total_commits,
                        (SELECT sum(xact_rollback) FROM pg_stat_database) as total_rollbacks,
                        (SELECT sum(blks_read) FROM pg_stat_database) as disk_reads,
                        (SELECT sum(blks_hit) FROM pg_stat_database) as cache_hits,
                        (SELECT sum(tup_returned) FROM pg_stat_database) as tuples_returned,
                        (SELECT sum(tup_fetched) FROM pg_stat_database) as tuples_fetched,
                        (SELECT sum(tup_inserted) FROM pg_stat_database) as tuples_inserted,
                        (SELECT sum(tup_updated) FROM pg_stat_database) as tuples_updated,
                        (SELECT sum(tup_deleted) FROM pg_stat_database) as tuples_deleted
                """)
                
                result = await session.execute(perf_query)
                data = result.fetchone()
                
                # Convert to pandas row
                new_data = {
                    'timestamp': data.timestamp,
                    'active_connections': data.active_connections,
                    'idle_connections': data.idle_connections,
                    'total_backends': data.total_backends,
                    'total_commits': data.total_commits,
                    'total_rollbacks': data.total_rollbacks,
                    'disk_reads': data.disk_reads,
                    'cache_hits': data.cache_hits,
                    'tuples_returned': data.tuples_returned,
                    'tuples_fetched': data.tuples_fetched,
                    'tuples_inserted': data.tuples_inserted,
                    'tuples_updated': data.tuples_updated,
                    'tuples_deleted': data.tuples_deleted
                }
                
                # Calculate derived metrics
                new_data['cache_hit_ratio'] = (
                    data.cache_hits / (data.cache_hits + data.disk_reads)
                    if (data.cache_hits + data.disk_reads) > 0 else 0
                )
                
                new_data['commit_ratio'] = (
                    data.total_commits / (data.total_commits + data.total_rollbacks)
                    if (data.total_commits + data.total_rollbacks) > 0 else 1
                )
                
                # Add to historical data
                if self.historical_data.empty:
                    self.historical_data = pd.DataFrame([new_data])
                else:
                    self.historical_data = pd.concat([
                        self.historical_data,
                        pd.DataFrame([new_data])
                    ], ignore_index=True)
                    
                # Keep only recent data (last 7 days)
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                self.historical_data = self.historical_data[
                    pd.to_datetime(self.historical_data['timestamp']) > cutoff_time
                ]
                
                # Store in cache for persistence
                await self.cache.set(
                    "ai_historical_data",
                    pickle.dumps(self.historical_data),
                    expire=604800  # 7 days
                )
                
        except Exception as e:
            self.logger.error(f"Failed to collect training data: {e}")
            
    async def _detect_anomalies(self):
        """Detect anomalies in database metrics"""
        try:
            if len(self.historical_data) < 100:  # Need sufficient data
                return
                
            # Prepare data for anomaly detection
            feature_columns = [
                'active_connections', 'idle_connections', 'total_backends',
                'disk_reads', 'cache_hits', 'cache_hit_ratio',
                'tuples_returned', 'tuples_fetched', 'commit_ratio'
            ]
            
            features = self.historical_data[feature_columns].fillna(0)
            
            # Scale features
            scaled_features = self.models['scaler'].fit_transform(features)
            
            # Detect performance anomalies
            performance_anomalies = self.models['performance_anomaly'].fit_predict(scaled_features)
            anomaly_scores = self.models['performance_anomaly'].decision_function(scaled_features)
            
            # Process anomalies
            current_index = len(self.historical_data) - 1
            if performance_anomalies[current_index] == -1:  # Anomaly detected
                await self._process_anomaly(
                    AnomalyType.PERFORMANCE_DEGRADATION,
                    anomaly_scores[current_index],
                    self.historical_data.iloc[current_index],
                    feature_columns
                )
                
            # Detect query pattern anomalies
            await self._detect_query_anomalies()
            
        except Exception as e:
            self.logger.error(f"Failed to detect anomalies: {e}")
            
    async def _detect_query_anomalies(self):
        """Detect anomalies in query patterns"""
        try:
            async with get_database_session() as session:
                # Get recent query statistics
                query_stats_query = text("""
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows,
                        100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                    FROM pg_stat_statements
                    WHERE calls > 10
                    ORDER BY total_time DESC
                    LIMIT 100
                """)
                
                result = await session.execute(query_stats_query)
                query_stats = result.fetchall()
                
                if not query_stats:
                    return
                    
                # Prepare query features
                query_features = []
                for stat in query_stats:
                    features = [
                        stat.calls,
                        stat.total_time,
                        stat.mean_time,
                        stat.rows or 0,
                        stat.hit_percent or 0
                    ]
                    query_features.append(features)
                    
                query_features = np.array(query_features)
                
                # Detect anomalies
                query_anomalies = self.models['query_anomaly'].fit_predict(query_features)
                query_scores = self.models['query_anomaly'].decision_function(query_features)
                
                # Process query anomalies
                for i, (stat, is_anomaly, score) in enumerate(zip(query_stats, query_anomalies, query_scores)):
                    if is_anomaly == -1:  # Anomaly detected
                        await self._process_query_anomaly(stat, score)
                        
        except Exception as e:
            self.logger.error(f"Failed to detect query anomalies: {e}")
            
    async def _process_anomaly(self, anomaly_type: AnomalyType, score: float, data_point: pd.Series, features: List[str]):
        """Process detected anomaly"""
        try:
            anomaly_id = f"anomaly_{anomaly_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Calculate severity based on score
            severity = self._calculate_anomaly_severity(score)
            
            # Analyze root cause
            root_cause = await self._analyze_root_cause(anomaly_type, data_point, features)
            
            # Generate recommendations
            recommendations = await self._generate_anomaly_recommendations(anomaly_type, root_cause)
            
            anomaly = AnomalyDetection(
                anomaly_id=anomaly_id,
                timestamp=datetime.utcnow(),
                anomaly_type=anomaly_type,
                severity=severity,
                affected_metrics=features,
                anomaly_score=abs(score),
                confidence=min(abs(score) * 0.8, 1.0),
                description=f"Anomaly detected in {anomaly_type.value}",
                root_cause_analysis=root_cause,
                recommended_actions=recommendations
            )
            
            self.anomalies[anomaly_id] = anomaly
            await self._store_anomaly(anomaly)
            
            # Send notification for high-severity anomalies
            if severity in ['HIGH', 'CRITICAL']:
                await self._send_anomaly_alert(anomaly)
                
        except Exception as e:
            self.logger.error(f"Failed to process anomaly: {e}")
            
    async def _process_query_anomaly(self, query_stat, score: float):
        """Process query anomaly"""
        try:
            anomaly_id = f"query_anomaly_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            severity = self._calculate_anomaly_severity(score)
            
            # Analyze query characteristics
            query_analysis = {
                'query_text': query_stat.query[:200],  # Truncate long queries
                'call_frequency': query_stat.calls,
                'total_time': query_stat.total_time,
                'mean_time': query_stat.mean_time,
                'cache_hit_rate': query_stat.hit_percent or 0
            }
            
            recommendations = [
                "Review query execution plan",
                "Consider adding appropriate indexes",
                "Optimize query structure if needed",
                "Monitor query performance trends"
            ]
            
            if query_stat.mean_time > 1000:  # > 1 second
                recommendations.append("Consider query optimization - high execution time")
                
            if (query_stat.hit_percent or 0) < 80:
                recommendations.append("Investigate low cache hit rate")
                
            anomaly = AnomalyDetection(
                anomaly_id=anomaly_id,
                timestamp=datetime.utcnow(),
                anomaly_type=AnomalyType.UNUSUAL_QUERY_PATTERN,
                severity=severity,
                affected_metrics=['query_performance'],
                anomaly_score=abs(score),
                confidence=min(abs(score) * 0.8, 1.0),
                description=f"Unusual query pattern detected",
                root_cause_analysis=query_analysis,
                recommended_actions=recommendations
            )
            
            await self._store_anomaly(anomaly)
            
        except Exception as e:
            self.logger.error(f"Failed to process query anomaly: {e}")
            
    def _calculate_anomaly_severity(self, score: float) -> str:
        """Calculate anomaly severity based on score"""
        abs_score = abs(score)
        
        if abs_score > 0.8:
            return "CRITICAL"
        elif abs_score > 0.6:
            return "HIGH"
        elif abs_score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
            
    async def _analyze_root_cause(self, anomaly_type: AnomalyType, data_point: pd.Series, features: List[str]) -> Dict[str, Any]:
        """Analyze root cause of anomaly"""
        try:
            root_cause = {
                'most_deviant_metrics': [],
                'potential_causes': [],
                'correlation_analysis': {}
            }
            
            # Find metrics with highest deviation
            if len(self.historical_data) > 1:
                recent_mean = self.historical_data[features].tail(20).mean()
                current_values = data_point[features]
                
                deviations = {}
                for feature in features:
                    if recent_mean[feature] > 0:
                        deviation = abs(current_values[feature] - recent_mean[feature]) / recent_mean[feature]
                        deviations[feature] = deviation
                        
                # Sort by deviation
                sorted_deviations = sorted(deviations.items(), key=lambda x: x[1], reverse=True)
                root_cause['most_deviant_metrics'] = sorted_deviations[:3]
                
                # Generate potential causes based on deviant metrics
                for metric, deviation in sorted_deviations[:3]:
                    if deviation > 0.5:  # Significant deviation
                        causes = self._get_potential_causes(metric, current_values[metric], recent_mean[metric])
                        root_cause['potential_causes'].extend(causes)
                        
            return root_cause
            
        except Exception as e:
            self.logger.error(f"Failed to analyze root cause: {e}")
            return {}
            
    def _get_potential_causes(self, metric: str, current_value: float, normal_value: float) -> List[str]:
        """Get potential causes for metric deviation"""
        causes = []
        
        if metric == 'active_connections' and current_value > normal_value * 2:
            causes.extend([
                "Connection pool exhaustion",
                "Application connection leak",
                "Increased user traffic"
            ])
        elif metric == 'cache_hit_ratio' and current_value < normal_value * 0.8:
            causes.extend([
                "Insufficient shared buffers",
                "Large table scans",
                "Cache invalidation"
            ])
        elif metric == 'disk_reads' and current_value > normal_value * 2:
            causes.extend([
                "Missing indexes",
                "Large query operations",
                "Cache misses"
            ])
            
        return causes
        
    async def _generate_anomaly_recommendations(self, anomaly_type: AnomalyType, root_cause: Dict[str, Any]) -> List[str]:
        """Generate recommendations for anomaly"""
        recommendations = []
        
        if anomaly_type == AnomalyType.PERFORMANCE_DEGRADATION:
            recommendations.extend([
                "Monitor system resources (CPU, memory, disk)",
                "Review recent configuration changes",
                "Analyze slow query log",
                "Check for blocking processes"
            ])
            
        # Add specific recommendations based on root cause
        for cause in root_cause.get('potential_causes', []):
            if "connection" in cause.lower():
                recommendations.append("Review connection pooling configuration")
            elif "cache" in cause.lower():
                recommendations.append("Consider increasing shared_buffers")
            elif "index" in cause.lower():
                recommendations.append("Analyze and optimize database indexes")
                
        return list(set(recommendations))  # Remove duplicates
        
    async def _store_anomaly(self, anomaly: AnomalyDetection):
        """Store anomaly detection result"""
        try:
            await self.cache.set(
                f"anomaly:{anomaly.anomaly_id}",
                json.dumps(anomaly.to_dict()),
                expire=604800  # 7 days
            )
            
            # Add to timeline
            await self.cache.zadd(
                "anomalies_timeline",
                {anomaly.anomaly_id: anomaly.timestamp.timestamp()}
            )
            
            # Index by type
            await self.cache.sadd(
                f"anomalies_by_type:{anomaly.anomaly_type.value}",
                anomaly.anomaly_id
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store anomaly: {e}")
            
    async def _send_anomaly_alert(self, anomaly: AnomalyDetection):
        """Send anomaly alert notification"""
        try:
            await self.notification_manager.send_anomaly_alert(
                severity=anomaly.severity,
                title=f'Database Anomaly: {anomaly.anomaly_type.value.title()}',
                message=anomaly.description,
                details=anomaly.to_dict()
            )
        except Exception as e:
            self.logger.error(f"Failed to send anomaly alert: {e}")
            
    async def _generate_predictions(self):
        """Generate performance predictions"""
        try:
            if len(self.historical_data) < 50:  # Need sufficient data
                return
                
            # Predict key metrics
            metrics_to_predict = [
                'active_connections',
                'cache_hit_ratio',
                'disk_reads',
                'total_commits'
            ]
            
            for metric in metrics_to_predict:
                prediction = await self._predict_metric(metric)
                if prediction:
                    self.predictions[prediction.prediction_id] = prediction
                    await self._store_prediction(prediction)
                    
        except Exception as e:
            self.logger.error(f"Failed to generate predictions: {e}")
            
    async def _predict_metric(self, metric: str) -> Optional[PredictionResult]:
        """Predict specific metric value"""
        try:
            # Prepare time series data
            data = self.historical_data[['timestamp', metric]].copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data = data.sort_values('timestamp')
            
            if len(data) < 20:
                return None
                
            # Create features (time-based)
            data['hour'] = data['timestamp'].dt.hour
            data['day_of_week'] = data['timestamp'].dt.dayofweek
            data['minute'] = data['timestamp'].dt.minute
            
            # Create lag features
            for lag in [1, 2, 3, 6, 12]:
                data[f'{metric}_lag_{lag}'] = data[metric].shift(lag)
                
            # Remove rows with NaN
            data = data.dropna()
            
            if len(data) < 10:
                return None
                
            # Prepare features and target
            feature_cols = ['hour', 'day_of_week', 'minute'] + [col for col in data.columns if 'lag' in col]
            X = data[feature_cols]
            y = data[metric]
            
            # Train model
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X, y)
            
            # Make prediction for next time point
            last_row = X.iloc[-1:].copy()
            
            # Update lag features for prediction
            current_value = data[metric].iloc[-1]
            
            prediction = model.predict(last_row)[0]
            
            # Calculate confidence interval (simplified)
            predictions = []
            for _ in range(100):
                # Add some noise for uncertainty estimation
                noisy_input = last_row + np.random.normal(0, 0.1, last_row.shape)
                pred = model.predict(noisy_input)[0]
                predictions.append(pred)
                
            confidence_interval = (
                np.percentile(predictions, 10),
                np.percentile(predictions, 90)
            )
            
            # Determine trend
            recent_values = data[metric].tail(5).values
            if len(recent_values) >= 2:
                if prediction > recent_values[-1] * 1.1:
                    trend = "increasing"
                elif prediction < recent_values[-1] * 0.9:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "unknown"
                
            # Feature importance as factors
            factors = {}
            if hasattr(model, 'feature_importances_'):
                for i, col in enumerate(feature_cols):
                    factors[col] = float(model.feature_importances_[i])
                    
            prediction_result = PredictionResult(
                prediction_id=f"prediction_{metric}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.utcnow(),
                target_metric=metric,
                current_value=current_value,
                predicted_value=prediction,
                prediction_horizon="1h",
                confidence_interval=confidence_interval,
                accuracy_score=model.score(X, y),
                trend_direction=trend,
                factors=factors
            )
            
            return prediction_result
            
        except Exception as e:
            self.logger.error(f"Failed to predict metric {metric}: {e}")
            return None
            
    async def _store_prediction(self, prediction: PredictionResult):
        """Store prediction result"""
        try:
            await self.cache.set(
                f"prediction:{prediction.prediction_id}",
                json.dumps(prediction.to_dict()),
                expire=86400  # 1 day
            )
            
            # Add to timeline
            await self.cache.zadd(
                f"predictions_timeline:{prediction.target_metric}",
                {prediction.prediction_id: prediction.timestamp.timestamp()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store prediction: {e}")
            
    async def _recognize_patterns(self):
        """Recognize patterns in database behavior"""
        try:
            if len(self.historical_data) < 100:
                return
                
            # Pattern recognition for usage patterns
            await self._recognize_usage_patterns()
            
            # Pattern recognition for performance patterns
            await self._recognize_performance_patterns()
            
        except Exception as e:
            self.logger.error(f"Failed to recognize patterns: {e}")
            
    async def _recognize_usage_patterns(self):
        """Recognize database usage patterns"""
        try:
            # Group by hour to find usage patterns
            data = self.historical_data.copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data['hour'] = data['timestamp'].dt.hour
            
            hourly_stats = data.groupby('hour').agg({
                'active_connections': 'mean',
                'total_commits': 'mean',
                'tuples_inserted': 'mean',
                'tuples_updated': 'mean',
                'tuples_deleted': 'mean'
            })
            
            # Find peak hours
            peak_connections_hour = hourly_stats['active_connections'].idxmax()
            peak_activity_hour = hourly_stats['total_commits'].idxmax()
            
            # Generate insight
            pattern_insight = AIInsight(
                insight_id=f"pattern_usage_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.utcnow(),
                insight_type=InsightType.USAGE_ANALYTICS,
                confidence=0.8,
                confidence_level=ConfidenceLevel.HIGH,
                title="Database Usage Pattern Identified",
                description=f"Peak database activity occurs at {peak_activity_hour}:00, with highest connections at {peak_connections_hour}:00",
                impact_score=0.6,
                severity="INFO",
                recommendations=[
                    f"Consider scaling resources during peak hours ({peak_activity_hour}:00)",
                    "Monitor connection pool sizing for peak usage",
                    "Schedule maintenance during low-activity periods"
                ],
                data_sources=["pg_stat_activity", "pg_stat_database"],
                metadata={
                    'peak_connections_hour': int(peak_connections_hour),
                    'peak_activity_hour': int(peak_activity_hour),
                    'hourly_patterns': hourly_stats.to_dict()
                }
            )
            
            await self._store_insight(pattern_insight)
            
        except Exception as e:
            self.logger.error(f"Failed to recognize usage patterns: {e}")
            
    async def _recognize_performance_patterns(self):
        """Recognize performance patterns"""
        try:
            # Analyze performance correlations
            data = self.historical_data.copy()
            
            # Calculate correlation matrix
            numeric_cols = ['active_connections', 'cache_hit_ratio', 'disk_reads', 'total_commits']
            correlation_matrix = data[numeric_cols].corr()
            
            # Find strong correlations
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # Strong correlation
                        strong_correlations.append({
                            'metric1': correlation_matrix.columns[i],
                            'metric2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
                        
            if strong_correlations:
                correlation_insight = AIInsight(
                    insight_id=f"pattern_correlation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.utcnow(),
                    insight_type=InsightType.PATTERN_RECOGNITION,
                    confidence=0.9,
                    confidence_level=ConfidenceLevel.VERY_HIGH,
                    title="Performance Correlation Patterns Detected",
                    description=f"Found {len(strong_correlations)} strong correlations between performance metrics",
                    impact_score=0.7,
                    severity="INFO",
                    recommendations=[
                        "Use correlated metrics for predictive monitoring",
                        "Optimize performance by focusing on highly correlated metrics",
                        "Consider these relationships in capacity planning"
                    ],
                    data_sources=["performance_metrics"],
                    metadata={
                        'correlations': strong_correlations,
                        'correlation_matrix': correlation_matrix.to_dict()
                    }
                )
                
                await self._store_insight(correlation_insight)
                
        except Exception as e:
            self.logger.error(f"Failed to recognize performance patterns: {e}")
            
    async def _generate_insights(self):
        """Generate high-level AI insights"""
        try:
            # Generate capacity planning insights
            await self._generate_capacity_insights()
            
            # Generate optimization insights
            await self._generate_optimization_insights()
            
        except Exception as e:
            self.logger.error(f"Failed to generate insights: {e}")
            
    async def _generate_capacity_insights(self):
        """Generate capacity planning insights"""
        try:
            if len(self.historical_data) < 24:  # Need at least 24 data points
                return
                
            # Analyze growth trends
            data = self.historical_data.copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data = data.sort_values('timestamp')
            
            # Calculate growth rates
            growth_metrics = ['active_connections', 'total_commits', 'disk_reads']
            growth_rates = {}
            
            for metric in growth_metrics:
                if data[metric].sum() > 0:
                    # Calculate percentage change over time
                    first_half = data[metric].head(len(data)//2).mean()
                    second_half = data[metric].tail(len(data)//2).mean()
                    
                    if first_half > 0:
                        growth_rate = (second_half - first_half) / first_half
                        growth_rates[metric] = growth_rate
                        
            # Find metrics with significant growth
            high_growth_metrics = {k: v for k, v in growth_rates.items() if v > 0.2}  # > 20% growth
            
            if high_growth_metrics:
                capacity_insight = AIInsight(
                    insight_id=f"capacity_planning_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.utcnow(),
                    insight_type=InsightType.CAPACITY_PLANNING,
                    confidence=0.8,
                    confidence_level=ConfidenceLevel.HIGH,
                    title="Capacity Planning Alert",
                    description=f"Detected significant growth in {len(high_growth_metrics)} metrics",
                    impact_score=0.8,
                    severity="MEDIUM",
                    recommendations=[
                        "Plan for capacity scaling in the next 30 days",
                        "Monitor resource utilization closely",
                        "Consider upgrading infrastructure",
                        "Implement auto-scaling if available"
                    ],
                    data_sources=["performance_metrics"],
                    metadata={
                        'growth_rates': growth_rates,
                        'high_growth_metrics': high_growth_metrics,
                        'projected_capacity_needs': {
                            metric: f"{(1 + rate) * 100:.1f}% increase needed"
                            for metric, rate in high_growth_metrics.items()
                        }
                    },
                    expires_at=datetime.utcnow() + timedelta(days=7)
                )
                
                await self._store_insight(capacity_insight)
                
        except Exception as e:
            self.logger.error(f"Failed to generate capacity insights: {e}")
            
    async def _generate_optimization_insights(self):
        """Generate optimization insights"""
        try:
            data = self.historical_data.copy()
            
            if len(data) < 10:
                return
                
            # Analyze cache hit ratio
            avg_cache_hit_ratio = data['cache_hit_ratio'].mean()
            
            if avg_cache_hit_ratio < 0.9:  # Less than 90%
                cache_insight = AIInsight(
                    insight_id=f"optimization_cache_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.utcnow(),
                    insight_type=InsightType.OPTIMIZATION_RECOMMENDATION,
                    confidence=0.9,
                    confidence_level=ConfidenceLevel.VERY_HIGH,
                    title="Cache Hit Ratio Optimization Opportunity",
                    description=f"Average cache hit ratio is {avg_cache_hit_ratio:.1%}, below optimal 90%",
                    impact_score=0.7,
                    severity="MEDIUM",
                    recommendations=[
                        "Consider increasing shared_buffers configuration",
                        "Analyze query patterns for optimization opportunities",
                        "Review most frequently accessed tables for caching",
                        "Monitor buffer usage patterns"
                    ],
                    data_sources=["pg_stat_database"],
                    metadata={
                        'current_cache_hit_ratio': avg_cache_hit_ratio,
                        'target_cache_hit_ratio': 0.9,
                        'improvement_potential': f"{(0.9 - avg_cache_hit_ratio) * 100:.1f}%"
                    }
                )
                
                await self._store_insight(cache_insight)
                
        except Exception as e:
            self.logger.error(f"Failed to generate optimization insights: {e}")
            
    async def _store_insight(self, insight: AIInsight):
        """Store AI insight"""
        try:
            self.insights[insight.insight_id] = insight
            
            await self.cache.set(
                f"ai_insight:{insight.insight_id}",
                json.dumps(insight.to_dict()),
                expire=604800  # 7 days
            )
            
            # Add to timeline
            await self.cache.zadd(
                "insights_timeline",
                {insight.insight_id: insight.timestamp.timestamp()}
            )
            
            # Index by type
            await self.cache.sadd(
                f"insights_by_type:{insight.insight_type.value}",
                insight.insight_id
            )
            
            # Send notification for high-impact insights
            if insight.impact_score > 0.7:
                await self._send_insight_notification(insight)
                
        except Exception as e:
            self.logger.error(f"Failed to store insight: {e}")
            
    async def _send_insight_notification(self, insight: AIInsight):
        """Send insight notification"""
        try:
            await self.notification_manager.send_insight_notification(
                title=insight.title,
                message=insight.description,
                details=insight.to_dict()
            )
        except Exception as e:
            self.logger.error(f"Failed to send insight notification: {e}")
            
    async def _retrain_models_if_needed(self):
        """Retrain models if needed"""
        try:
            # Retrain models daily
            for model_name in ['performance_anomaly', 'query_anomaly']:
                last_trained = self.model_last_trained.get(model_name)
                
                if not last_trained or (datetime.utcnow() - last_trained).days >= 1:
                    await self._retrain_model(model_name)
                    self.model_last_trained[model_name] = datetime.utcnow()
                    
            # Save models to cache
            await self._save_models()
            
        except Exception as e:
            self.logger.error(f"Failed to retrain models: {e}")
            
    async def _retrain_model(self, model_name: str):
        """Retrain specific model"""
        try:
            if len(self.historical_data) < 100:
                return
                
            feature_columns = [
                'active_connections', 'idle_connections', 'total_backends',
                'disk_reads', 'cache_hits', 'cache_hit_ratio',
                'tuples_returned', 'tuples_fetched', 'commit_ratio'
            ]
            
            features = self.historical_data[feature_columns].fillna(0)
            scaled_features = self.models['scaler'].fit_transform(features)
            
            # Retrain the model
            self.models[model_name].fit(scaled_features)
            
            self.logger.info(f"Retrained model: {model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to retrain model {model_name}: {e}")
            
    async def _save_models(self):
        """Save trained models to cache"""
        try:
            models_to_save = {
                key: value for key, value in self.models.items()
                if key in ['performance_anomaly', 'query_anomaly', 'scaler']
            }
            
            await self.cache.set(
                "ai_models",
                pickle.dumps(models_to_save),
                expire=604800  # 7 days
            )
            
        except Exception as e:
            self.logger.error(f"Failed to save models: {e}")
            
    async def _cleanup_old_insights(self):
        """Cleanup old insights and data"""
        try:
            # Remove insights older than 7 days
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # Cleanup insights
            await self.cache.zremrangebyscore(
                "insights_timeline",
                "-inf",
                cutoff_timestamp
            )
            
            # Cleanup anomalies
            await self.cache.zremrangebyscore(
                "anomalies_timeline",
                "-inf",
                cutoff_timestamp
            )
            
            # Cleanup predictions (1 day retention)
            pred_cutoff = datetime.utcnow() - timedelta(days=1)
            pred_cutoff_timestamp = pred_cutoff.timestamp()
            
            for metric in ['active_connections', 'cache_hit_ratio', 'disk_reads', 'total_commits']:
                await self.cache.zremrangebyscore(
                    f"predictions_timeline:{metric}",
                    "-inf",
                    pred_cutoff_timestamp
                )
                
            self.logger.debug("Cleaned up old AI insights data")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old insights: {e}")
            
    async def get_insights_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get AI insights summary"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # Get recent insights
            insight_ids = await self.cache.zrangebyscore(
                "insights_timeline",
                cutoff_timestamp,
                "+inf"
            )
            
            insights_by_type = defaultdict(int)
            total_impact_score = 0.0
            
            for insight_id in insight_ids:
                insight_data = await self.cache.get(f"ai_insight:{insight_id}")
                if insight_data:
                    insight = json.loads(insight_data)
                    insights_by_type[insight['insight_type']] += 1
                    total_impact_score += insight['impact_score']
                    
            # Get recent anomalies
            anomaly_ids = await self.cache.zrangebyscore(
                "anomalies_timeline",
                cutoff_timestamp,
                "+inf"
            )
            
            anomalies_by_type = defaultdict(int)
            for anomaly_id in anomaly_ids:
                anomaly_data = await self.cache.get(f"anomaly:{anomaly_id}")
                if anomaly_data:
                    anomaly = json.loads(anomaly_data)
                    anomalies_by_type[anomaly['anomaly_type']] += 1
                    
            return {
                'period_hours': hours,
                'total_insights': len(insight_ids),
                'total_anomalies': len(anomaly_ids),
                'insights_by_type': dict(insights_by_type),
                'anomalies_by_type': dict(anomalies_by_type),
                'average_impact_score': total_impact_score / max(len(insight_ids), 1),
                'models_trained': len(self.model_last_trained),
                'data_points_analyzed': len(self.historical_data),
                'monitoring_active': self._monitoring_active,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get insights summary: {e}")
            return {}


class PredictiveAnalyzer:
    """Advanced predictive analysis engine"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
    async def predict_performance_degradation(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Predict potential performance degradation"""
        # Implementation for performance degradation prediction
        pass
        
    async def forecast_capacity_needs(self, usage_trends: List[Dict]) -> Dict[str, Any]:
        """Forecast future capacity requirements"""
        # Implementation for capacity forecasting
        pass


class AnomalyDetector:
    """Advanced anomaly detection engine"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
    async def detect_performance_anomalies(self, metrics: List[Dict]) -> List[AnomalyDetection]:
        """Detect performance anomalies"""
        # Implementation for performance anomaly detection
        pass
        
    async def detect_security_anomalies(self, security_events: List[Dict]) -> List[AnomalyDetection]:
        """Detect security anomalies"""
        # Implementation for security anomaly detection
        pass
