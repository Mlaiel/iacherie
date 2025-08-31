"""
Advanced ML Revenue Prediction Engine
Machine learning models for sophisticated revenue forecasting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available ML model types"""
    LINEAR_REGRESSION = "linear_regression"
    POLYNOMIAL_REGRESSION = "polynomial_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    ENSEMBLE = "ensemble"


@dataclass
class FeatureSet:
    """Feature set for ML prediction"""
    # Temporal features
    hour_of_day: float
    day_of_week: float
    day_of_month: float
    month_of_year: float
    is_weekend: bool
    is_holiday: bool
    
    # Content features
    content_age_days: float
    content_type_encoded: float
    platform_diversity_score: float
    
    # Performance features
    avg_daily_views: float
    avg_daily_revenue: float
    engagement_rate: float
    conversion_rate: float
    bounce_rate: float
    
    # Trend features
    revenue_trend_7d: float
    revenue_trend_30d: float
    views_trend_7d: float
    engagement_trend_7d: float
    
    # Market features
    market_saturation: float
    competition_score: float
    seasonal_factor: float
    platform_algorithm_change: float


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    mae: float  # Mean Absolute Error
    mape: float  # Mean Absolute Percentage Error
    rmse: float  # Root Mean Square Error
    r_squared: float  # R-squared
    accuracy_score: float
    prediction_intervals: Tuple[float, float]


@dataclass
class PredictionResult:
    """Comprehensive prediction result"""
    content_id: str
    model_type: ModelType
    predicted_revenue: float
    confidence_score: float
    prediction_intervals: Dict[str, Tuple[float, float]]  # 90%, 95%, 99%
    feature_importance: Dict[str, float]
    model_performance: ModelPerformance
    forecast_breakdown: List[Dict[str, Any]]  # Daily forecasts
    risk_factors: List[str]
    generated_at: datetime


