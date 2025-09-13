#!/usr/bin/env python3
"""
Quality AI Orchestrator - Ainflue Quality Platform
================================================

Enterprise AI-powered quality analysis and prediction system.
Demonstrates ML Engineer + IA Prompt Engineer + Lead Dev IA expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import pickle
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import openai
from transformers import pipeline
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QualityPrediction:
    """Quality prediction result."""
    prediction_type: str  # 'bug_risk', 'performance_degradation', 'security_risk'
    confidence: float
    prediction_value: Any
    features_used: List[str]
    model_accuracy: float
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QualityAnomalyDetection:
    """Quality anomaly detection result."""
    anomaly_type: str  # 'performance', 'error_rate', 'resource_usage'
    severity: str  # 'critical', 'high', 'medium', 'low'
    confidence: float
    anomaly_score: float
    affected_metrics: List[str]
    description: str
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QualityInsight:
    """AI-generated quality insight."""
    insight_type: str  # 'trend', 'pattern', 'recommendation', 'alert'
    title: str
    description: str
    impact_level: str  # 'critical', 'high', 'medium', 'low'
    actionable_items: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class MLModelManager:
    """Machine Learning model management for quality prediction."""
    
    def __init__(self, models_dir: str = "ml_models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Model instances
        self.bug_predictor = None
        self.performance_predictor = None
        self.security_classifier = None
        self.anomaly_detector = None
        
        # Scalers and encoders
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Model metadata
        self.model_metadata = {}
    
    async def train_bug_prediction_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train a model to predict bug likelihood."""
        logger.info("Training bug prediction model")
        
        # Feature engineering
        features = self._extract_code_quality_features(training_data)
        target = training_data['has_bugs'].astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=0.2, random_state=42, stratify=target
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.bug_predictor = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.bug_predictor.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.bug_predictor.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self.bug_predictor, X_train_scaled, y_train, cv=5)
        
        # Feature importance
        feature_importance = dict(zip(
            features.columns,
            self.bug_predictor.feature_importances_
        ))
        
        # Save model
        model_path = self.models_dir / "bug_predictor.joblib"
        joblib.dump(self.bug_predictor, model_path)
        
        scaler_path = self.models_dir / "bug_scaler.joblib"
        joblib.dump(self.scaler, scaler_path)
        
        # Store metadata
        metadata = {
            'model_type': 'bug_prediction',
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': feature_importance,
            'training_size': len(X_train),
            'trained_at': datetime.now().isoformat()
        }
        
        self.model_metadata['bug_predictor'] = metadata
        
        logger.info(f"Bug prediction model trained - Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
        return metadata
    
    async def train_performance_prediction_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train a model to predict performance degradation."""
        logger.info("Training performance prediction model")
        
        # Feature engineering
        features = self._extract_performance_features(training_data)
        target = training_data['response_time_ms']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.performance_predictor = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.performance_predictor.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.performance_predictor.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # Feature importance
        feature_importance = dict(zip(
            features.columns,
            self.performance_predictor.feature_importances_
        ))
        
        # Save model
        model_path = self.models_dir / "performance_predictor.joblib"
        joblib.dump(self.performance_predictor, model_path)
        
        # Store metadata
        metadata = {
            'model_type': 'performance_prediction',
            'r2_score': r2,
            'rmse': rmse,
            'mse': mse,
            'feature_importance': feature_importance,
            'training_size': len(X_train),
            'trained_at': datetime.now().isoformat()
        }
        
        self.model_metadata['performance_predictor'] = metadata
        
        logger.info(f"Performance prediction model trained - R²: {r2:.3f}, RMSE: {rmse:.3f}")
        return metadata
    
    async def train_anomaly_detection_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train anomaly detection model."""
        logger.info("Training anomaly detection model")
        
        # Feature engineering
        features = self._extract_anomaly_features(training_data)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train DBSCAN for anomaly detection
        self.anomaly_detector = DBSCAN(
            eps=0.5,
            min_samples=5,
            metric='euclidean'
        )
        
        labels = self.anomaly_detector.fit_predict(features_scaled)
        
        # Calculate anomaly statistics
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_anomalies = list(labels).count(-1)
        anomaly_rate = n_anomalies / len(labels)
        
        # Save model
        model_path = self.models_dir / "anomaly_detector.joblib"
        joblib.dump(self.anomaly_detector, model_path)
        
        # Store metadata
        metadata = {
            'model_type': 'anomaly_detection',
            'n_clusters': n_clusters,
            'anomaly_rate': anomaly_rate,
            'n_anomalies': n_anomalies,
            'training_size': len(features),
            'trained_at': datetime.now().isoformat()
        }
        
        self.model_metadata['anomaly_detector'] = metadata
        
        logger.info(f"Anomaly detection model trained - Clusters: {n_clusters}, Anomaly rate: {anomaly_rate:.3f}")
        return metadata
    
    def _extract_code_quality_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for bug prediction."""
        features = pd.DataFrame()
        
        # Code complexity metrics
        features['cyclomatic_complexity'] = data.get('cyclomatic_complexity', 0)
        features['lines_of_code'] = data.get('lines_of_code', 0)
        features['number_of_methods'] = data.get('number_of_methods', 0)
        features['number_of_classes'] = data.get('number_of_classes', 0)
        
        # Code quality metrics
        features['test_coverage'] = data.get('test_coverage', 0)
        features['code_duplication'] = data.get('code_duplication', 0)
        features['technical_debt_hours'] = data.get('technical_debt_hours', 0)
        
        # Git metrics
        features['commits_last_month'] = data.get('commits_last_month', 0)
        features['unique_authors'] = data.get('unique_authors', 0)
        features['files_changed'] = data.get('files_changed', 0)
        
        # Historical bug metrics
        features['bugs_last_quarter'] = data.get('bugs_last_quarter', 0)
        features['avg_time_to_fix'] = data.get('avg_time_to_fix', 0)
        
        return features.fillna(0)
    
    def _extract_performance_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for performance prediction."""
        features = pd.DataFrame()
        
        # System metrics
        features['cpu_usage'] = data.get('cpu_usage', 0)
        features['memory_usage'] = data.get('memory_usage', 0)
        features['disk_io'] = data.get('disk_io', 0)
        features['network_io'] = data.get('network_io', 0)
        
        # Application metrics
        features['concurrent_users'] = data.get('concurrent_users', 0)
        features['requests_per_second'] = data.get('requests_per_second', 0)
        features['database_connections'] = data.get('database_connections', 0)
        features['cache_hit_rate'] = data.get('cache_hit_rate', 0)
        
        # Code metrics
        features['code_complexity'] = data.get('code_complexity', 0)
        features['database_queries'] = data.get('database_queries', 0)
        features['external_api_calls'] = data.get('external_api_calls', 0)
        
        return features.fillna(0)
    
    def _extract_anomaly_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for anomaly detection."""
        features = pd.DataFrame()
        
        # Performance metrics
        features['response_time'] = data.get('response_time_ms', 0)
        features['error_rate'] = data.get('error_rate', 0)
        features['throughput'] = data.get('throughput', 0)
        
        # Resource metrics
        features['cpu_usage'] = data.get('cpu_usage', 0)
        features['memory_usage'] = data.get('memory_usage', 0)
        features['disk_usage'] = data.get('disk_usage', 0)
        
        # Quality metrics
        features['test_pass_rate'] = data.get('test_pass_rate', 0)
        features['code_coverage'] = data.get('code_coverage', 0)
        features['technical_debt'] = data.get('technical_debt', 0)
        
        return features.fillna(0)
    
    async def predict_bug_risk(self, feature_data: Dict[str, Any]) -> QualityPrediction:
        """Predict bug risk for given features."""
        if not self.bug_predictor:
            # Try to load model
            model_path = self.models_dir / "bug_predictor.joblib"
            scaler_path = self.models_dir / "bug_scaler.joblib"
            
            if model_path.exists() and scaler_path.exists():
                self.bug_predictor = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
            else:
                raise ValueError("Bug prediction model not trained or saved")
        
        # Prepare features
        features_df = pd.DataFrame([feature_data])
        features_processed = self._extract_code_quality_features(features_df)
        features_scaled = self.scaler.transform(features_processed)
        
        # Make prediction
        prediction_proba = self.bug_predictor.predict_proba(features_scaled)[0]
        bug_probability = prediction_proba[1]  # Probability of having bugs
        
        # Get feature importance for explanation
        feature_importance = dict(zip(
            features_processed.columns,
            self.bug_predictor.feature_importances_
        ))
        
        return QualityPrediction(
            prediction_type="bug_risk",
            confidence=max(prediction_proba),
            prediction_value=bug_probability,
            features_used=list(features_processed.columns),
            model_accuracy=self.model_metadata.get('bug_predictor', {}).get('accuracy', 0.0),
            reasoning=f"Based on code complexity and quality metrics. Top risk factors: {sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]}"
        )
    
    async def predict_performance(self, feature_data: Dict[str, Any]) -> QualityPrediction:
        """Predict performance metrics for given features."""
        if not self.performance_predictor:
            # Try to load model
            model_path = self.models_dir / "performance_predictor.joblib"
            
            if model_path.exists():
                self.performance_predictor = joblib.load(model_path)
            else:
                raise ValueError("Performance prediction model not trained or saved")
        
        # Prepare features
        features_df = pd.DataFrame([feature_data])
        features_processed = self._extract_performance_features(features_df)
        features_scaled = self.scaler.transform(features_processed)
        
        # Make prediction
        predicted_response_time = self.performance_predictor.predict(features_scaled)[0]
        
        # Calculate confidence based on model performance
        r2_score = self.model_metadata.get('performance_predictor', {}).get('r2_score', 0.0)
        confidence = max(0.5, r2_score)  # Minimum 50% confidence
        
        return QualityPrediction(
            prediction_type="performance_degradation",
            confidence=confidence,
            prediction_value=predicted_response_time,
            features_used=list(features_processed.columns),
            model_accuracy=r2_score,
            reasoning=f"Predicted response time based on system load and application metrics"
        )
    
    async def detect_anomalies(self, feature_data: List[Dict[str, Any]]) -> List[QualityAnomalyDetection]:
        """Detect anomalies in quality metrics."""
        if not self.anomaly_detector:
            # Try to load model
            model_path = self.models_dir / "anomaly_detector.joblib"
            
            if model_path.exists():
                self.anomaly_detector = joblib.load(model_path)
            else:
                raise ValueError("Anomaly detection model not trained or saved")
        
        # Prepare features
        features_df = pd.DataFrame(feature_data)
        features_processed = self._extract_anomaly_features(features_df)
        features_scaled = self.scaler.transform(features_processed)
        
        # Detect anomalies
        labels = self.anomaly_detector.fit_predict(features_scaled)
        
        anomalies = []
        for i, label in enumerate(labels):
            if label == -1:  # Anomaly detected
                # Calculate anomaly score
                core_samples = self.anomaly_detector.core_sample_indices_
                if len(core_samples) > 0:
                    distances = np.linalg.norm(features_scaled[i] - features_scaled[core_samples], axis=1)
                    anomaly_score = np.min(distances)
                else:
                    anomaly_score = 1.0
                
                # Determine severity based on anomaly score
                if anomaly_score > 2.0:
                    severity = "critical"
                elif anomaly_score > 1.5:
                    severity = "high"
                elif anomaly_score > 1.0:
                    severity = "medium"
                else:
                    severity = "low"
                
                # Identify affected metrics
                affected_metrics = []
                for col, value in features_processed.iloc[i].items():
                    if value > features_processed[col].quantile(0.95) or value < features_processed[col].quantile(0.05):
                        affected_metrics.append(col)
                
                anomaly = QualityAnomalyDetection(
                    anomaly_type="quality_metrics",
                    severity=severity,
                    confidence=min(1.0, anomaly_score / 2.0),
                    anomaly_score=anomaly_score,
                    affected_metrics=affected_metrics,
                    description=f"Anomalous behavior detected in quality metrics",
                    recommendations=[
                        "Investigate recent changes in affected components",
                        "Check system resource usage and capacity",
                        "Review recent deployments and configuration changes"
                    ]
                )
                
                anomalies.append(anomaly)
        
        return anomalies


class AIInsightGenerator:
    """AI-powered insight generation using language models."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.openai_client = None
        self.local_model = None
        
        # Initialize AI models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models for insight generation."""
        try:
            # Initialize OpenAI client if API key provided
            if self.config.get('openai_api_key'):
                openai.api_key = self.config['openai_api_key']
                self.openai_client = openai
                logger.info("OpenAI client initialized")
            
            # Initialize local model as fallback
            if torch.cuda.is_available():
                device = 0
            else:
                device = -1
            
            self.local_model = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                device=device
            )
            logger.info("Local AI model initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize AI models: {e}")
    
    async def generate_quality_insights(self, quality_data: Dict[str, Any]) -> List[QualityInsight]:
        """Generate AI-powered quality insights from data."""
        insights = []
        
        # Analyze trends
        trend_insights = await self._analyze_trends(quality_data)
        insights.extend(trend_insights)
        
        # Generate recommendations
        recommendation_insights = await self._generate_recommendations(quality_data)
        insights.extend(recommendation_insights)
        
        # Detect patterns
        pattern_insights = await self._detect_patterns(quality_data)
        insights.extend(pattern_insights)
        
        return insights
    
    async def _analyze_trends(self, data: Dict[str, Any]) -> List[QualityInsight]:
        """Analyze quality trends using AI."""
        insights = []
        
        # Extract time series data
        metrics_over_time = data.get('metrics_over_time', {})
        
        for metric_name, values in metrics_over_time.items():
            if len(values) < 3:
                continue
            
            # Calculate trend
            trend = np.polyfit(range(len(values)), values, 1)[0]
            
            # Generate insight based on trend
            if abs(trend) > 0.1:  # Significant trend
                trend_direction = "increasing" if trend > 0 else "decreasing"
                impact_level = "high" if abs(trend) > 0.5 else "medium"
                
                # Use AI to generate description
                description = await self._generate_ai_description(
                    f"Quality metric '{metric_name}' is {trend_direction} with a trend slope of {trend:.3f}. "
                    f"Recent values: {values[-3:]}. Analyze the impact and provide insights."
                )
                
                insight = QualityInsight(
                    insight_type="trend",
                    title=f"{metric_name.replace('_', ' ').title()} Trend Analysis",
                    description=description,
                    impact_level=impact_level,
                    actionable_items=[
                        f"Monitor {metric_name} closely",
                        f"Investigate root cause of {trend_direction} trend",
                        "Review recent changes that might impact this metric"
                    ],
                    data_sources=[metric_name],
                    confidence=min(0.9, abs(trend))
                )
                
                insights.append(insight)
        
        return insights
    
    async def _generate_recommendations(self, data: Dict[str, Any]) -> List[QualityInsight]:
        """Generate AI-powered recommendations."""
        insights = []
        
        # Analyze current quality state
        current_metrics = data.get('current_metrics', {})
        
        # Generate recommendations based on thresholds
        recommendations = []
        
        if current_metrics.get('test_coverage', 0) < 80:
            recommendations.append("Increase test coverage to at least 80%")
        
        if current_metrics.get('error_rate', 0) > 5:
            recommendations.append("Reduce error rate through better error handling")
        
        if current_metrics.get('response_time_p95', 0) > 2000:
            recommendations.append("Optimize performance to reduce P95 response time")
        
        if recommendations:
            # Use AI to enhance recommendations
            enhanced_recommendations = await self._enhance_recommendations(recommendations, current_metrics)
            
            insight = QualityInsight(
                insight_type="recommendation",
                title="Quality Improvement Recommendations",
                description="AI-generated recommendations based on current quality metrics",
                impact_level="medium",
                actionable_items=enhanced_recommendations,
                data_sources=list(current_metrics.keys()),
                confidence=0.8
            )
            
            insights.append(insight)
        
        return insights
    
    async def _detect_patterns(self, data: Dict[str, Any]) -> List[QualityInsight]:
        """Detect patterns in quality data using AI."""
        insights = []
        
        # Analyze correlation patterns
        metrics = data.get('correlation_matrix', {})
        
        if metrics:
            # Find strong correlations
            strong_correlations = []
            for metric1, correlations in metrics.items():
                for metric2, correlation in correlations.items():
                    if metric1 != metric2 and abs(correlation) > 0.7:
                        strong_correlations.append((metric1, metric2, correlation))
            
            if strong_correlations:
                # Generate pattern insights
                pattern_description = await self._generate_pattern_description(strong_correlations)
                
                insight = QualityInsight(
                    insight_type="pattern",
                    title="Quality Metric Correlation Patterns",
                    description=pattern_description,
                    impact_level="medium",
                    actionable_items=[
                        "Leverage strong correlations for predictive monitoring",
                        "Focus optimization efforts on highly correlated metrics",
                        "Investigate root causes of unexpected correlations"
                    ],
                    data_sources=[item[0] for item in strong_correlations],
                    confidence=0.7
                )
                
                insights.append(insight)
        
        return insights
    
    async def _generate_ai_description(self, prompt: str) -> str:
        """Generate AI description using available models."""
        try:
            if self.openai_client:
                response = await self.openai_client.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a quality assurance expert analyzing software quality metrics."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            
            elif self.local_model:
                response = self.local_model(prompt, max_length=150, num_return_sequences=1)
                return response[0]['generated_text'].strip()
            
        except Exception as e:
            logger.warning(f"AI description generation failed: {e}")
        
        # Fallback to template-based description
        return f"Analysis of quality metrics indicates significant changes requiring attention."
    
    async def _enhance_recommendations(self, recommendations: List[str], metrics: Dict[str, Any]) -> List[str]:
        """Enhance recommendations using AI."""
        enhanced = []
        
        for rec in recommendations:
            try:
                prompt = f"Enhance this quality recommendation with specific actionable steps: '{rec}'. Current metrics: {metrics}"
                enhanced_rec = await self._generate_ai_description(prompt)
                enhanced.append(enhanced_rec if enhanced_rec else rec)
            except:
                enhanced.append(rec)
        
        return enhanced
    
    async def _generate_pattern_description(self, correlations: List[Tuple[str, str, float]]) -> str:
        """Generate description of correlation patterns."""
        try:
            correlation_text = ", ".join([
                f"{metric1} and {metric2} (correlation: {corr:.2f})"
                for metric1, metric2, corr in correlations[:3]
            ])
            
            prompt = f"Analyze these quality metric correlations and explain their significance: {correlation_text}"
            return await self._generate_ai_description(prompt)
            
        except Exception as e:
            logger.warning(f"Pattern description generation failed: {e}")
            return "Strong correlations detected between quality metrics, indicating interconnected quality factors."


