"""AI Revenue Analytics Repository

Enterprise-grade repository for AI-powered revenue prediction, optimization,
and comprehensive analytics for content creators and influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, asc, and_, or_, func, text
import numpy as np

from .base_repository import BaseRepository
from ..models.ai_revenue_analytics import (
    AIRevenueAnalytics,
    OptimizationExperiment,
    PredictionValidation,
    ModelType,
    PredictionTimeframe,
    ExperimentStatus,
    ValidationStatus
)
from ..connections.manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class AIRevenueAnalyticsRepository(BaseRepository[AIRevenueAnalytics]):
    """
    Enterprise AI Revenue Analytics Repository
    
    Manages AI-powered revenue predictions, optimization experiments, and
    advanced analytics for content creator revenue optimization.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(AIRevenueAnalytics, db_session)
        self.model = AIRevenueAnalytics
    
    async def create_revenue_analytics(
        self,
        user_id: str,
        content_fingerprint_id: str,
        model_type: ModelType,
        timeframe: PredictionTimeframe,
        prediction_data: Dict[str, Any],
        **kwargs
    ) -> AIRevenueAnalytics:
        """
        Create new AI revenue analytics record
        
        Args:
            user_id: User UUID
            content_fingerprint_id: Content fingerprint UUID
            model_type: ML model type used for prediction
            timeframe: Prediction timeframe
            prediction_data: Detailed prediction results
            **kwargs: Additional analytics parameters
            
        Returns:
            Created AIRevenueAnalytics instance
        """
        try:
            analytics_data = {
                "user_id": user_id,
                "content_fingerprint_id": content_fingerprint_id,
                "model_type": model_type,
                "prediction_timeframe": timeframe,
                "predicted_revenue": Decimal(str(prediction_data.get('predicted_revenue', 0.0))),
                "confidence_score": prediction_data.get('confidence_score', 0.0),
                "prediction_data": prediction_data,
                "model_version": kwargs.get('model_version', '1.0.0'),
                "features_used": kwargs.get('features_used', []),
                **kwargs
            }
            
            # Calculate historical accuracy if available
            if 'historical_accuracy' in prediction_data:
                analytics_data['historical_accuracy'] = prediction_data['historical_accuracy']
            
            # Set engagement predictions
            if 'engagement_predictions' in prediction_data:
                analytics_data['predicted_engagement'] = prediction_data['engagement_predictions']
            
            # Set optimization suggestions
            if 'optimization_suggestions' in prediction_data:
                analytics_data['optimization_suggestions'] = prediction_data['optimization_suggestions']
            
            revenue_analytics = AIRevenueAnalytics(**analytics_data)
            
            self.db_session.add(revenue_analytics)
            await self.db_session.commit()
            await self.db_session.refresh(revenue_analytics)
            
            logger.info(f"Created revenue analytics: {revenue_analytics.id} for user: {user_id}")
            return revenue_analytics
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create revenue analytics: {str(e)}")
            raise
    
    async def update_actual_revenue(
        self,
        analytics_id: str,
        actual_revenue: Decimal,
        actual_engagement: Optional[Dict[str, Any]] = None
    ) -> AIRevenueAnalytics:
        """
        Update actual revenue for prediction validation
        
        Args:
            analytics_id: AIRevenueAnalytics UUID
            actual_revenue: Actual revenue achieved
            actual_engagement: Actual engagement metrics
            
        Returns:
            Updated AIRevenueAnalytics instance
        """
        try:
            analytics_record = await self.get_by_id(analytics_id)
            if not analytics_record:
                raise ValueError(f"Revenue analytics not found: {analytics_id}")
            
            analytics_record.actual_revenue = actual_revenue
            analytics_record.revenue_variance = abs(actual_revenue - analytics_record.predicted_revenue)
            
            # Calculate prediction accuracy
            if analytics_record.predicted_revenue > 0:
                accuracy = 1.0 - float(analytics_record.revenue_variance / analytics_record.predicted_revenue)
                analytics_record.prediction_accuracy = max(0.0, min(1.0, accuracy))
            
            if actual_engagement:
                analytics_record.actual_engagement = actual_engagement
            
            analytics_record.prediction_validated = True
            analytics_record.validation_date = datetime.now(timezone.utc)
            
            await self.db_session.commit()
            
            logger.info(f"Updated actual revenue for analytics: {analytics_id} - Accuracy: {analytics_record.prediction_accuracy:.2%}")
            return analytics_record
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update actual revenue: {str(e)}")
            raise
    
    async def get_model_performance(
        self,
        model_type: ModelType,
        timeframe: Optional[PredictionTimeframe] = None,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a specific model
        
        Args:
            model_type: ML model type
            timeframe: Optional timeframe filter
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing model performance metrics
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            query = self.db_session.query(self.model).filter(
                and_(
                    self.model.model_type == model_type,
                    self.model.created_at >= cutoff_date,
                    self.model.prediction_validated == True
                )
            )
            
            if timeframe:
                query = query.filter(self.model.prediction_timeframe == timeframe)
            
            validated_predictions = query.all()
            
            if not validated_predictions:
                return {
                    "model_type": model_type.value,
                    "total_predictions": 0,
                    "average_accuracy": 0.0,
                    "average_confidence": 0.0,
                    "performance_trend": "insufficient_data"
                }
            
            # Calculate performance metrics
            accuracies = [p.prediction_accuracy for p in validated_predictions if p.prediction_accuracy is not None]
            confidences = [p.confidence_score for p in validated_predictions]
            
            avg_accuracy = np.mean(accuracies) if accuracies else 0.0
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            # Revenue prediction analysis
            revenue_errors = []
            for prediction in validated_predictions:
                if prediction.actual_revenue and prediction.predicted_revenue:
                    error = abs(float(prediction.actual_revenue - prediction.predicted_revenue))
                    revenue_errors.append(error)
            
            avg_revenue_error = np.mean(revenue_errors) if revenue_errors else 0.0
            
            # Performance trend analysis
            recent_predictions = [p for p in validated_predictions if p.validation_date and 
                                p.validation_date >= datetime.now(timezone.utc) - timedelta(days=30)]
            
            if len(recent_predictions) >= 5:
                recent_accuracies = [p.prediction_accuracy for p in recent_predictions if p.prediction_accuracy is not None]
                older_accuracies = [p.prediction_accuracy for p in validated_predictions 
                                  if p not in recent_predictions and p.prediction_accuracy is not None]
                
                if recent_accuracies and older_accuracies:
                    recent_avg = np.mean(recent_accuracies)
                    older_avg = np.mean(older_accuracies)
                    
                    if recent_avg > older_avg + 0.05:
                        trend = "improving"
                    elif recent_avg < older_avg - 0.05:
                        trend = "declining"
                    else:
                        trend = "stable"
                else:
                    trend = "unknown"
            else:
                trend = "insufficient_recent_data"
            
            performance_metrics = {
                "model_type": model_type.value,
                "timeframe": timeframe.value if timeframe else "all",
                "total_predictions": len(validated_predictions),
                "average_accuracy": round(avg_accuracy, 4),
                "average_confidence": round(avg_confidence, 4),
                "average_revenue_error": round(avg_revenue_error, 2),
                "performance_trend": trend,
                "accuracy_distribution": {
                    "excellent": len([a for a in accuracies if a >= 0.9]),
                    "good": len([a for a in accuracies if 0.7 <= a < 0.9]),
                    "fair": len([a for a in accuracies if 0.5 <= a < 0.7]),
                    "poor": len([a for a in accuracies if a < 0.5])
                },
                "confidence_distribution": {
                    "high": len([c for c in confidences if c >= 0.8]),
                    "medium": len([c for c in confidences if 0.5 <= c < 0.8]),
                    "low": len([c for c in confidences if c < 0.5])
                }
            }
            
            logger.info(f"Calculated performance metrics for model: {model_type.value}")
            return performance_metrics
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get model performance: {str(e)}")
            raise
    
    async def create_optimization_experiment(
        self,
        user_id: str,
        experiment_name: str,
        experiment_type: str,
        parameters: Dict[str, Any],
        control_group_ids: List[str],
        treatment_group_ids: List[str]
    ) -> OptimizationExperiment:
        """
        Create new optimization experiment
        
        Args:
            user_id: User UUID
            experiment_name: Name of the experiment
            experiment_type: Type of optimization experiment
            parameters: Experiment parameters
            control_group_ids: Content IDs for control group
            treatment_group_ids: Content IDs for treatment group
            
        Returns:
            Created OptimizationExperiment instance
        """
        try:
            experiment_data = {
                "user_id": user_id,
                "experiment_name": experiment_name,
                "experiment_type": experiment_type,
                "experiment_parameters": parameters,
                "control_group_ids": control_group_ids,
                "treatment_group_ids": treatment_group_ids,
                "experiment_status": ExperimentStatus.ACTIVE,
                "start_date": datetime.now(timezone.utc),
                "expected_end_date": datetime.now(timezone.utc) + timedelta(days=parameters.get('duration_days', 30))
            }
            
            experiment = OptimizationExperiment(**experiment_data)
            
            self.db_session.add(experiment)
            await self.db_session.commit()
            await self.db_session.refresh(experiment)
            
            logger.info(f"Created optimization experiment: {experiment.id} - {experiment_name}")
            return experiment
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create optimization experiment: {str(e)}")
            raise
    
    async def complete_experiment(
        self,
        experiment_id: str,
        results: Dict[str, Any],
        statistical_significance: float
    ) -> OptimizationExperiment:
        """
        Complete optimization experiment with results
        
        Args:
            experiment_id: OptimizationExperiment UUID
            results: Experiment results
            statistical_significance: Statistical significance of results
            
        Returns:
            Updated OptimizationExperiment instance
        """
        try:
            experiment = self.db_session.query(OptimizationExperiment).filter(
                OptimizationExperiment.id == experiment_id
            ).first()
            
            if not experiment:
                raise ValueError(f"Optimization experiment not found: {experiment_id}")
            
            experiment.experiment_status = ExperimentStatus.COMPLETED
            experiment.end_date = datetime.now(timezone.utc)
            experiment.experiment_results = results
            experiment.statistical_significance = statistical_significance
            
            # Determine if experiment was successful
            experiment.experiment_successful = statistical_significance >= 0.05 and \
                                             results.get('treatment_performance', 0) > results.get('control_performance', 0)
            
            await self.db_session.commit()
            
            logger.info(f"Completed optimization experiment: {experiment_id} - Success: {experiment.experiment_successful}")
            return experiment
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to complete experiment: {str(e)}")
            raise
    
    async def create_prediction_validation(
        self,
        analytics_id: str,
        validation_date: datetime,
        validation_metrics: Dict[str, Any]
    ) -> PredictionValidation:
        """
        Create prediction validation record
        
        Args:
            analytics_id: AIRevenueAnalytics UUID
            validation_date: Date of validation
            validation_metrics: Validation metrics
            
        Returns:
            Created PredictionValidation instance
        """
        try:
            validation_data = {
                "ai_revenue_analytics_id": analytics_id,
                "validation_date": validation_date,
                "validation_metrics": validation_metrics,
                "validation_status": ValidationStatus.COMPLETED,
                "accuracy_score": validation_metrics.get('accuracy_score', 0.0),
                "bias_detected": validation_metrics.get('bias_detected', False)
            }
            
            # Set validation score based on accuracy
            accuracy = validation_metrics.get('accuracy_score', 0.0)
            if accuracy >= 0.9:
                validation_data['validation_score'] = "excellent"
            elif accuracy >= 0.7:
                validation_data['validation_score'] = "good"
            elif accuracy >= 0.5:
                validation_data['validation_score'] = "fair"
            else:
                validation_data['validation_score'] = "poor"
            
            validation = PredictionValidation(**validation_data)
            
            self.db_session.add(validation)
            await self.db_session.commit()
            await self.db_session.refresh(validation)
            
            logger.info(f"Created prediction validation: {validation.id} with score: {validation.validation_score}")
            return validation
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create prediction validation: {str(e)}")
            raise
    
    async def get_user_revenue_insights(
        self,
        user_id: str,
        timeframe_days: int = 90
    ) -> Dict[str, Any]:
        """
        Get comprehensive revenue insights for a user
        
        Args:
            user_id: User UUID
            timeframe_days: Analysis timeframe in days
            
        Returns:
            Dictionary containing revenue insights
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=timeframe_days)
            
            # Get all analytics records for user
            analytics_records = self.db_session.query(self.model).filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.created_at >= cutoff_date
                )
            ).order_by(desc(self.model.created_at)).all()
            
            if not analytics_records:
                return {
                    "user_id": user_id,
                    "total_predictions": 0,
                    "insights": "Insufficient data for analysis"
                }
            
            # Separate validated and unvalidated predictions
            validated_records = [r for r in analytics_records if r.prediction_validated]
            unvalidated_records = [r for r in analytics_records if not r.prediction_validated]
            
            # Revenue predictions summary
            total_predicted_revenue = sum(float(r.predicted_revenue) for r in analytics_records)
            total_actual_revenue = sum(float(r.actual_revenue or 0) for r in validated_records)
            
            # Model performance by type
            model_performance = {}
            for model_type in ModelType:
                model_records = [r for r in validated_records if r.model_type == model_type]
                if model_records:
                    accuracies = [r.prediction_accuracy for r in model_records if r.prediction_accuracy is not None]
                    avg_accuracy = np.mean(accuracies) if accuracies else 0.0
                    model_performance[model_type.value] = {
                        "total_predictions": len(model_records),
                        "average_accuracy": round(avg_accuracy, 4),
                        "usage_percentage": round(len(model_records) / len(validated_records) * 100, 2)
                    }
            
            # Timeframe analysis
            timeframe_performance = {}
            for timeframe in PredictionTimeframe:
                timeframe_records = [r for r in validated_records if r.prediction_timeframe == timeframe]
                if timeframe_records:
                    accuracies = [r.prediction_accuracy for r in timeframe_records if r.prediction_accuracy is not None]
                    avg_accuracy = np.mean(accuracies) if accuracies else 0.0
                    timeframe_performance[timeframe.value] = {
                        "total_predictions": len(timeframe_records),
                        "average_accuracy": round(avg_accuracy, 4)
                    }
            
            # Optimization opportunities
            optimization_opportunities = []
            
            # Low accuracy models
            for model_type, performance in model_performance.items():
                if performance['average_accuracy'] < 0.7:
                    optimization_opportunities.append({
                        "type": "model_improvement",
                        "target": model_type,
                        "current_accuracy": performance['average_accuracy'],
                        "recommendation": f"Consider retraining {model_type} model with additional features"
                    })
            
            # Underutilized timeframes
            for timeframe, performance in timeframe_performance.items():
                if performance['total_predictions'] < 5:
                    optimization_opportunities.append({
                        "type": "timeframe_expansion",
                        "target": timeframe,
                        "recommendation": f"Expand {timeframe} predictions to improve revenue planning"
                    })
            
            insights = {
                "user_id": user_id,
                "analysis_period_days": timeframe_days,
                "summary": {
                    "total_predictions": len(analytics_records),
                    "validated_predictions": len(validated_records),
                    "pending_validation": len(unvalidated_records),
                    "total_predicted_revenue": round(total_predicted_revenue, 2),
                    "total_actual_revenue": round(total_actual_revenue, 2),
                    "overall_prediction_accuracy": round(np.mean([r.prediction_accuracy for r in validated_records 
                                                                if r.prediction_accuracy is not None]), 4) if validated_records else 0.0
                },
                "model_performance": model_performance,
                "timeframe_performance": timeframe_performance,
                "revenue_trends": {
                    "prediction_vs_actual_variance": round(abs(total_predicted_revenue - total_actual_revenue), 2),
                    "average_revenue_per_prediction": round(total_actual_revenue / len(validated_records), 2) if validated_records else 0,
                    "revenue_growth_indicator": "positive" if total_actual_revenue > total_predicted_revenue * 0.9 else "needs_attention"
                },
                "optimization_opportunities": optimization_opportunities,
                "recommendations": {
                    "primary": "Focus on improving prediction accuracy for most used models",
                    "secondary": "Expand prediction timeframes for better revenue planning",
                    "advanced": "Consider implementing ensemble models for better performance"
                }
            }
            
            logger.info(f"Generated revenue insights for user: {user_id}")
            return insights
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get user revenue insights: {str(e)}")
            raise
    
    async def get_trending_optimizations(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get trending optimization strategies based on successful experiments
        
        Args:
            limit: Maximum number of trends to return
            
        Returns:
            List of trending optimization strategies
        """
        try:
            # Get successful experiments from last 60 days
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)
            
            successful_experiments = self.db_session.query(OptimizationExperiment).filter(
                and_(
                    OptimizationExperiment.experiment_successful == True,
                    OptimizationExperiment.end_date >= cutoff_date,
                    OptimizationExperiment.statistical_significance >= 0.05
                )
            ).order_by(desc(OptimizationExperiment.statistical_significance)).limit(limit * 2).all()
            
            # Analyze experiment types and success patterns
            experiment_analysis = {}
            for experiment in successful_experiments:
                exp_type = experiment.experiment_type
                if exp_type not in experiment_analysis:
                    experiment_analysis[exp_type] = {
                        "count": 0,
                        "avg_significance": 0.0,
                        "avg_improvement": 0.0,
                        "success_rate": 0.0,
                        "parameters": []
                    }
                
                experiment_analysis[exp_type]["count"] += 1
                experiment_analysis[exp_type]["avg_significance"] += experiment.statistical_significance
                
                # Extract improvement from results
                if experiment.experiment_results:
                    improvement = experiment.experiment_results.get('improvement_percentage', 0)
                    experiment_analysis[exp_type]["avg_improvement"] += improvement
                
                # Collect parameter patterns
                if experiment.experiment_parameters:
                    experiment_analysis[exp_type]["parameters"].append(experiment.experiment_parameters)
            
            # Calculate averages and create trending list
            trending_optimizations = []
            for exp_type, analysis in experiment_analysis.items():
                if analysis["count"] >= 2:  # Minimum threshold for trending
                    avg_significance = analysis["avg_significance"] / analysis["count"]
                    avg_improvement = analysis["avg_improvement"] / analysis["count"]
                    
                    # Identify common parameters
                    common_params = {}
                    if analysis["parameters"]:
                        for param_set in analysis["parameters"]:
                            for key, value in param_set.items():
                                if key not in common_params:
                                    common_params[key] = []
                                common_params[key].append(value)
                    
                    trending_optimizations.append({
                        "optimization_type": exp_type,
                        "success_count": analysis["count"],
                        "average_statistical_significance": round(avg_significance, 4),
                        "average_improvement_percentage": round(avg_improvement, 2),
                        "trending_score": round((avg_significance * avg_improvement) / 100, 4),
                        "common_parameters": {k: max(set(v), key=v.count) for k, v in common_params.items() if len(v) > 1},
                        "recommendation": f"Implement {exp_type} optimization with proven {avg_improvement:.1f}% average improvement"
                    })
            
            # Sort by trending score
            trending_optimizations.sort(key=lambda x: x["trending_score"], reverse=True)
            
            logger.info(f"Generated {len(trending_optimizations)} trending optimization strategies")
            return trending_optimizations[:limit]
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get trending optimizations: {str(e)}")
            raise