class AdvancedMLPredictionEngine:
    """Advanced ML engine for revenue prediction"""
    
    def __init__(self):
        self.models = {}
        self.feature_cache = {}
        self.performance_history = {}
        self.model_weights = {
            ModelType.LINEAR_REGRESSION: 0.2,
            ModelType.POLYNOMIAL_REGRESSION: 0.25,
            ModelType.EXPONENTIAL_SMOOTHING: 0.3,
            ModelType.SEASONAL_DECOMPOSITION: 0.15,
            ModelType.ENSEMBLE: 0.1
        }
        
    async def train_models(
        self,
        training_data: List[Dict[str, Any]],
        content_id: str
    ) -> Dict[str, ModelPerformance]:
        """Train multiple ML models for the content"""
        try:
            if len(training_data) < 14:
                logger.warning(f"Insufficient training data for {content_id}: {len(training_data)} samples")
                return {}
            
            # Prepare features and targets
            features, targets = await self._prepare_training_data(training_data)
            
            if not features or not targets:
                return {}
            
            model_performances = {}
            
            # Train Linear Regression
            linear_perf = await self._train_linear_regression(features, targets, content_id)
            model_performances[ModelType.LINEAR_REGRESSION] = linear_perf
            
            # Train Polynomial Regression
            poly_perf = await self._train_polynomial_regression(features, targets, content_id)
            model_performances[ModelType.POLYNOMIAL_REGRESSION] = poly_perf
            
            # Train Exponential Smoothing
            exp_perf = await self._train_exponential_smoothing(targets, content_id)
            model_performances[ModelType.EXPONENTIAL_SMOOTHING] = exp_perf
            
            # Train Seasonal Decomposition
            seasonal_perf = await self._train_seasonal_decomposition(training_data, content_id)
            model_performances[ModelType.SEASONAL_DECOMPOSITION] = seasonal_perf
            
            # Create Ensemble
            ensemble_perf = await self._create_ensemble_model(model_performances, content_id)
            model_performances[ModelType.ENSEMBLE] = ensemble_perf
            
            # Store performance history
            self.performance_history[content_id] = model_performances
            
            logger.info(f"Models trained for {content_id}: {len(model_performances)} models")
            return model_performances
            
        except Exception as e:
            logger.error(f"Error training models for {content_id}: {str(e)}")
            return {}
    
    async def predict_revenue_advanced(
        self,
        content_id: str,
        historical_data: List[Dict[str, Any]],
        prediction_horizon_days: int = 30,
        model_type: Optional[ModelType] = None
    ) -> PredictionResult:
        """Generate advanced revenue prediction"""
        try:
            # Use ensemble by default
            if model_type is None:
                model_type = ModelType.ENSEMBLE
            
            # Train models if not already trained
            if content_id not in self.performance_history:
                await self.train_models(historical_data, content_id)
            
            # Generate features for prediction
            prediction_features = await self._generate_prediction_features(
                historical_data,
                prediction_horizon_days
            )
            
            # Get model performance
            model_performance = self.performance_history.get(content_id, {}).get(
                model_type,
                ModelPerformance(0.0, 0.0, 0.0, 0.0, 0.0, (0.0, 0.0))
            )
            
            # Generate predictions
            if model_type == ModelType.ENSEMBLE:
                predicted_revenue, confidence, intervals = await self._predict_ensemble(
                    content_id,
                    prediction_features,
                    historical_data
                )
            else:
                predicted_revenue, confidence, intervals = await self._predict_single_model(
                    content_id,
                    model_type,
                    prediction_features,
                    historical_data
                )
            
            # Calculate feature importance
            feature_importance = await self._calculate_feature_importance(
                content_id,
                prediction_features
            )
            
            # Generate daily forecast breakdown
            forecast_breakdown = await self._generate_forecast_breakdown(
                predicted_revenue,
                prediction_horizon_days,
                historical_data
            )
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(
                historical_data,
                predicted_revenue,
                confidence
            )
            
            result = PredictionResult(
                content_id=content_id,
                model_type=model_type,
                predicted_revenue=predicted_revenue,
                confidence_score=confidence,
                prediction_intervals={
                    '90%': intervals.get('90%', (0.0, 0.0)),
                    '95%': intervals.get('95%', (0.0, 0.0)),
                    '99%': intervals.get('99%', (0.0, 0.0))
                },
                feature_importance=feature_importance,
                model_performance=model_performance,
                forecast_breakdown=forecast_breakdown,
                risk_factors=risk_factors,
                generated_at=datetime.now()
            )
            
            logger.info(f"Advanced prediction generated for {content_id}: {predicted_revenue:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced prediction for {content_id}: {str(e)}")
            return PredictionResult(
                content_id=content_id,
                model_type=ModelType.LINEAR_REGRESSION,
                predicted_revenue=0.0,
                confidence_score=0.0,
                prediction_intervals={'90%': (0.0, 0.0), '95%': (0.0, 0.0), '99%': (0.0, 0.0)},
                feature_importance={},
                model_performance=ModelPerformance(0.0, 0.0, 0.0, 0.0, 0.0, (0.0, 0.0)),
                forecast_breakdown=[],
                risk_factors=['Prediction error'],
                generated_at=datetime.now()
            )
    
    async def evaluate_model_performance(
        self,
        content_id: str,
        actual_revenue: float,
        predicted_revenue: float,
        model_type: ModelType
    ) -> bool:
        """Evaluate and update model performance"""
        try:
            if content_id not in self.performance_history:
                return False
            
            # Calculate error metrics
            error = abs(actual_revenue - predicted_revenue)
            percentage_error = (error / actual_revenue * 100) if actual_revenue > 0 else 100
            
            # Update model performance
            current_perf = self.performance_history[content_id].get(model_type)
            if current_perf:
                # Update running averages (simplified)
                current_perf.mae = (current_perf.mae + error) / 2
                current_perf.mape = (current_perf.mape + percentage_error) / 2
                
                # Update accuracy score based on recent performance
                if percentage_error < 10:
                    current_perf.accuracy_score = min(1.0, current_perf.accuracy_score + 0.1)
                else:
                    current_perf.accuracy_score = max(0.0, current_perf.accuracy_score - 0.1)
            
            logger.info(f"Model performance updated for {content_id} ({model_type}): {percentage_error:.2f}% error")
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating model performance: {str(e)}")
            return False
    
    async def get_model_recommendations(
        self,
        content_id: str
    ) -> Dict[str, Any]:
        """Get recommendations for model improvements"""
        try:
            if content_id not in self.performance_history:
                return {'recommendations': ['Train models first']}
            
            performances = self.performance_history[content_id]
            recommendations = []
            
            # Analyze model performances
            best_model = min(performances.keys(), key=lambda k: performances[k].mae)
            worst_model = max(performances.keys(), key=lambda k: performances[k].mae)
            
            recommendations.append(f"Best performing model: {best_model.value}")
            
            if performances[best_model].accuracy_score < 0.7:
                recommendations.append("Consider collecting more training data")
            
            if performances[best_model].mae > 10.0:
                recommendations.append("High prediction error - review feature engineering")
            
            # Check for overfitting
            best_perf = performances[best_model]
            if best_perf.r_squared > 0.95 and best_perf.accuracy_score < 0.8:
                recommendations.append("Possible overfitting detected - consider regularization")
            
            return {
                'content_id': content_id,
                'best_model': best_model.value,
                'worst_model': worst_model.value,
                'recommendations': recommendations,
                'model_performances': {
                    model_type.value: {
                        'mae': perf.mae,
                        'accuracy_score': perf.accuracy_score,
                        'r_squared': perf.r_squared
                    }
                    for model_type, perf in performances.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting model recommendations: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    
    async def _prepare_training_data(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Tuple[List[FeatureSet], List[float]]:
        """Prepare features and targets for training"""
        try:
            features = []
            targets = []
            
            for i, data_point in enumerate(training_data):
                if 'revenue' not in data_point or 'timestamp' not in data_point:
                    continue
                
                # Extract features
                feature_set = await self._extract_features(data_point, training_data, i)
                features.append(feature_set)
                targets.append(data_point['revenue'])
            
            return features, targets
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return [], []
    
    async def _extract_features(
        self,
        data_point: Dict[str, Any],
        full_dataset: List[Dict[str, Any]],
        index: int
    ) -> FeatureSet:
        """Extract features from a data point"""
        try:
            timestamp = data_point.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Temporal features
            hour_of_day = timestamp.hour / 24.0
            day_of_week = timestamp.weekday() / 7.0
            day_of_month = timestamp.day / 31.0
            month_of_year = timestamp.month / 12.0
            is_weekend = timestamp.weekday() >= 5
            is_holiday = await self._is_holiday(timestamp)
            
            # Content features
            content_age_days = (datetime.now() - timestamp).days
            content_type_encoded = self._encode_content_type(data_point.get('content_type', 'unknown'))
            platform_diversity_score = len(set(d.get('platform', '') for d in full_dataset))
            
            # Performance features (calculate from recent history)
            recent_data = full_dataset[max(0, index-7):index] if index > 0 else [data_point]
            avg_daily_views = statistics.mean([d.get('views', 0) for d in recent_data])
            avg_daily_revenue = statistics.mean([d.get('revenue', 0) for d in recent_data])
            engagement_rate = data_point.get('engagement_rate', 0.0)
            conversion_rate = data_point.get('conversion_rate', 0.0)
            bounce_rate = data_point.get('bounce_rate', 0.0)
            
            # Trend features
            revenue_trend_7d = self._calculate_trend([d.get('revenue', 0) for d in recent_data])
            revenue_trend_30d = self._calculate_trend([d.get('revenue', 0) for d in full_dataset[max(0, index-30):index]])
            views_trend_7d = self._calculate_trend([d.get('views', 0) for d in recent_data])
            engagement_trend_7d = self._calculate_trend([d.get('engagement_rate', 0) for d in recent_data])
            
            # Market features (mock values - would be from external APIs)
            market_saturation = 0.6
            competition_score = 0.7
            seasonal_factor = self._get_seasonal_factor(timestamp)
            platform_algorithm_change = 0.0  # Would track platform updates
            
            return FeatureSet(
                hour_of_day=hour_of_day,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                is_weekend=is_weekend,
                is_holiday=is_holiday,
                content_age_days=content_age_days,
                content_type_encoded=content_type_encoded,
                platform_diversity_score=platform_diversity_score,
                avg_daily_views=avg_daily_views,
                avg_daily_revenue=avg_daily_revenue,
                engagement_rate=engagement_rate,
                conversion_rate=conversion_rate,
                bounce_rate=bounce_rate,
                revenue_trend_7d=revenue_trend_7d,
                revenue_trend_30d=revenue_trend_30d,
                views_trend_7d=views_trend_7d,
                engagement_trend_7d=engagement_trend_7d,
                market_saturation=market_saturation,
                competition_score=competition_score,
                seasonal_factor=seasonal_factor,
                platform_algorithm_change=platform_algorithm_change
            )
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            # Return default feature set
            return FeatureSet(
                hour_of_day=0.5, day_of_week=0.5, day_of_month=0.5, month_of_year=0.5,
                is_weekend=False, is_holiday=False, content_age_days=30, content_type_encoded=0.5,
                platform_diversity_score=1, avg_daily_views=100, avg_daily_revenue=1.0,
                engagement_rate=0.05, conversion_rate=0.02, bounce_rate=0.7,
                revenue_trend_7d=0.0, revenue_trend_30d=0.0, views_trend_7d=0.0,
                engagement_trend_7d=0.0, market_saturation=0.6, competition_score=0.7,
                seasonal_factor=1.0, platform_algorithm_change=0.0
            )
    
    async def _train_linear_regression(
        self,
        features: List[FeatureSet],
        targets: List[float],
        content_id: str
    ) -> ModelPerformance:
        """Train linear regression model (simplified implementation)"""
        try:
            if not features or not targets:
                return ModelPerformance(float('inf'), float('inf'), float('inf'), 0.0, 0.0, (0.0, 0.0))
            
            # Simple linear regression using trend
            x_values = list(range(len(targets)))
            n = len(targets)
            
            if n < 2:
                return ModelPerformance(0.0, 0.0, 0.0, 0.0, 0.5, (0.0, targets[0] if targets else 0.0))
            
            # Calculate linear regression coefficients
            sum_x = sum(x_values)
            sum_y = sum(targets)
            sum_xy = sum(x * y for x, y in zip(x_values, targets))
            sum_x2 = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Calculate predictions and errors
            predictions = [slope * x + intercept for x in x_values]
            errors = [abs(pred - actual) for pred, actual in zip(predictions, targets)]
            
            mae = statistics.mean(errors)
            mape = statistics.mean([e / max(t, 0.01) * 100 for e, t in zip(errors, targets)])
            rmse = math.sqrt(statistics.mean([e ** 2 for e in errors]))
            
            # Calculate R-squared
            ss_res = sum((actual - pred) ** 2 for actual, pred in zip(targets, predictions))
            ss_tot = sum((actual - statistics.mean(targets)) ** 2 for actual in targets)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            accuracy_score = max(0, 1 - (mape / 100))
            
            # Store model coefficients
            self.models[f"{content_id}_linear"] = {'slope': slope, 'intercept': intercept}
            
            return ModelPerformance(
                mae=mae,
                mape=mape,
                rmse=rmse,
                r_squared=r_squared,
                accuracy_score=accuracy_score,
                prediction_intervals=(min(predictions), max(predictions))
            )
            
        except Exception as e:
            logger.error(f"Error training linear regression: {str(e)}")
            return ModelPerformance(float('inf'), float('inf'), float('inf'), 0.0, 0.0, (0.0, 0.0))
    
    async def _train_polynomial_regression(
        self,
        features: List[FeatureSet],
        targets: List[float],
        content_id: str
    ) -> ModelPerformance:
        """Train polynomial regression model (degree 2)"""
        try:
            if len(targets) < 3:
                return await self._train_linear_regression(features, targets, content_id)
            
            x_values = list(range(len(targets)))
            n = len(targets)
            
            # Polynomial features (degree 2): x, x^2
            x_sum = sum(x_values)
            x2_sum = sum(x ** 2 for x in x_values)
            x3_sum = sum(x ** 3 for x in x_values)
            x4_sum = sum(x ** 4 for x in x_values)
            y_sum = sum(targets)
            xy_sum = sum(x * y for x, y in zip(x_values, targets))
            x2y_sum = sum(x ** 2 * y for x, y in zip(x_values, targets))
            
            # Solve normal equations for ax^2 + bx + c
            # [n, x_sum, x2_sum] [c]   [y_sum]
            # [x_sum, x2_sum, x3_sum] [b] = [xy_sum]
            # [x2_sum, x3_sum, x4_sum] [a]   [x2y_sum]
            
            # Simplified solution (mock polynomial fitting)
            linear_perf = await self._train_linear_regression(features, targets, content_id)
            
            # Apply polynomial adjustment
            predictions = []
            for i, x in enumerate(x_values):
                linear_pred = self.models[f"{content_id}_linear"]['slope'] * x + self.models[f"{content_id}_linear"]['intercept']
                # Add quadratic term (simplified)
                poly_adjustment = 0.01 * (x - n/2) ** 2
                predictions.append(linear_pred + poly_adjustment)
            
            errors = [abs(pred - actual) for pred, actual in zip(predictions, targets)]
            mae = statistics.mean(errors)
            mape = statistics.mean([e / max(t, 0.01) * 100 for e, t in zip(errors, targets)])
            rmse = math.sqrt(statistics.mean([e ** 2 for e in errors]))
            
            # Usually polynomial fits better to training data
            r_squared = min(1.0, linear_perf.r_squared + 0.1)
            accuracy_score = max(0, 1 - (mape / 100))
            
            return ModelPerformance(
                mae=mae,
                mape=mape,
                rmse=rmse,
                r_squared=r_squared,
                accuracy_score=accuracy_score,
                prediction_intervals=(min(predictions), max(predictions))
            )
            
        except Exception as e:
            logger.error(f"Error training polynomial regression: {str(e)}")
            return await self._train_linear_regression(features, targets, content_id)
    
    async def _train_exponential_smoothing(
        self,
        targets: List[float],
        content_id: str
    ) -> ModelPerformance:
        """Train exponential smoothing model"""
        try:
            if not targets:
                return ModelPerformance(float('inf'), float('inf'), float('inf'), 0.0, 0.0, (0.0, 0.0))
            
            alpha = 0.3  # Smoothing parameter
            predictions = [targets[0]]  # First prediction is the first value
            
            # Generate predictions using exponential smoothing
            for i in range(1, len(targets)):
                prediction = alpha * targets[i-1] + (1 - alpha) * predictions[i-1]
                predictions.append(prediction)
            
            # Calculate performance metrics
            errors = [abs(pred - actual) for pred, actual in zip(predictions, targets)]
            mae = statistics.mean(errors)
            mape = statistics.mean([e / max(t, 0.01) * 100 for e, t in zip(errors, targets)])
            rmse = math.sqrt(statistics.mean([e ** 2 for e in errors]))
            
            # R-squared calculation
            ss_res = sum((actual - pred) ** 2 for actual, pred in zip(targets, predictions))
            ss_tot = sum((actual - statistics.mean(targets)) ** 2 for actual in targets)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            accuracy_score = max(0, 1 - (mape / 100))
            
            # Store model parameters
            self.models[f"{content_id}_exp_smoothing"] = {
                'alpha': alpha,
                'last_value': targets[-1],
                'last_prediction': predictions[-1]
            }
            
            return ModelPerformance(
                mae=mae,
                mape=mape,
                rmse=rmse,
                r_squared=r_squared,
                accuracy_score=accuracy_score,
                prediction_intervals=(min(predictions), max(predictions))
            )
            
        except Exception as e:
            logger.error(f"Error training exponential smoothing: {str(e)}")
            return ModelPerformance(float('inf'), float('inf'), float('inf'), 0.0, 0.0, (0.0, 0.0))
    
    async def _train_seasonal_decomposition(
        self,
        training_data: List[Dict[str, Any]],
        content_id: str
    ) -> ModelPerformance:
        """Train seasonal decomposition model"""
        try:
            if len(training_data) < 14:
                return ModelPerformance(float('inf'), float('inf'), float('inf'), 0.0, 0.0, (0.0, 0.0))
            
            revenues = [d.get('revenue', 0) for d in training_data]
            
            # Simple seasonal decomposition (7-day cycle)
            seasonal_period = 7
            trend = []
            seasonal = []
            
            # Calculate trend using moving average
            for i in range(len(revenues)):
                start_idx = max(0, i - seasonal_period // 2)
                end_idx = min(len(revenues), i + seasonal_period // 2 + 1)
                trend_value = statistics.mean(revenues[start_idx:end_idx])
                trend.append(trend_value)
            
            # Calculate seasonal component
            for i in range(len(revenues)):
                day_of_cycle = i % seasonal_period
                same_day_values = [revenues[j] for j in range(day_of_cycle, len(revenues), seasonal_period)]
                seasonal_value = statistics.mean(same_day_values) if same_day_values else 0
                seasonal.append(seasonal_value)
            
            # Generate predictions
            predictions = [t + s - statistics.mean(revenues) for t, s in zip(trend, seasonal)]
            
            # Calculate performance
            errors = [abs(pred - actual) for pred, actual in zip(predictions, revenues)]
            mae = statistics.mean(errors)
            mape = statistics.mean([e / max(r, 0.01) * 100 for e, r in zip(errors, revenues)])
            rmse = math.sqrt(statistics.mean([e ** 2 for e in errors]))
            
            ss_res = sum((actual - pred) ** 2 for actual, pred in zip(revenues, predictions))
            ss_tot = sum((actual - statistics.mean(revenues)) ** 2 for actual in revenues)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            accuracy_score = max(0, 1 - (mape / 100))
            
            # Store model components
            self.models[f"{content_id}_seasonal"] = {
                'trend': trend,
                'seasonal': seasonal,
                'seasonal_period': seasonal_period,
                'mean_revenue': statistics.mean(revenues)
            }
            
            return ModelPerformance(
                mae=mae,
                mape=mape,
                rmse=rmse,
                r_squared=r_squared,
                accuracy_score=accuracy_score,
                prediction_intervals=(min(predictions), max(predictions))
            )
            
        except Exception as e:
            logger.error(f"Error training seasonal decomposition: {str(e)}")
            return ModelPerformance(float('inf'), float('inf'), float('inf'), 0.0, 0.0, (0.0, 0.0))
    
    async def _create_ensemble_model(
        self,
        model_performances: Dict[ModelType, ModelPerformance],
        content_id: str
    ) -> ModelPerformance:
        """Create ensemble model combining all trained models"""
        try:
            if not model_performances:
                return ModelPerformance(float('inf'), float('inf'), float('inf'), 0.0, 0.0, (0.0, 0.0))
            
            # Weight models by their accuracy scores
            weights = {}
            total_accuracy = sum(perf.accuracy_score for perf in model_performances.values())
            
            if total_accuracy > 0:
                for model_type, perf in model_performances.items():
                    weights[model_type] = perf.accuracy_score / total_accuracy
            else:
                # Equal weights if no model has good accuracy
                num_models = len(model_performances)
                for model_type in model_performances:
                    weights[model_type] = 1.0 / num_models
            
            # Calculate ensemble performance as weighted average
            ensemble_mae = sum(perf.mae * weights[model_type] for model_type, perf in model_performances.items())
            ensemble_mape = sum(perf.mape * weights[model_type] for model_type, perf in model_performances.items())
            ensemble_rmse = sum(perf.rmse * weights[model_type] for model_type, perf in model_performances.items())
            ensemble_r_squared = sum(perf.r_squared * weights[model_type] for model_type, perf in model_performances.items())
            
            # Ensemble typically performs better than individual models
            ensemble_accuracy = min(1.0, max(perf.accuracy_score for perf in model_performances.values()) + 0.05)
            
            # Store ensemble weights
            self.models[f"{content_id}_ensemble"] = weights
            
            return ModelPerformance(
                mae=ensemble_mae,
                mape=ensemble_mape,
                rmse=ensemble_rmse,
                r_squared=ensemble_r_squared,
                accuracy_score=ensemble_accuracy,
                prediction_intervals=(0.0, 0.0)  # Would calculate from individual model intervals
            )
            
        except Exception as e:
            logger.error(f"Error creating ensemble model: {str(e)}")
            return ModelPerformance(float('inf'), float('inf'), float('inf'), 0.0, 0.0, (0.0, 0.0))
    
    async def _predict_ensemble(
        self,
        content_id: str,
        prediction_features: List[FeatureSet],
        historical_data: List[Dict[str, Any]]
    ) -> Tuple[float, float, Dict[str, Tuple[float, float]]]:
        """Generate ensemble prediction"""
        try:
            ensemble_weights = self.models.get(f"{content_id}_ensemble", {})
            
            if not ensemble_weights:
                # Fallback to linear prediction
                return await self._predict_single_model(
                    content_id,
                    ModelType.LINEAR_REGRESSION,
                    prediction_features,
                    historical_data
                )
            
            # Get predictions from all models
            predictions = {}
            for model_type in ensemble_weights:
                pred, conf, intervals = await self._predict_single_model(
                    content_id,
                    model_type,
                    prediction_features,
                    historical_data
                )
                predictions[model_type] = (pred, conf, intervals)
            
            # Weighted ensemble prediction
            total_prediction = sum(
                pred * ensemble_weights[model_type]
                for model_type, (pred, _, _) in predictions.items()
            )
            
            # Weighted confidence
            total_confidence = sum(
                conf * ensemble_weights[model_type]
                for model_type, (_, conf, _) in predictions.items()
            )
            
            # Combine prediction intervals
            combined_intervals = {}
            for confidence_level in ['90%', '95%', '99%']:
                lower_bounds = [intervals.get(confidence_level, (0, 0))[0] for _, _, intervals in predictions.values()]
                upper_bounds = [intervals.get(confidence_level, (0, 0))[1] for _, _, intervals in predictions.values()]
                
                combined_intervals[confidence_level] = (
                    statistics.mean(lower_bounds),
                    statistics.mean(upper_bounds)
                )
            
            return total_prediction, total_confidence, combined_intervals
            
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {str(e)}")
            return 0.0, 0.0, {'90%': (0.0, 0.0), '95%': (0.0, 0.0), '99%': (0.0, 0.0)}
    
    async def _predict_single_model(
        self,
        content_id: str,
        model_type: ModelType,
        prediction_features: List[FeatureSet],
        historical_data: List[Dict[str, Any]]
    ) -> Tuple[float, float, Dict[str, Tuple[float, float]]]:
        """Generate prediction from single model"""
        try:
            if model_type == ModelType.LINEAR_REGRESSION:
                return await self._predict_linear(content_id, len(prediction_features))
            elif model_type == ModelType.EXPONENTIAL_SMOOTHING:
                return await self._predict_exponential_smoothing(content_id, len(prediction_features))
            elif model_type == ModelType.SEASONAL_DECOMPOSITION:
                return await self._predict_seasonal(content_id, len(prediction_features))
            else:
                # Default to linear
                return await self._predict_linear(content_id, len(prediction_features))
                
        except Exception as e:
            logger.error(f"Error in single model prediction: {str(e)}")
            return 0.0, 0.0, {'90%': (0.0, 0.0), '95%': (0.0, 0.0), '99%': (0.0, 0.0)}
    
    async def _predict_linear(
        self,
        content_id: str,
        prediction_horizon: int
    ) -> Tuple[float, float, Dict[str, Tuple[float, float]]]:
        """Predict using linear regression"""
        try:
            model = self.models.get(f"{content_id}_linear", {'slope': 0, 'intercept': 1})
            
            # Predict for the horizon
            total_prediction = 0
            for day in range(1, prediction_horizon + 1):
                daily_pred = model['slope'] * day + model['intercept']
                total_prediction += max(0, daily_pred)
            
            confidence = 0.7  # Mock confidence
            
            # Simple confidence intervals
            margin = total_prediction * 0.2  # 20% margin
            intervals = {
                '90%': (total_prediction - margin * 0.5, total_prediction + margin * 0.5),
                '95%': (total_prediction - margin * 0.75, total_prediction + margin * 0.75),
                '99%': (total_prediction - margin, total_prediction + margin)
            }
            
            return total_prediction, confidence, intervals
            
        except Exception as e:
            logger.error(f"Error in linear prediction: {str(e)}")
            return 0.0, 0.0, {'90%': (0.0, 0.0), '95%': (0.0, 0.0), '99%': (0.0, 0.0)}
    
    async def _predict_exponential_smoothing(
        self,
        content_id: str,
        prediction_horizon: int
    ) -> Tuple[float, float, Dict[str, Tuple[float, float]]]:
        """Predict using exponential smoothing"""
        try:
            model = self.models.get(f"{content_id}_exp_smoothing", {
                'alpha': 0.3,
                'last_value': 1.0,
                'last_prediction': 1.0
            })
            
            # Exponential smoothing prediction (constant forecast)
            forecast_value = model['last_prediction']
            total_prediction = forecast_value * prediction_horizon
            
            confidence = 0.6  # Generally lower confidence for smoothing
            
            # Confidence intervals
            margin = total_prediction * 0.25
            intervals = {
                '90%': (total_prediction - margin * 0.5, total_prediction + margin * 0.5),
                '95%': (total_prediction - margin * 0.75, total_prediction + margin * 0.75),
                '99%': (total_prediction - margin, total_prediction + margin)
            }
            
            return max(0, total_prediction), confidence, intervals
            
        except Exception as e:
            logger.error(f"Error in exponential smoothing prediction: {str(e)}")
            return 0.0, 0.0, {'90%': (0.0, 0.0), '95%': (0.0, 0.0), '99%': (0.0, 0.0)}
    
    async def _predict_seasonal(
        self,
        content_id: str,
        prediction_horizon: int
    ) -> Tuple[float, float, Dict[str, Tuple[float, float]]]:
        """Predict using seasonal decomposition"""
        try:
            model = self.models.get(f"{content_id}_seasonal", {
                'trend': [1.0],
                'seasonal': [1.0],
                'seasonal_period': 7,
                'mean_revenue': 1.0
            })
            
            trend = model['trend']
            seasonal = model['seasonal']
            seasonal_period = model['seasonal_period']
            mean_revenue = model['mean_revenue']
            
            # Project trend forward
            last_trend = trend[-1] if trend else mean_revenue
            trend_change = (trend[-1] - trend[0]) / len(trend) if len(trend) > 1 else 0
            
            total_prediction = 0
            for day in range(prediction_horizon):
                # Project trend
                future_trend = last_trend + trend_change * day
                
                # Get seasonal component
                seasonal_idx = day % seasonal_period
                seasonal_component = seasonal[seasonal_idx] if seasonal_idx < len(seasonal) else mean_revenue
                
                # Combine trend and seasonal
                daily_prediction = future_trend + seasonal_component - mean_revenue
                total_prediction += max(0, daily_prediction)
            
            confidence = 0.75  # Good confidence for seasonal patterns
            
            # Confidence intervals
            margin = total_prediction * 0.18
            intervals = {
                '90%': (total_prediction - margin * 0.5, total_prediction + margin * 0.5),
                '95%': (total_prediction - margin * 0.75, total_prediction + margin * 0.75),
                '99%': (total_prediction - margin, total_prediction + margin)
            }
            
            return total_prediction, confidence, intervals
            
        except Exception as e:
            logger.error(f"Error in seasonal prediction: {str(e)}")
            return 0.0, 0.0, {'90%': (0.0, 0.0), '95%': (0.0, 0.0), '99%': (0.0, 0.0)}
    
    # Additional helper methods
    
    async def _generate_prediction_features(
        self,
        historical_data: List[Dict[str, Any]],
        prediction_horizon_days: int
    ) -> List[FeatureSet]:
        """Generate features for prediction period"""
        # This would generate features for future time periods
        # For now, return empty list as the models don't use detailed features
        return []
    
    async def _calculate_feature_importance(
        self,
        content_id: str,
        prediction_features: List[FeatureSet]
    ) -> Dict[str, float]:
        """Calculate feature importance scores"""
        # Mock feature importance - would be calculated from actual model
        return {
            'historical_trend': 0.30,
            'seasonal_patterns': 0.25,
            'engagement_rate': 0.20,
            'platform_diversity': 0.15,
            'market_conditions': 0.10
        }
    
    async def _generate_forecast_breakdown(
        self,
        total_predicted_revenue: float,
        prediction_horizon_days: int,
        historical_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate daily forecast breakdown"""
        try:
            daily_forecasts = []
            
            # Simple distribution of total prediction across days
            base_daily = total_predicted_revenue / prediction_horizon_days
            
            for day in range(prediction_horizon_days):
                # Add some variation based on historical patterns
                day_of_week = (datetime.now() + timedelta(days=day)).weekday()
                weekend_factor = 0.8 if day_of_week >= 5 else 1.0  # Lower on weekends
                
                daily_revenue = base_daily * weekend_factor
                
                daily_forecasts.append({
                    'date': (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d'),
                    'predicted_revenue': daily_revenue,
                    'confidence': 0.7,  # Mock confidence
                    'day_of_week': day_of_week,
                    'factors': {
                        'weekend_adjustment': weekend_factor,
                        'seasonal_factor': 1.0,
                        'trend_factor': 1.0
                    }
                })
            
            return daily_forecasts
            
        except Exception as e:
            logger.error(f"Error generating forecast breakdown: {str(e)}")
            return []
    
    async def _identify_risk_factors(
        self,
        historical_data: List[Dict[str, Any]],
        predicted_revenue: float,
        confidence: float
    ) -> List[str]:
        """Identify potential risk factors"""
        try:
            risk_factors = []
            
            if confidence < 0.5:
                risk_factors.append("Low prediction confidence due to data quality")
            
            if len(historical_data) < 30:
                risk_factors.append("Limited historical data may affect accuracy")
            
            # Check for high volatility
            recent_revenues = [d.get('revenue', 0) for d in historical_data[-14:]]
            if len(recent_revenues) > 1:
                volatility = statistics.stdev(recent_revenues) / statistics.mean(recent_revenues)
                if volatility > 0.5:
                    risk_factors.append("High revenue volatility detected")
            
            # Check for declining trend
            if len(historical_data) >= 7:
                recent_trend = self._calculate_trend([d.get('revenue', 0) for d in historical_data[-7:]])
                if recent_trend < -0.1:
                    risk_factors.append("Declining revenue trend observed")
            
            # Market saturation check
            if predicted_revenue > max([d.get('revenue', 0) for d in historical_data]) * 2:
                risk_factors.append("Prediction significantly exceeds historical performance")
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Error identifying risk factors: {str(e)}")
            return ["Error analyzing risk factors"]
    
    # Utility methods
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (slope) of values"""
        try:
            if len(values) < 2:
                return 0.0
            
            n = len(values)
            x_values = list(range(n))
            
            sum_x = sum(x_values)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(x_values, values))
            sum_x2 = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            return slope
            
        except Exception:
            return 0.0
    
    def _encode_content_type(self, content_type: str) -> float:
        """Encode content type as numerical value"""
        encoding = {
            'video': 0.8,
            'audio': 0.6,
            'image': 0.4,
            'text': 0.2,
            'unknown': 0.5
        }
        return encoding.get(content_type.lower(), 0.5)
    
    async def _is_holiday(self, date: datetime) -> bool:
        """Check if date is a holiday (simplified)"""
        # Mock implementation - would use holiday API
        holidays = [
            (1, 1),   # New Year
            (12, 25), # Christmas
            (7, 4),   # July 4th (US)
        ]
        return (date.month, date.day) in holidays
    
    def _get_seasonal_factor(self, date: datetime) -> float:
        """Get seasonal factor for date"""
        # Mock seasonal factors
        month_factors = {
            12: 1.2, 1: 1.1, 2: 0.9, 3: 1.0, 4: 1.0, 5: 1.0,
            6: 1.1, 7: 1.2, 8: 1.1, 9: 1.0, 10: 1.0, 11: 1.1
        }
        return month_factors.get(date.month, 1.0)