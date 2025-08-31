"""IA-Influencer Agent - Decision Engine

Advanced AI-powered decision making engine for intelligent content optimization,
workflow routing, and system orchestration decisions.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: 2025 - All rights reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Expert Team Specializations:
- Lead AI Developer: Fahed Mlaiel  
- Decision Science Expert
- Machine Learning Engineer
- Neural Network Architect
- Optimization Specialist
"""import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import statistics
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib

try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...utils.ml_utils import MLModelManager


class DecisionCategory(Enum):
    """Categories of decisions the engine can make."""    CONTENT_STRATEGY = "content_strategy"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    AUDIENCE_TARGETING = "audience_targeting"
    COLLABORATION_MATCHING = "collaboration_matching"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    SECURITY_RESPONSE = "security_response"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    PERFORMANCE_TUNING = "performance_tuning"


class DecisionPriority(Enum):
    """Priority levels for decisions."""    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class DecisionContext:
    """Context information for decision making."""    user_id: str
    content_type: str
    platform: str
    timestamp: datetime
    user_preferences: Dict[str, Any]
    content_metadata: Dict[str, Any]
    performance_history: List[Dict[str, Any]]
    market_conditions: Dict[str, Any]
    competition_analysis: Dict[str, Any]
    budget_constraints: Optional[Dict[str, float]] = None
    compliance_requirements: List[str] = field(default_factory=list)


@dataclass
class DecisionOption:
    """A single decision option with evaluation metrics."""    option_id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    expected_outcome: Dict[str, float]
    confidence_score: float
    risk_assessment: Dict[str, float]
    resource_requirements: Dict[str, float]
    implementation_complexity: float
    estimated_impact: Dict[str, float]


@dataclass
class DecisionResult:
    """Result of a decision making process."""    decision_id: str
    category: DecisionCategory
    priority: DecisionPriority
    context: DecisionContext
    options_evaluated: List[DecisionOption]
    selected_option: DecisionOption
    confidence_score: float
    reasoning: str
    expected_roi: float
    implementation_timeline: Dict[str, datetime]
    success_metrics: Dict[str, float]
    fallback_options: List[DecisionOption]
    created_at: datetime = field(default_factory=datetime.now)