class QualityAIOrchestrator:
    """
    Enterprise Quality AI Orchestration Engine
    ========================================
    
    AI-powered quality analysis, prediction, and insight generation.
    Demonstrates ML Engineer + IA Prompt Engineer + Lead Dev IA expertise.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.ml_manager = MLModelManager(self.config.get('models_dir', 'ml_models'))
        self.ai_insights = AIInsightGenerator(self.config.get('ai_config', {}))
        
        # Quality data storage
        self.quality_data: List[Dict[str, Any]] = []
        self.predictions: List[QualityPrediction] = []
        self.anomalies: List[QualityAnomalyDetection] = []
        self.insights: List[QualityInsight] = []
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load AI orchestrator configuration."""
        default_config = {
            'models_dir': 'ml_models',
            'ai_config': {
                'openai_api_key': None,
                'use_local_models': True
            },
            'prediction_settings': {
                'retrain_interval_days': 7,
                'minimum_training_samples': 100,
                'prediction_confidence_threshold': 0.6
            },
            'anomaly_settings': {
                'detection_sensitivity': 'medium',
                'alert_threshold': 0.8
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def ingest_quality_data(self, data: Dict[str, Any]):
        """Ingest quality data for analysis."""
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        self.quality_data.append(data)
        
        # Trigger real-time analysis if threshold reached
        if len(self.quality_data) % 10 == 0:  # Every 10 data points
            await self._trigger_real_time_analysis()
    
    async def _trigger_real_time_analysis(self):
        """Trigger real-time analysis on recent data."""
        # Get recent data
        recent_data = self.quality_data[-10:]
        
        # Check for anomalies
        try:
            anomalies = await self.ml_manager.detect_anomalies(recent_data)
            self.anomalies.extend(anomalies)
            
            # Generate alerts for critical anomalies
            for anomaly in anomalies:
                if anomaly.severity == 'critical':
                    logger.warning(f"Critical quality anomaly detected: {anomaly.description}")
        
        except Exception as e:
            logger.error(f"Real-time anomaly detection failed: {e}")
    
    async def train_quality_models(self, historical_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Train quality prediction models."""
        logger.info("Training quality prediction models")
        
        if historical_data is None:
            # Use stored quality data
            if len(self.quality_data) < self.config['prediction_settings']['minimum_training_samples']:
                raise ValueError("Insufficient training data")
            
            historical_data = pd.DataFrame(self.quality_data)
        
        training_results = {}
        
        try:
            # Train bug prediction model
            if 'has_bugs' in historical_data.columns:
                bug_results = await self.ml_manager.train_bug_prediction_model(historical_data)
                training_results['bug_predictor'] = bug_results
            
            # Train performance prediction model
            if 'response_time_ms' in historical_data.columns:
                perf_results = await self.ml_manager.train_performance_prediction_model(historical_data)
                training_results['performance_predictor'] = perf_results
            
            # Train anomaly detection model
            anomaly_results = await self.ml_manager.train_anomaly_detection_model(historical_data)
            training_results['anomaly_detector'] = anomaly_results
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            training_results['error'] = str(e)
        
        return training_results
    
    async def predict_quality_metrics(self, feature_data: Dict[str, Any]) -> List[QualityPrediction]:
        """Predict quality metrics for given features."""
        predictions = []
        
        try:
            # Predict bug risk
            bug_prediction = await self.ml_manager.predict_bug_risk(feature_data)
            predictions.append(bug_prediction)
            
            # Predict performance
            perf_prediction = await self.ml_manager.predict_performance(feature_data)
            predictions.append(perf_prediction)
            
        except Exception as e:
            logger.error(f"Quality prediction failed: {e}")
            # Create error prediction
            error_prediction = QualityPrediction(
                prediction_type="error",
                confidence=0.0,
                prediction_value=None,
                features_used=[],
                model_accuracy=0.0,
                reasoning=f"Prediction failed: {str(e)}"
            )
            predictions.append(error_prediction)
        
        self.predictions.extend(predictions)
        return predictions
    
    async def detect_quality_anomalies(self, data_points: List[Dict[str, Any]]) -> List[QualityAnomalyDetection]:
        """Detect anomalies in quality data."""
        try:
            anomalies = await self.ml_manager.detect_anomalies(data_points)
            self.anomalies.extend(anomalies)
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    async def generate_quality_insights(self) -> List[QualityInsight]:
        """Generate AI-powered quality insights."""
        # Prepare data for insight generation
        quality_summary = self._prepare_insight_data()
        
        try:
            insights = await self.ai_insights.generate_quality_insights(quality_summary)
            self.insights.extend(insights)
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return []
    
    def _prepare_insight_data(self) -> Dict[str, Any]:
        """Prepare quality data for insight generation."""
        if not self.quality_data:
            return {}
        
        df = pd.DataFrame(self.quality_data)
        
        # Calculate metrics over time
        metrics_over_time = {}
        for column in df.select_dtypes(include=[np.number]).columns:
            metrics_over_time[column] = df[column].tolist()
        
        # Calculate current metrics
        current_metrics = {}
        for column in df.select_dtypes(include=[np.number]).columns:
            current_metrics[column] = df[column].iloc[-1] if len(df) > 0 else 0
        
        # Calculate correlation matrix
        correlation_matrix = {}
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            for col in corr_matrix.columns:
                correlation_matrix[col] = corr_matrix[col].to_dict()
        
        return {
            'metrics_over_time': metrics_over_time,
            'current_metrics': current_metrics,
            'correlation_matrix': correlation_matrix,
            'data_points': len(self.quality_data),
            'time_range': {
                'start': self.quality_data[0].get('timestamp') if self.quality_data else None,
                'end': self.quality_data[-1].get('timestamp') if self.quality_data else None
            }
        }
    
    async def run_comprehensive_analysis(self, analysis_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run comprehensive quality analysis."""
        logger.info("Running comprehensive quality analysis")
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'predictions': [],
            'anomalies': [],
            'insights': [],
            'summary': {}
        }
        
        try:
            # Generate predictions if feature data provided
            if analysis_data and 'features' in analysis_data:
                predictions = await self.predict_quality_metrics(analysis_data['features'])
                analysis_results['predictions'] = [
                    {
                        'type': p.prediction_type,
                        'value': p.prediction_value,
                        'confidence': p.confidence,
                        'model_accuracy': p.model_accuracy,
                        'reasoning': p.reasoning
                    }
                    for p in predictions
                ]
            
            # Detect anomalies
            if self.quality_data:
                recent_data = self.quality_data[-20:]  # Last 20 data points
                anomalies = await self.detect_quality_anomalies(recent_data)
                analysis_results['anomalies'] = [
                    {
                        'type': a.anomaly_type,
                        'severity': a.severity,
                        'confidence': a.confidence,
                        'score': a.anomaly_score,
                        'affected_metrics': a.affected_metrics,
                        'description': a.description,
                        'recommendations': a.recommendations
                    }
                    for a in anomalies
                ]
            
            # Generate insights
            insights = await self.generate_quality_insights()
            analysis_results['insights'] = [
                {
                    'type': i.insight_type,
                    'title': i.title,
                    'description': i.description,
                    'impact_level': i.impact_level,
                    'actionable_items': i.actionable_items,
                    'confidence': i.confidence
                }
                for i in insights
            ]
            
            # Generate summary
            analysis_results['summary'] = {
                'total_predictions': len(analysis_results['predictions']),
                'total_anomalies': len(analysis_results['anomalies']),
                'total_insights': len(analysis_results['insights']),
                'critical_issues': len([a for a in analysis_results['anomalies'] if a['severity'] == 'critical']),
                'high_confidence_predictions': len([p for p in analysis_results['predictions'] if p['confidence'] > 0.8]),
                'actionable_insights': len([i for i in analysis_results['insights'] if i['actionable_items']])
            }
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    async def save_analysis_report(self, analysis_results: Dict[str, Any], 
                                 output_path: str = "quality_ai_analysis_report.json"):
        """Save analysis report to file."""
        with open(output_path, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        logger.info(f"Quality AI analysis report saved to: {output_path}")


# CLI Interface
async def main():
    """Main CLI interface for quality AI orchestration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quality AI Orchestration Engine")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--data", help="Quality data file for analysis")
    parser.add_argument("--train", action="store_true", help="Train models with provided data")
    parser.add_argument("--analyze", action="store_true", help="Run comprehensive analysis")
    parser.add_argument("--output", default="quality_ai_analysis_report.json", help="Output report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize orchestrator
    orchestrator = QualityAIOrchestrator(args.config)
    
    try:
        analysis_data = None
        
        # Load data if provided
        if args.data:
            with open(args.data, 'r') as f:
                analysis_data = json.load(f)
            
            # Ingest data
            if isinstance(analysis_data, list):
                for data_point in analysis_data:
                    await orchestrator.ingest_quality_data(data_point)
            else:
                await orchestrator.ingest_quality_data(analysis_data)
        
        # Train models if requested
        if args.train and orchestrator.quality_data:
            training_results = await orchestrator.train_quality_models()
            print(f"\n🤖 Model Training Results:")
            for model_name, results in training_results.items():
                if isinstance(results, dict) and 'accuracy' in results:
                    print(f"  {model_name}: Accuracy {results['accuracy']:.3f}")
                elif isinstance(results, dict) and 'r2_score' in results:
                    print(f"  {model_name}: R² Score {results['r2_score']:.3f}")
        
        # Run analysis if requested
        if args.analyze:
            analysis_results = await orchestrator.run_comprehensive_analysis(analysis_data)
            
            # Save report
            await orchestrator.save_analysis_report(analysis_results, args.output)
            
            # Print summary
            summary = analysis_results['summary']
            print(f"\n🤖 Quality AI Analysis Results")
            print(f"{'='*50}")
            print(f"Predictions Generated: {summary['total_predictions']}")
            print(f"Anomalies Detected: {summary['total_anomalies']}")
            print(f"Insights Generated: {summary['total_insights']}")
            print(f"Critical Issues: {summary['critical_issues']}")
            print(f"High Confidence Predictions: {summary['high_confidence_predictions']}")
            print(f"Actionable Insights: {summary['actionable_insights']}")
            
            if analysis_results['insights']:
                print(f"\n💡 Key Insights:")
                for insight in analysis_results['insights'][:3]:  # Show first 3 insights
                    print(f"  - {insight['title']}: {insight['description'][:100]}...")
    
    except Exception as e:
        logger.error(f"Quality AI orchestration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())