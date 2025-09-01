"""🔮 Prediction Engine
==================

Advanced AI prediction system for content protection:
- Risk prediction modeling
- Threat forecasting
- Violation likelihood assessment
- Revenue impact prediction
- Behavioral outcome prediction

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + ML Engineer + Data Scientist
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import pickle
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error
import xgboost as xgb
import lightgbm as lgb
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class PredictionEngine:
    """
    Enterprise AI prediction engine for content protection
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self.model_performance = {}
        
        # Prediction types
        self.prediction_types = {
            'risk_assessment': 'classification',
            'violation_likelihood': 'classification', 
            'revenue_impact': 'regression',
            'threat_severity': 'classification',
            'user_behavior': 'classification',
            'content_popularity': 'regression',
            'protection_effectiveness': 'regression'
        }
        
        # Initialize models
        self._initialize_models()
        
        logger.info("Prediction Engine initialized with advanced ML models")
    
    def _initialize_models(self):
        """Initialize all prediction models"""
        try:
            for prediction_type, model_type in self.prediction_types.items():
                self.models[prediction_type] = self._create_ensemble_model(model_type)
                self.scalers[prediction_type] = StandardScaler()
                self.encoders[prediction_type] = {}
                
            logger.info(f"Initialized {len(self.prediction_types)} prediction models")
            
        except Exception as e:
            logger.error(f"Failed to initialize prediction models: {str(e)}")
            raise
    
    def _create_ensemble_model(self, model_type: str) -> Dict[str, Any]:
        """Create ensemble model for specific prediction type"""
        if model_type == 'classification':
            return {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'xgboost': xgb.XGBClassifier(random_state=42),
                'lightgbm': lgb.LGBMClassifier(random_state=42),
                'neural_network': MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42),
                'ensemble_weights': [0.25, 0.25, 0.2, 0.2, 0.1]
            }
        else:  # regression
            return {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': xgb.XGBRegressor(random_state=42),
                'lightgbm': lgb.LGBMRegressor(random_state=42),
                'svr': SVR(kernel='rbf'),
                'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42),
                'ensemble_weights': [0.3, 0.25, 0.25, 0.1, 0.1]
            }
    
    async def predict_risks(self, content_data: Dict[str, Any], classification: Dict[str, Any], 
                           threats: List[Dict[str, Any]], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main risk prediction entry point
        """
        try:
            prediction_results = {
                'content_id': content_data.get('id'),
                'timestamp': datetime.utcnow().isoformat(),
                'predictions': {},
                'confidence_scores': {},
                'feature_importance': {},
                'risk_factors': {},
                'recommendations': []
            }
            
            # Extract features from all inputs
            features = await self._extract_prediction_features(content_data, classification, threats, patterns)
            
            # Risk assessment prediction
            risk_prediction = await self._predict_risk_assessment(features)
            prediction_results['predictions']['risk_assessment'] = risk_prediction
            
            # Violation likelihood prediction
            violation_prediction = await self._predict_violation_likelihood(features)
            prediction_results['predictions']['violation_likelihood'] = violation_prediction
            
            # Revenue impact prediction
            revenue_prediction = await self._predict_revenue_impact(features)
            prediction_results['predictions']['revenue_impact'] = revenue_prediction
            
            # Threat severity prediction
            threat_prediction = await self._predict_threat_severity(features, threats)
            prediction_results['predictions']['threat_severity'] = threat_prediction
            
            # User behavior prediction
            behavior_prediction = await self._predict_user_behavior(features)
            prediction_results['predictions']['user_behavior'] = behavior_prediction
            
            # Content popularity prediction
            popularity_prediction = await self._predict_content_popularity(features)
            prediction_results['predictions']['content_popularity'] = popularity_prediction
            
            # Protection effectiveness prediction
            effectiveness_prediction = await self._predict_protection_effectiveness(features)
            prediction_results['predictions']['protection_effectiveness'] = effectiveness_prediction
            
            # Calculate confidence scores
            confidence_scores = self._calculate_prediction_confidence(prediction_results['predictions'])
            prediction_results['confidence_scores'] = confidence_scores
            
            # Extract feature importance
            feature_importance = self._extract_feature_importance(features)
            prediction_results['feature_importance'] = feature_importance
            
            # Identify key risk factors
            risk_factors = self._identify_risk_factors(prediction_results, features)
            prediction_results['risk_factors'] = risk_factors
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(prediction_results, features)
            prediction_results['recommendations'] = recommendations
            
            logger.info(f"Risk prediction completed for content {content_data.get('id')}")
            
            return prediction_results
            
        except Exception as e:
            logger.error(f"Risk prediction failed: {str(e)}")
            raise
    
    async def _extract_prediction_features(self, content_data: Dict[str, Any], classification: Dict[str, Any], 
                                         threats: List[Dict[str, Any]], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive features for prediction"""
        try:
            features = {
                'content_features': self._extract_content_features(content_data),
                'classification_features': self._extract_classification_features(classification),
                'threat_features': self._extract_threat_features(threats),
                'pattern_features': self._extract_pattern_features(patterns),
                'temporal_features': self._extract_temporal_features(content_data),
                'user_features': self._extract_user_features(content_data),
                'technical_features': self._extract_technical_features(content_data)
            }
            
            # Flatten features for model input
            flattened_features = self._flatten_features(features)
            
            return flattened_features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            raise
    
    async def _predict_risk_assessment(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict overall risk assessment"""
        try:
            model_ensemble = self.models['risk_assessment']
            scaler = self.scalers['risk_assessment']
            
            # Prepare features
            feature_vector = self._prepare_feature_vector(features, 'risk_assessment')
            
            if len(feature_vector) == 0:
                return {'risk_level': 'unknown', 'confidence': 0.0, 'probability': 0.5}
            
            # Scale features
            scaled_features = scaler.fit_transform([feature_vector])
            
            # Ensemble prediction
            predictions = []
            weights = model_ensemble['ensemble_weights']
            
            model_names = [k for k in model_ensemble.keys() if k != 'ensemble_weights']
            for i, model_name in enumerate(model_names):
                try:
                    model = model_ensemble[model_name]
                    if hasattr(model, 'predict_proba'):
                        pred_proba = model.predict_proba(scaled_features)[0]
                        predictions.append(pred_proba * weights[i])
                    else:
                        pred = model.predict(scaled_features)[0]
                        # Convert to probability-like score
                        prob_score = 1 / (1 + np.exp(-pred))  # Sigmoid
                        predictions.append([1-prob_score, prob_score] * weights[i])
                except Exception as e:
                    logger.warning(f"Model {model_name} prediction failed: {str(e)}")
                    continue
            
            if predictions:
                ensemble_pred = np.mean(predictions, axis=0)
                risk_probability = ensemble_pred[1] if len(ensemble_pred) > 1 else ensemble_pred[0]
                
                # Determine risk level
                if risk_probability >= 0.8:
                    risk_level = 'critical'
                elif risk_probability >= 0.6:
                    risk_level = 'high'
                elif risk_probability >= 0.4:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                return {
                    'risk_level': risk_level,
                    'probability': float(risk_probability),
                    'confidence': float(np.max(ensemble_pred)),
                    'prediction_details': {
                        'ensemble_predictions': [float(p[1] if len(p) > 1 else p[0]) for p in predictions],
                        'model_weights': weights[:len(predictions)]
                    }
                }
            else:
                return {'risk_level': 'unknown', 'confidence': 0.0, 'probability': 0.5}
                
        except Exception as e:
            logger.error(f"Risk assessment prediction failed: {str(e)}")
            return {'risk_level': 'unknown', 'confidence': 0.0, 'probability': 0.5}
    
    async def _predict_violation_likelihood(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict likelihood of copyright violation"""
        try:
            # Similar structure to risk assessment but for violation prediction
            model_ensemble = self.models['violation_likelihood']
            scaler = self.scalers['violation_likelihood']
            
            feature_vector = self._prepare_feature_vector(features, 'violation_likelihood')
            
            if len(feature_vector) == 0:
                return {'likelihood': 'unknown', 'probability': 0.5, 'confidence': 0.0}
            
            scaled_features = scaler.fit_transform([feature_vector])
            
            # Prediction logic similar to risk assessment
            violation_probability = 0.3  # Placeholder - would use actual ensemble prediction
            
            if violation_probability >= 0.7:
                likelihood = 'very_high'
            elif violation_probability >= 0.5:
                likelihood = 'high'
            elif violation_probability >= 0.3:
                likelihood = 'medium'
            else:
                likelihood = 'low'
            
            return {
                'likelihood': likelihood,
                'probability': float(violation_probability),
                'confidence': 0.8,
                'time_to_violation': self._predict_time_to_violation(violation_probability),
                'violation_type': self._predict_violation_type(features)
            }
            
        except Exception as e:
            logger.error(f"Violation likelihood prediction failed: {str(e)}")
            return {'likelihood': 'unknown', 'probability': 0.5, 'confidence': 0.0}
    
    async def _predict_revenue_impact(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict revenue impact of protection measures"""
        try:
            model_ensemble = self.models['revenue_impact']
            scaler = self.scalers['revenue_impact']
            
            feature_vector = self._prepare_feature_vector(features, 'revenue_impact')
            
            if len(feature_vector) == 0:
                return {'impact_amount': 0.0, 'confidence': 0.0, 'currency': 'EUR'}
            
            scaled_features = scaler.fit_transform([feature_vector])
            
            # Revenue prediction (regression)
            revenue_predictions = []
            weights = model_ensemble['ensemble_weights']
            
            model_names = [k for k in model_ensemble.keys() if k != 'ensemble_weights']
            for i, model_name in enumerate(model_names):
                try:
                    model = model_ensemble[model_name]
                    pred = model.predict(scaled_features)[0]
                    revenue_predictions.append(pred * weights[i])
                except Exception as e:
                    logger.warning(f"Revenue model {model_name} prediction failed: {str(e)}")
                    continue
            
            if revenue_predictions:
                ensemble_pred = np.sum(revenue_predictions)
                confidence = 1.0 - (np.std(revenue_predictions) / np.mean(revenue_predictions)) if revenue_predictions else 0.0
                
                return {
                    'impact_amount': float(max(0, ensemble_pred)),  # Ensure non-negative
                    'confidence': float(max(0, min(1, confidence))),
                    'currency': 'EUR',
                    'time_period': 'monthly',
                    'impact_breakdown': {
                        'protection_cost': float(ensemble_pred * 0.2),
                        'prevented_losses': float(ensemble_pred * 0.8),
                        'opportunity_cost': float(ensemble_pred * 0.1)
                    }
                }
            else:
                return {'impact_amount': 0.0, 'confidence': 0.0, 'currency': 'EUR'}
                
        except Exception as e:
            logger.error(f"Revenue impact prediction failed: {str(e)}")
            return {'impact_amount': 0.0, 'confidence': 0.0, 'currency': 'EUR'}
    
    async def _predict_threat_severity(self, features: Dict[str, Any], threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict threat severity evolution"""
        try:
            if not threats:
                return {'severity': 'none', 'escalation_probability': 0.0, 'confidence': 1.0}
            
            # Analyze current threats
            current_severity = max([self._map_severity_to_score(t.get('severity', 'low')) for t in threats])
            threat_count = len(threats)
            
            # Predict escalation
            escalation_factors = self._calculate_escalation_factors(features, threats)
            escalation_probability = min(1.0, sum(escalation_factors.values()) / len(escalation_factors))
            
            # Future severity prediction
            predicted_severity_score = current_severity * (1 + escalation_probability * 0.5)
            predicted_severity = self._map_score_to_severity(predicted_severity_score)
            
            return {
                'current_severity': self._map_score_to_severity(current_severity),
                'predicted_severity': predicted_severity,
                'escalation_probability': float(escalation_probability),
                'threat_count': threat_count,
                'escalation_factors': escalation_factors,
                'confidence': 0.7,
                'time_to_escalation': self._predict_escalation_time(escalation_probability)
            }
            
        except Exception as e:
            logger.error(f"Threat severity prediction failed: {str(e)}")
            return {'severity': 'unknown', 'escalation_probability': 0.5, 'confidence': 0.0}
    
    async def _predict_user_behavior(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict user behavior patterns"""
        try:
            user_features = features.get('user_features', {})
            
            # Behavior classification
            behavior_score = sum([
                user_features.get('engagement_score', 0) * 0.3,
                user_features.get('compliance_score', 0) * 0.4,
                user_features.get('activity_score', 0) * 0.3
            ])
            
            if behavior_score >= 0.8:
                behavior_class = 'highly_compliant'
            elif behavior_score >= 0.6:
                behavior_class = 'compliant'
            elif behavior_score >= 0.4:
                behavior_class = 'neutral'
            elif behavior_score >= 0.2:
                behavior_class = 'risky'
            else:
                behavior_class = 'high_risk'
            
            # Predict future actions
            action_predictions = {
                'will_comply_with_takedown': min(1.0, behavior_score + 0.2),
                'will_repeat_violation': max(0.0, 1.0 - behavior_score),
                'will_escalate_dispute': max(0.0, 0.5 - behavior_score),
                'will_seek_legal_remedy': min(0.3, behavior_score * 0.5)
            }
            
            return {
                'behavior_class': behavior_class,
                'behavior_score': float(behavior_score),
                'action_predictions': action_predictions,
                'confidence': 0.75,
                'behavioral_trends': self._analyze_behavioral_trends(user_features)
            }
            
        except Exception as e:
            logger.error(f"User behavior prediction failed: {str(e)}")
            return {'behavior_class': 'unknown', 'confidence': 0.0}
    
    async def _predict_content_popularity(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict content popularity and spread"""
        try:
            content_features = features.get('content_features', {})
            
            # Popularity score calculation
            popularity_factors = {
                'content_quality': content_features.get('quality_score', 0.5),
                'trend_alignment': content_features.get('trend_score', 0.5),
                'viral_potential': content_features.get('viral_score', 0.3),
                'engagement_history': content_features.get('engagement_rate', 0.4)
            }
            
            popularity_score = np.mean(list(popularity_factors.values()))
            
            # Predict spread metrics
            predicted_views = int(popularity_score * 10000)  # Base prediction
            predicted_shares = int(predicted_views * 0.05)
            predicted_platforms = min(10, int(popularity_score * 15))
            
            # Time-based predictions
            peak_time = self._predict_peak_popularity_time(popularity_score)
            decay_rate = 1.0 - (popularity_score * 0.5)  # Higher popularity = slower decay
            
            return {
                'popularity_score': float(popularity_score),
                'predicted_metrics': {
                    'views': predicted_views,
                    'shares': predicted_shares,
                    'platforms_reached': predicted_platforms,
                    'peak_time_days': peak_time,
                    'decay_rate': float(decay_rate)
                },
                'popularity_factors': popularity_factors,
                'confidence': 0.6,
                'viral_probability': float(min(1.0, popularity_score * 1.5))
            }
            
        except Exception as e:
            logger.error(f"Content popularity prediction failed: {str(e)}")
            return {'popularity_score': 0.5, 'confidence': 0.0}
    
    async def _predict_protection_effectiveness(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict effectiveness of protection measures"""
        try:
            # Analyze protection factors
            protection_factors = {
                'fingerprint_quality': features.get('technical_features', {}).get('fingerprint_strength', 0.8),
                'detection_coverage': 0.85,  # Would be calculated from actual coverage
                'response_speed': 0.9,       # Based on system performance
                'legal_strength': features.get('content_features', {}).get('copyright_strength', 0.7)
            }
            
            effectiveness_score = np.mean(list(protection_factors.values()))
            
            # Predict protection outcomes
            protection_predictions = {
                'detection_rate': float(min(1.0, effectiveness_score + 0.1)),
                'false_positive_rate': float(max(0.0, 0.2 - effectiveness_score * 0.15)),
                'takedown_success_rate': float(min(1.0, effectiveness_score * 0.9 + 0.1)),
                'response_time_hours': float(max(1.0, 24 * (1.0 - effectiveness_score)))
            }
            
            return {
                'effectiveness_score': float(effectiveness_score),
                'protection_predictions': protection_predictions,
                'protection_factors': protection_factors,
                'confidence': 0.8,
                'improvement_recommendations': self._generate_protection_improvements(protection_factors)
            }
            
        except Exception as e:
            logger.error(f"Protection effectiveness prediction failed: {str(e)}")
            return {'effectiveness_score': 0.7, 'confidence': 0.0}
    
    async def update_model(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update prediction models based on feedback"""
        try:
            update_results = {
                'timestamp': datetime.utcnow().isoformat(),
                'samples_processed': len(feedback_data),
                'model_updates': [],
                'performance_improvements': {}
            }
            
            # Group feedback by prediction type
            feedback_by_type = self._group_feedback_by_type(feedback_data)
            
            for prediction_type, type_feedback in feedback_by_type.items():
                if prediction_type in self.models and len(type_feedback) >= 10:
                    # Retrain models for this prediction type
                    model_update = await self._retrain_prediction_model(prediction_type, type_feedback)
                    update_results['model_updates'].append(model_update)
                    
                    # Evaluate performance improvement
                    performance_improvement = self._evaluate_model_improvement(prediction_type, type_feedback)
                    update_results['performance_improvements'][prediction_type] = performance_improvement
            
            # Update feature importance
            await self._update_feature_importance(feedback_data)
            
            logger.info(f"Prediction models updated with {len(feedback_data)} feedback samples")
            
            return update_results
            
        except Exception as e:
            logger.error(f"Prediction model update failed: {str(e)}")
            raise
    
    # Helper methods for feature extraction and model operations
    def _extract_content_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content-specific features"""
        return {
            'file_size': content_data.get('file_size', 0),
            'duration': content_data.get('duration', 0),
            'quality_score': content_data.get('quality_score', 0.5),
            'format': content_data.get('format', ''),
            'upload_time': content_data.get('upload_time', ''),
            'copyright_strength': content_data.get('copyright_strength', 0.5)
        }
    
    def _extract_classification_features(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
Extract classification-based features"""
        classifications = classification.get('classifications', {})
        return {
            'adult_content_score': classifications.get('adult_content', 0.0),
            'violence_score': classifications.get('violence', 0.0),
            'copyright_risk_score': classifications.get('copyright_risk', 0.0),
            'overall_confidence': classification.get('confidence_scores', {}).get('overall', 0.0)
        }
    
    def _extract_threat_features(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
Extract threat-based features"""
        if not threats:
            return {'threat_count': 0, 'max_severity': 0.0, 'avg_confidence': 0.0}
        
        severities = [self._map_severity_to_score(t.get('severity', 'low')) for t in threats]
        confidences = [t.get('confidence', 0.0) for t in threats]
        
        return {
            'threat_count': len(threats),
            'max_severity': max(severities),
            'avg_severity': np.mean(severities),
            'avg_confidence': np.mean(confidences),
            'critical_threats': sum(1 for s in severities if s >= 0.8)
        }
    
    def _extract_pattern_features(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
Extract pattern-based features"""
        return {
            'anomaly_count': len(patterns.get('anomalies', [])),
            'usage_pattern_confidence': patterns.get('usage', {}).get('confidence', 0.0),
            'geographic_spread': patterns.get('geographic', {}).get('geographic_spread', 0.0),
            'behavioral_risk': patterns.get('behavioral_insights', {}).get('risk_score', 0.0)
        }
    
    def _extract_temporal_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Extract temporal features"""
        now = datetime.utcnow()
        upload_time = content_data.get('upload_time')
        
        if upload_time:
            upload_dt = pd.to_datetime(upload_time)
            age_hours = (now - upload_dt).total_seconds() / 3600
        else:
            age_hours = 0
        
        return {
            'content_age_hours': age_hours,
            'upload_hour': upload_dt.hour if upload_time else 12,
            'upload_day_of_week': upload_dt.weekday() if upload_time else 0,
            'is_weekend': upload_dt.weekday() >= 5 if upload_time else False
        }
    
    def _extract_user_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Extract user-based features"""
        user_data = content_data.get('user_data', {})
        return {
            'user_reputation': user_data.get('reputation_score', 0.5),
            'account_age_days': user_data.get('account_age_days', 0),
            'previous_violations': user_data.get('violation_count', 0),
            'engagement_score': user_data.get('engagement_score', 0.5),
            'compliance_score': user_data.get('compliance_score', 0.5)
        }
    
    def _extract_technical_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Extract technical features"""
        return {
            'fingerprint_strength': content_data.get('fingerprint_strength', 0.8),
            'compression_ratio': content_data.get('compression_ratio', 1.0),
            'metadata_completeness': content_data.get('metadata_completeness', 0.5),
            'file_integrity': content_data.get('file_integrity_score', 1.0)
        }
    
    def _flatten_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
Flatten nested feature dictionary"""
        flattened = {}
        for category, category_features in features.items():
            for feature_name, feature_value in category_features.items():
                flattened[f"{category}_{feature_name}"] = feature_value
        return flattened
    
    def _prepare_feature_vector(self, features: Dict[str, Any], prediction_type: str) -> List[float]:
        """Prepare feature vector for specific prediction type"""
        # Select relevant features for this prediction type
        relevant_features = self._get_relevant_features(prediction_type)
        
        vector = []
        for feature_name in relevant_features:
            value = features.get(feature_name, 0.0)
            if isinstance(value, (int, float)):
                vector.append(float(value))
            elif isinstance(value, bool):
                vector.append(float(value))
            else:
                vector.append(0.0)  # Default for non-numeric features
        
        return vector
    
    def _get_relevant_features(self, prediction_type: str) -> List[str]:
        """
Get relevant features for specific prediction type"""
        # This would be configured based on feature importance analysis
        base_features = [
            'content_features_file_size', 'content_features_quality_score',
            'classification_features_copyright_risk_score', 'threat_features_threat_count',
            'user_features_user_reputation', 'technical_features_fingerprint_strength'
        ]
        return base_features
    
    # Additional helper methods...
    def _map_severity_to_score(self, severity: str) -> float:
        """
Map severity string to numeric score"""
        mapping = {'low': 0.2, 'medium': 0.4, 'high': 0.7, 'critical': 1.0}
        return mapping.get(severity, 0.2)
    
    def _map_score_to_severity(self, score: float) -> str:
        """
Map numeric score to severity string"""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _predict_time_to_violation(self, probability: float) -> str:
        """
Predict time until potential violation"""
        if probability >= 0.8:
            return 'within_24_hours'
        elif probability >= 0.6:
            return 'within_week'
        elif probability >= 0.4:
            return 'within_month'
        else:
            return 'unlikely'
    
    def _predict_violation_type(self, features: Dict[str, Any]) -> str:
        """
Predict most likely type of violation"""
        # Simplified logic - would use ML model in practice
        copyright_risk = features.get('classification_features_copyright_risk_score', 0.0)
        if copyright_risk > 0.7:
            return 'direct_copy'
        elif copyright_risk > 0.4:
            return 'derivative_work'
        else:
            return 'unauthorized_distribution'
    
    # Additional methods would continue here for completeness...
    def _calculate_prediction_confidence(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
Calculate confidence scores for all predictions"""
        confidences = {}
        for pred_type, pred_data in predictions.items():
            if isinstance(pred_data, dict) and 'confidence' in pred_data:
                confidences[f'{pred_type}_confidence'] = pred_data['confidence']
            else:
                confidences[f'{pred_type}_confidence'] = 0.5
        
        # Overall confidence
        individual_confidences = list(confidences.values())
        confidences['overall_confidence'] = np.mean(individual_confidences) if individual_confidences else 0.0
        
        return confidences
    
    def _extract_feature_importance(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
Extract feature importance from trained models"""
        # Placeholder implementation
        return {'top_features': ['copyright_risk', 'user_reputation', 'threat_count']}
    
    def _identify_risk_factors(self, predictions: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """
Identify key risk factors from predictions"""
        # Placeholder implementation
        return {'primary_risks': ['high_copyright_risk', 'suspicious_user_behavior']}
    
    async def _generate_recommendations(self, predictions: Dict[str, Any], features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Generate actionable recommendations based on predictions"""
        # Placeholder implementation
        return [
            {'action': 'increase_monitoring', 'priority': 'high', 'reason': 'High violation likelihood'},
            {'action': 'strengthen_watermarks', 'priority': 'medium', 'reason': 'Medium protection effectiveness'}
        ]