class DecisionEngine:
    """    Advanced AI-powered decision making engine for content creators.
    
    Provides intelligent decision-making capabilities including:
    - Multi-criteria decision analysis
    - Machine learning-based option evaluation
    - Risk assessment and mitigation
    - Performance prediction and optimization
    - Real-time adaptation and learning
    """    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Decision Engine with ML models and configuration."""        self.config = config or {}
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # ML Model management
        self.ml_manager = MLModelManager()
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Decision configuration
        self.confidence_threshold = self.config.get('confidence_threshold', 0.75)
        self.max_options_to_evaluate = self.config.get('max_options_to_evaluate', 10)
        self.learning_rate = self.config.get('learning_rate', 0.01)
        
        # Decision history and analytics
        self.decision_history: Dict[str, DecisionResult] = {}
        self.performance_metrics: Dict[str, List[float]] = {}
        self.model_accuracy: Dict[str, float] = {}
        
        # Feature engineering configuration
        self.feature_extractors = {
            'content_features': self._extract_content_features,
            'user_features': self._extract_user_features,
            'platform_features': self._extract_platform_features,
            'temporal_features': self._extract_temporal_features,
            'market_features': self._extract_market_features
        }
        
        # Initialize ML models
        self._initialize_decision_models()
        
        self.logger.info("Decision Engine initialized with advanced ML capabilities")
    
    def _initialize_decision_models(self):
        """Initialize and load pre-trained ML models for each decision category."""        model_configs = {
            DecisionCategory.CONTENT_STRATEGY: {
                'model_type': 'random_forest',
                'params': {'n_estimators': 100, 'max_depth': 10},
                'features': ['engagement_rate', 'reach_score', 'quality_score', 'timing_score']
            },
            DecisionCategory.PLATFORM_OPTIMIZATION: {
                'model_type': 'gradient_boosting',
                'params': {'n_estimators': 150, 'learning_rate': 0.1},
                'features': ['platform_engagement', 'audience_match', 'competition_level']
            },
            DecisionCategory.AUDIENCE_TARGETING: {
                'model_type': 'logistic_regression',
                'params': {'C': 1.0, 'max_iter': 1000},
                'features': ['demographic_match', 'interest_alignment', 'behavior_similarity']
            },
            DecisionCategory.COLLABORATION_MATCHING: {
                'model_type': 'random_forest',
                'params': {'n_estimators': 80, 'max_depth': 8},
                'features': ['style_compatibility', 'audience_overlap', 'mutual_benefit']
            },
            DecisionCategory.REVENUE_OPTIMIZATION: {
                'model_type': 'gradient_boosting',
                'params': {'n_estimators': 200, 'learning_rate': 0.05},
                'features': ['monetization_potential', 'cost_efficiency', 'market_demand']
            }
        }
        
        for category, config in model_configs.items():
            try:
                model = self._create_ml_model(config['model_type'], config['params'])
                self.models[category.value] = model
                self.scalers[category.value] = StandardScaler()
                
                # Load pre-trained weights if available
                self._load_pretrained_model(category.value)
                
            except Exception as e:
                self.logger.error(f"Failed to initialize model for {category.value}: {str(e)}")
    
    def _create_ml_model(self, model_type: str, params: Dict[str, Any]):
        """Create ML model based on type and parameters."""        if model_type == 'random_forest':
            return RandomForestClassifier(**params)
        elif model_type == 'gradient_boosting':
            return GradientBoostingRegressor(**params)
        elif model_type == 'logistic_regression':
            return LogisticRegression(**params)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    async def make_decision(
        self,
        category: DecisionCategory,
        context: DecisionContext,
        options: List[DecisionOption],
        priority: DecisionPriority = DecisionPriority.MEDIUM
    ) -> DecisionResult:
        """        Make an intelligent decision using ML models and advanced analytics.
        
        Args:
            category: Category of decision to make
            context: Decision context and environment
            options: Available options to evaluate
            priority: Decision priority level
            
        Returns:
            DecisionResult: Comprehensive decision result with reasoning
        """        try:
            decision_id = f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{category.value}"
            
            self.logger.info(f"Making decision {decision_id} with {len(options)} options")
            
            # Limit options if too many
            if len(options) > self.max_options_to_evaluate:
                options = self._prioritize_options(options, context)[:self.max_options_to_evaluate]
            
            # Extract features for ML prediction
            context_features = await self._extract_decision_features(context)
            
            # Evaluate each option using ML models
            evaluated_options = []
            for option in options:
                evaluation = await self._evaluate_option(category, context_features, option)
                evaluated_options.append(evaluation)
            
            # Select the best option
            best_option = max(evaluated_options, key=lambda x: x.confidence_score)
            
            # Calculate overall confidence
            confidence_score = await self._calculate_decision_confidence(
                category, context_features, best_option
            )
            
            # Generate reasoning and explanation
            reasoning = await self._generate_decision_reasoning(
                category, context, best_option, evaluated_options
            )
            
            # Calculate expected ROI
            expected_roi = await self._calculate_expected_roi(context, best_option)
            
            # Create implementation timeline
            timeline = await self._create_implementation_timeline(best_option)
            
            # Define success metrics
            success_metrics = await self._define_success_metrics(category, context, best_option)
            
            # Select fallback options
            fallback_options = sorted(
                [opt for opt in evaluated_options if opt != best_option],
                key=lambda x: x.confidence_score,
                reverse=True
            )[:3]
            
            # Create decision result
            decision_result = DecisionResult(
                decision_id=decision_id,
                category=category,
                priority=priority,
                context=context,
                options_evaluated=evaluated_options,
                selected_option=best_option,
                confidence_score=confidence_score,
                reasoning=reasoning,
                expected_roi=expected_roi,
                implementation_timeline=timeline,
                success_metrics=success_metrics,
                fallback_options=fallback_options
            )
            
            # Store decision for learning
            self.decision_history[decision_id] = decision_result
            
            # Update performance metrics
            await self._update_performance_metrics(category, decision_result)
            
            self.logger.info(f"Decision completed: {decision_id} (confidence: {confidence_score:.3f})")
            
            return decision_result
            
        except Exception as e:
            self.logger.error(f"Failed to make decision: {str(e)}")
            raise
    
    async def _extract_decision_features(self, context: DecisionContext) -> np.ndarray:
        """Extract ML features from decision context."""        features = []
        
        # Extract features using all extractors
        for extractor_name, extractor_func in self.feature_extractors.items():
            try:
                extracted_features = extractor_func(context)
                features.extend(extracted_features)
            except Exception as e:
                self.logger.warning(f"Feature extraction failed for {extractor_name}: {str(e)}")
                features.extend([0.0] * 5)  # Default fallback features
        
        return np.array(features).reshape(1, -1)
    
    def _extract_content_features(self, context: DecisionContext) -> List[float]:
        """Extract content-related features."""        metadata = context.content_metadata
        
        return [
            metadata.get('quality_score', 0.0),
            metadata.get('originality_score', 0.0),
            metadata.get('engagement_potential', 0.0),
            metadata.get('viral_potential', 0.0),
            metadata.get('monetization_score', 0.0)
        ]
    
    def _extract_user_features(self, context: DecisionContext) -> List[float]:
        """Extract user-related features."""        preferences = context.user_preferences
        history = context.performance_history
        
        avg_engagement = statistics.mean(
            [h.get('engagement_rate', 0.0) for h in history]
        ) if history else 0.0
        
        return [
            preferences.get('risk_tolerance', 0.5),
            preferences.get('growth_focus', 0.5),
            preferences.get('revenue_priority', 0.5),
            avg_engagement,
            len(history) / 100.0  # Normalize experience level
        ]
    
    def _extract_platform_features(self, context: DecisionContext) -> List[float]:
        """Extract platform-related features."""        platform = context.platform
        
        # Platform-specific scoring (simplified)
        platform_scores = {
            'spotify': [0.8, 0.7, 0.9, 0.6, 0.8],
            'youtube': [0.9, 0.8, 0.7, 0.9, 0.7],
            'instagram': [0.7, 0.9, 0.8, 0.8, 0.6],
            'tiktok': [0.6, 0.9, 0.6, 0.9, 0.5],
            'twitter': [0.5, 0.6, 0.7, 0.7, 0.4]
        }
        
        return platform_scores.get(platform.lower(), [0.5, 0.5, 0.5, 0.5, 0.5])
    
    def _extract_temporal_features(self, context: DecisionContext) -> List[float]:
        """Extract time-related features."""        now = context.timestamp
        
        return [
            now.hour / 24.0,  # Hour of day normalized
            now.weekday() / 7.0,  # Day of week normalized
            now.month / 12.0,  # Month normalized
            (now - datetime(now.year, 1, 1)).days / 365.0,  # Day of year normalized
            1.0 if now.weekday() < 5 else 0.0  # Weekday vs weekend
        ]
    
    def _extract_market_features(self, context: DecisionContext) -> List[float]:
        """Extract market-related features."""        market = context.market_conditions
        competition = context.competition_analysis
        
        return [
            market.get('trend_strength', 0.0),
            market.get('saturation_level', 0.0),
            market.get('growth_rate', 0.0),
            competition.get('competitive_intensity', 0.0),
            competition.get('differentiation_opportunity', 0.0)
        ]
    
    async def _evaluate_option(
        self,
        category: DecisionCategory,
        context_features: np.ndarray,
        option: DecisionOption
    ) -> DecisionOption:
        """Evaluate a single option using ML models."""        try:
            # Get model for this category
            model = self.models.get(category.value)
            scaler = self.scalers.get(category.value)
            
            if not model or not scaler:
                # Fallback to rule-based evaluation
                return await self._rule_based_evaluation(option)
            
            # Prepare features for prediction
            option_features = self._extract_option_features(option)
            combined_features = np.concatenate([context_features.flatten(), option_features])
            
            # Scale features
            try:
                scaled_features = scaler.transform(combined_features.reshape(1, -1))
            except:
                # If scaler not fitted, use original features
                scaled_features = combined_features.reshape(1, -1)
            
            # Make prediction
            if hasattr(model, 'predict_proba'):
                # Classification model
                probabilities = model.predict_proba(scaled_features)[0]
                confidence = max(probabilities)
            else:
                # Regression model
                prediction = model.predict(scaled_features)[0]
                confidence = min(1.0, max(0.0, prediction))
            
            # Update option with ML prediction
            option.confidence_score = confidence
            option.expected_outcome['ml_prediction'] = float(confidence)
            
            return option
            
        except Exception as e:
            self.logger.error(f"ML evaluation failed for option {option.option_id}: {str(e)}")
            return await self._rule_based_evaluation(option)
    
    def _extract_option_features(self, option: DecisionOption) -> np.ndarray:
        """Extract features from a decision option."""        return np.array([
            option.expected_outcome.get('success_probability', 0.0),
            option.risk_assessment.get('overall_risk', 0.0),
            option.resource_requirements.get('total_cost', 0.0) / 10000.0,  # Normalized
            option.implementation_complexity,
            option.estimated_impact.get('expected_value', 0.0)
        ])
    
    async def _rule_based_evaluation(self, option: DecisionOption) -> DecisionOption:
        """Fallback rule-based evaluation when ML models are unavailable."""        # Simple scoring based on weighted criteria
        success_prob = option.expected_outcome.get('success_probability', 0.5)
        risk_level = 1.0 - option.risk_assessment.get('overall_risk', 0.5)
        cost_efficiency = 1.0 - min(1.0, option.resource_requirements.get('total_cost', 0.0) / 10000.0)
        simplicity = 1.0 - option.implementation_complexity
        impact = option.estimated_impact.get('expected_value', 0.0)
        
        # Weighted score
        confidence = (
            success_prob * 0.3 +
            risk_level * 0.2 +
            cost_efficiency * 0.2 +
            simplicity * 0.1 +
            impact * 0.2
        )
        
        option.confidence_score = min(1.0, max(0.0, confidence))
        return option
    
    async def _calculate_decision_confidence(
        self,
        category: DecisionCategory,
        context_features: np.ndarray,
        selected_option: DecisionOption
    ) -> float:
        """Calculate overall confidence in the decision."""        base_confidence = selected_option.confidence_score
        
        # Adjust based on model accuracy
        model_accuracy = self.model_accuracy.get(category.value, 0.8)
        
        # Adjust based on data quality
        data_quality = self._assess_data_quality(context_features)
        
        # Adjust based on option diversity
        option_confidence = min(1.0, selected_option.confidence_score + 0.1)
        
        overall_confidence = base_confidence * model_accuracy * data_quality * option_confidence
        
        return min(1.0, max(0.0, overall_confidence))
    
    def _assess_data_quality(self, features: np.ndarray) -> float:
        """Assess the quality of input data for decision making."""        # Check for missing or invalid values
        valid_ratio = np.sum(np.isfinite(features)) / len(features.flatten())
        
        # Check for feature variance (avoid all zeros or same values)
        variance_score = min(1.0, np.var(features) * 10)
        
        # Combine metrics
        quality_score = (valid_ratio * 0.7) + (variance_score * 0.3)
        
        return min(1.0, max(0.1, quality_score))
    
    async def _generate_decision_reasoning(
        self,
        category: DecisionCategory,
        context: DecisionContext,
        selected_option: DecisionOption,
        all_options: List[DecisionOption]
    ) -> str:
        """Generate human-readable reasoning for the decision."""        reasoning_parts = []
        
        # Category-specific reasoning
        reasoning_parts.append(f"Decision category: {category.value.replace('_', ' ').title()}")
        
        # Selection justification
        reasoning_parts.append(
            f"Selected '{selected_option.name}' with {selected_option.confidence_score:.1%} confidence"
        )
        
        # Key factors
        key_factors = []
        if selected_option.expected_outcome.get('success_probability', 0) > 0.7:
            key_factors.append("high success probability")
        if selected_option.risk_assessment.get('overall_risk', 1.0) < 0.3:
            key_factors.append("low risk profile")
        if selected_option.estimated_impact.get('expected_value', 0) > 0.6:
            key_factors.append("strong expected impact")
        
        if key_factors:
            reasoning_parts.append(f"Key factors: {', '.join(key_factors)}")
        
        # Comparison with alternatives
        if len(all_options) > 1:
            other_scores = [opt.confidence_score for opt in all_options if opt != selected_option]
            if other_scores:
                max_other = max(other_scores)
                advantage = selected_option.confidence_score - max_other
                if advantage > 0.1:
                    reasoning_parts.append(f"Clear advantage over alternatives (+{advantage:.1%})")
        
        # Context considerations
        if context.platform:
            reasoning_parts.append(f"Optimized for {context.platform} platform characteristics")
        
        return ". ".join(reasoning_parts) + "."
    
    async def _calculate_expected_roi(
        self,
        context: DecisionContext,
        option: DecisionOption
    ) -> float:
        """Calculate expected return on investment for the selected option."""        # Extract relevant metrics
        expected_value = option.estimated_impact.get('expected_value', 0.0)
        total_cost = option.resource_requirements.get('total_cost', 1.0)
        success_probability = option.expected_outcome.get('success_probability', 0.5)
        
        # Calculate ROI with risk adjustment
        if total_cost > 0:
            roi = (expected_value * success_probability - total_cost) / total_cost
        else:
            roi = expected_value * success_probability
        
        return round(roi, 3)
    
    async def _create_implementation_timeline(
        self,
        option: DecisionOption
    ) -> Dict[str, datetime]:
        """Create implementation timeline for the selected option."""        now = datetime.now()
        complexity = option.implementation_complexity
        
        # Estimate phases based on complexity
        planning_days = max(1, int(complexity * 7))
        development_days = max(1, int(complexity * 14))
        testing_days = max(1, int(complexity * 5))
        deployment_days = max(1, int(complexity * 3))
        
        timeline = {
            'planning_start': now,
            'planning_end': now + timedelta(days=planning_days),
            'development_start': now + timedelta(days=planning_days),
            'development_end': now + timedelta(days=planning_days + development_days),
            'testing_start': now + timedelta(days=planning_days + development_days),
            'testing_end': now + timedelta(days=planning_days + development_days + testing_days),
            'deployment_start': now + timedelta(days=planning_days + development_days + testing_days),
            'deployment_end': now + timedelta(days=planning_days + development_days + testing_days + deployment_days),
            'full_completion': now + timedelta(days=planning_days + development_days + testing_days + deployment_days + 7)
        }
        
        return timeline
    
    async def _define_success_metrics(
        self,
        category: DecisionCategory,
        context: DecisionContext,
        option: DecisionOption
    ) -> Dict[str, float]:
        """Define success metrics for measuring decision outcome."""        base_metrics = {
            'roi_threshold': 1.5,
            'timeline_adherence': 0.9,
            'quality_score': 0.8,
            'user_satisfaction': 0.85
        }
        
        # Category-specific metrics
        category_metrics = {
            DecisionCategory.CONTENT_STRATEGY: {
                'engagement_increase': 0.2,
                'reach_expansion': 0.15,
                'conversion_rate': 0.1
            },
            DecisionCategory.REVENUE_OPTIMIZATION: {
                'revenue_increase': 0.25,
                'cost_reduction': 0.1,
                'profit_margin': 0.15
            },
            DecisionCategory.AUDIENCE_TARGETING: {
                'audience_growth': 0.3,
                'engagement_quality': 0.2,
                'retention_rate': 0.85
            }
        }
        
        metrics = base_metrics.copy()
        metrics.update(category_metrics.get(category, {}))
        
        return metrics
    
    def _prioritize_options(
        self,
        options: List[DecisionOption],
        context: DecisionContext
    ) -> List[DecisionOption]:
        """Prioritize options when there are too many to evaluate."""        # Simple scoring for prioritization
        scored_options = []
        
        for option in options:
            score = (
                option.expected_outcome.get('success_probability', 0.0) * 0.4 +
                (1.0 - option.risk_assessment.get('overall_risk', 1.0)) * 0.3 +
                option.estimated_impact.get('expected_value', 0.0) * 0.3
            )
            scored_options.append((score, option))
        
        # Sort by score descending
        scored_options.sort(key=lambda x: x[0], reverse=True)
        
        return [option for score, option in scored_options]
    
    async def _update_performance_metrics(
        self,
        category: DecisionCategory,
        decision_result: DecisionResult
    ):
        """Update performance metrics for continuous learning."""        category_key = category.value
        
        if category_key not in self.performance_metrics:
            self.performance_metrics[category_key] = []
        
        # Store decision quality metrics
        self.performance_metrics[category_key].append(decision_result.confidence_score)
        
        # Maintain rolling window
        if len(self.performance_metrics[category_key]) > 1000:
            self.performance_metrics[category_key] = self.performance_metrics[category_key][-1000:]
    
    def _load_pretrained_model(self, category: str):
        """Load pre-trained model weights if available."""        try:
            model_path = f"models/decision_engine_{category}.joblib"
            scaler_path = f"models/decision_scaler_{category}.joblib"
            
            if self.ml_manager.model_exists(model_path):
                self.models[category] = joblib.load(model_path)
                self.logger.info(f"Loaded pre-trained model for {category}")
            
            if self.ml_manager.model_exists(scaler_path):
                self.scalers[category] = joblib.load(scaler_path)
                
        except Exception as e:
            self.logger.warning(f"Could not load pre-trained model for {category}: {str(e)}")
    
    async def get_decision_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics about decision engine performance."""        total_decisions = len(self.decision_history)
        
        if total_decisions == 0:
            return {
                'total_decisions': 0,
                'average_confidence': 0.0,
                'category_distribution': {},
                'success_rate': 0.0,
                'model_performance': {}
            }
        
        # Calculate metrics
        all_confidences = [d.confidence_score for d in self.decision_history.values()]
        avg_confidence = statistics.mean(all_confidences)
        
        # Category distribution
        category_counts = {}
        for decision in self.decision_history.values():
            category = decision.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Model performance
        model_performance = {}
        for category, metrics in self.performance_metrics.items():
            if metrics:
                model_performance[category] = {
                    'average_confidence': statistics.mean(metrics),
                    'decision_count': len(metrics),
                    'confidence_trend': 'improving' if len(metrics) > 1 and metrics[-1] > metrics[0] else 'stable'
                }
        
        return {
            'total_decisions': total_decisions,
            'average_confidence': round(avg_confidence, 3),
            'category_distribution': category_counts,
            'confidence_distribution': {
                'high': sum(1 for c in all_confidences if c > 0.8),
                'medium': sum(1 for c in all_confidences if 0.6 <= c <= 0.8),
                'low': sum(1 for c in all_confidences if c < 0.6)
            },
            'model_performance': model_performance,
            'active_models': len(self.models),
            'learning_enabled': True
        }
