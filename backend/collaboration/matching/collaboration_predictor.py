"""Collaboration Predictor - AI-Powered Success Prediction Engine
===============================================================

Advanced machine learning system for predicting collaboration success:
- Historical collaboration analysis
- Success pattern recognition
- ROI prediction modeling
- Risk assessment algorithms
- Timeline success prediction
- Quality outcome forecasting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class CollaborationOutcome(Enum):
    """Possible collaboration outcomes"""
    HIGHLY_SUCCESSFUL = "highly_successful"
    SUCCESSFUL = "successful"
    MODERATELY_SUCCESSFUL = "moderately_successful"
    MIXED_RESULTS = "mixed_results"
    UNSUCCESSFUL = "unsuccessful"
    FAILED = "failed"


class PredictionConfidence(Enum):
    """Confidence levels for predictions"""
    VERY_HIGH = "very_high"  # 90%+
    HIGH = "high"           # 80-90%
    MEDIUM = "medium"       # 60-80%
    LOW = "low"            # 40-60%
    VERY_LOW = "very_low"  # <40%


@dataclass
class PredictiveFeatures:
    """Features used for collaboration success prediction"""
    creator_a_id: str
    creator_b_id: str
    
    # Creator compatibility features
    skill_complementarity: float = 0.0
    audience_overlap: float = 0.0
    style_similarity: float = 0.0
    experience_gap: float = 0.0
    reputation_match: float = 0.0
    
    # Project features
    project_complexity: float = 0.0
    timeline_feasibility: float = 0.0
    budget_adequacy: float = 0.0
    resource_availability: float = 0.0
    market_demand: float = 0.0
    
    # Historical features
    individual_success_rates: Tuple[float, float] = (0.0, 0.0)
    collaboration_experience: Tuple[int, int] = (0, 0)
    similar_project_history: Tuple[int, int] = (0, 0)
    past_collaborations_together: int = 0
    
    # Communication features
    communication_style_match: float = 0.0
    timezone_compatibility: float = 0.0
    language_compatibility: float = 0.0
    response_time_compatibility: float = 0.0
    
    # External factors
    market_conditions: float = 0.0
    seasonal_factors: float = 0.0
    competitive_landscape: float = 0.0
    platform_support: float = 0.0
    
    def to_vector(self) -> np.ndarray:
        """Convert features to numpy vector for ML processing"""
        return np.array([
            self.skill_complementarity,
            self.audience_overlap,
            self.style_similarity,
            self.experience_gap,
            self.reputation_match,
            self.project_complexity,
            self.timeline_feasibility,
            self.budget_adequacy,
            self.resource_availability,
            self.market_demand,
            self.individual_success_rates[0],
            self.individual_success_rates[1],
            float(self.collaboration_experience[0]),
            float(self.collaboration_experience[1]),
            float(self.similar_project_history[0]),
            float(self.similar_project_history[1]),
            float(self.past_collaborations_together),
            self.communication_style_match,
            self.timezone_compatibility,
            self.language_compatibility,
            self.response_time_compatibility,
            self.market_conditions,
            self.seasonal_factors,
            self.competitive_landscape,
            self.platform_support
        ], dtype=np.float32)


@dataclass
class SuccessPrediction:
    """Collaboration success prediction result"""
    creator_a_id: str
    creator_b_id: str
    project_id: Optional[str] = None
    
    # Main prediction
    success_probability: float = 0.0
    predicted_outcome: CollaborationOutcome = CollaborationOutcome.MIXED_RESULTS
    confidence: PredictionConfidence = PredictionConfidence.MEDIUM
    
    # Detailed predictions
    quality_score_prediction: float = 0.0
    timeline_adherence_probability: float = 0.0
    budget_adherence_probability: float = 0.0
    satisfaction_score_prediction: float = 0.0
    roi_prediction: float = 0.0
    
    # Risk factors
    identified_risks: List[str] = field(default_factory=list)
    risk_mitigation_suggestions: List[str] = field(default_factory=list)
    critical_success_factors: List[str] = field(default_factory=list)
    
    # Feature importance
    feature_importance: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    
    # Time-based predictions
    predicted_duration_days: int = 0
    milestone_success_probabilities: List[float] = field(default_factory=list)
    
    def get_recommendation(self) -> str:
        """Get human-readable recommendation"""
        if self.success_probability >= 0.8:
            return "highly_recommended"
        elif self.success_probability >= 0.6:
            return "recommended"
        elif self.success_probability >= 0.4:
            return "proceed_with_caution"
        else:
            return "not_recommended"


@dataclass
class PredictionModel:
    """Machine learning model for success prediction"""
    model_type: str
    model: Any
    training_accuracy: float = 0.0
    validation_accuracy: float = 0.0
    feature_names: List[str] = field(default_factory=list)
    last_trained: datetime = field(default_factory=datetime.now)
    prediction_count: int = 0
    
    def predict(self, features: np.ndarray) -> Tuple[float, float]:
        """Make prediction and return (probability, confidence)"""
        try:
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(features.reshape(1, -1))[0]
                return float(proba[1]), float(max(proba))
            else:
                prediction = self.model.predict(features.reshape(1, -1))[0]
                return float(prediction), 0.7  # Default confidence
        except Exception as e:
            logger.error(f"❌ Model prediction error: {e}")
            return 0.5, 0.1  # Fallback


class CollaborationPredictor:
    """
    AI-powered collaboration success prediction engine
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize collaboration predictor"""
        self.config = config or {}
        self.models: Dict[str, PredictionModel] = {}
        self.training_data: List[Dict[str, Any]] = []
        self.prediction_cache: Dict[str, SuccessPrediction] = {}
        
        # Configuration
        self.cache_size_limit = self.config.get('cache_size_limit', 1000)
        self.model_update_threshold = self.config.get('model_update_threshold', 100)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.6)
        
        # Feature weights for ensemble
        self.feature_weights = {
            'creator_compatibility': 0.25,
            'project_feasibility': 0.20,
            'historical_performance': 0.20,
            'communication_factors': 0.15,
            'external_factors': 0.10,
            'risk_factors': 0.10
        }
        
        logger.info("🔮 Collaboration Predictor initialized")
    
    async def initialize_models(self):
        """Initialize prediction models"""
        try:
            await self._initialize_success_classifier()
            await self._initialize_quality_regressor()
            await self._initialize_timeline_predictor()
            await self._initialize_roi_predictor()
            
            logger.info("✅ Prediction models initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing prediction models: {e}")
    
    async def _initialize_success_classifier(self):
        """Initialize binary success classifier"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
            
            self.models['success_classifier'] = PredictionModel(
                model_type='RandomForestClassifier',
                model=model,
                feature_names=self._get_feature_names()
            )
            
        except ImportError:
            logger.warning("⚠️ scikit-learn not available, using simple model")
            await self._initialize_simple_classifier()
    
    async def _initialize_quality_regressor(self):
        """Initialize quality score regression model"""
        try:
            from sklearn.ensemble import GradientBoostingRegressor
            
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.models['quality_regressor'] = PredictionModel(
                model_type='GradientBoostingRegressor',
                model=model,
                feature_names=self._get_feature_names()
            )
            
        except ImportError:
            await self._initialize_simple_regressor('quality_regressor')
    
    async def _initialize_timeline_predictor(self):
        """Initialize timeline adherence predictor"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            
            model = RandomForestRegressor(
                n_estimators=50,
                max_depth=8,
                random_state=42
            )
            
            self.models['timeline_predictor'] = PredictionModel(
                model_type='RandomForestRegressor',
                model=model,
                feature_names=self._get_feature_names()
            )
            
        except ImportError:
            await self._initialize_simple_regressor('timeline_predictor')
    
    async def _initialize_roi_predictor(self):
        """Initialize ROI prediction model"""
        try:
            from sklearn.linear_model import LinearRegression
            
            model = LinearRegression()
            
            self.models['roi_predictor'] = PredictionModel(
                model_type='LinearRegression',
                model=model,
                feature_names=self._get_feature_names()
            )
            
        except ImportError:
            await self._initialize_simple_regressor('roi_predictor')
    
    async def _initialize_simple_classifier(self):
        """Initialize simple fallback classifier"""
        class SimpleClassifier:
            def predict_proba(self, X):
                # Simple heuristic based on first few features
                scores = np.mean(X[:, :5], axis=1)  # Average of first 5 features
                return np.column_stack([1 - scores, scores])
            
            def fit(self, X, y):
                pass  # No training needed for simple heuristic
        
        self.models['success_classifier'] = PredictionModel(
            model_type='SimpleClassifier',
            model=SimpleClassifier(),
            feature_names=self._get_feature_names()
        )
    
    async def _initialize_simple_regressor(self, model_name: str):
        """Initialize simple fallback regressor"""
        class SimpleRegressor:
            def predict(self, X):
                # Simple average-based prediction
                return np.mean(X[:, :10], axis=1)  # Average of first 10 features
            
            def fit(self, X, y):
                pass
        
        self.models[model_name] = PredictionModel(
            model_type='SimpleRegressor',
            model=SimpleRegressor(),
            feature_names=self._get_feature_names()
        )
    
    def _get_feature_names(self) -> List[str]:
        """Get ordered list of feature names"""
        return [
            'skill_complementarity',
            'audience_overlap',
            'style_similarity',
            'experience_gap',
            'reputation_match',
            'project_complexity',
            'timeline_feasibility',
            'budget_adequacy',
            'resource_availability',
            'market_demand',
            'creator_a_success_rate',
            'creator_b_success_rate',
            'creator_a_collab_exp',
            'creator_b_collab_exp',
            'creator_a_similar_projects',
            'creator_b_similar_projects',
            'past_collaborations_together',
            'communication_style_match',
            'timezone_compatibility',
            'language_compatibility',
            'response_time_compatibility',
            'market_conditions',
            'seasonal_factors',
            'competitive_landscape',
            'platform_support'
        ]
    
    async def extract_features(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any],
        project_details: Dict[str, Any]
    ) -> PredictiveFeatures:
        """Extract features for prediction"""
        try:
            features = PredictiveFeatures(
                creator_a_id=creator_a['creator_id'],
                creator_b_id=creator_b['creator_id']
            )
            
            # Creator compatibility features
            features.skill_complementarity = await self._calculate_skill_complementarity(creator_a, creator_b)
            features.audience_overlap = creator_a.get('audience_overlap_with_b', 0.0)
            features.style_similarity = await self._calculate_style_similarity(creator_a, creator_b)
            features.experience_gap = await self._calculate_experience_gap(creator_a, creator_b)
            features.reputation_match = await self._calculate_reputation_match(creator_a, creator_b)
            
            # Project features
            features.project_complexity = await self._assess_project_complexity(project_details)
            features.timeline_feasibility = await self._assess_timeline_feasibility(project_details, creator_a, creator_b)
            features.budget_adequacy = await self._assess_budget_adequacy(project_details, creator_a, creator_b)
            features.resource_availability = await self._assess_resource_availability(creator_a, creator_b, project_details)
            features.market_demand = project_details.get('market_demand_score', 0.5)
            
            # Historical features
            features.individual_success_rates = (
                creator_a.get('success_rate', 0.5),
                creator_b.get('success_rate', 0.5)
            )
            features.collaboration_experience = (
                creator_a.get('collaboration_count', 0),
                creator_b.get('collaboration_count', 0)
            )
            features.similar_project_history = (
                creator_a.get('similar_projects', 0),
                creator_b.get('similar_projects', 0)
            )
            features.past_collaborations_together = await self._count_past_collaborations(creator_a, creator_b)
            
            # Communication features
            features.communication_style_match = await self._assess_communication_compatibility(creator_a, creator_b)
            features.timezone_compatibility = await self._calculate_timezone_compatibility(creator_a, creator_b)
            features.language_compatibility = await self._calculate_language_compatibility(creator_a, creator_b)
            features.response_time_compatibility = await self._assess_response_time_compatibility(creator_a, creator_b)
            
            # External factors
            features.market_conditions = await self._assess_market_conditions()
            features.seasonal_factors = await self._assess_seasonal_factors()
            features.competitive_landscape = await self._assess_competitive_landscape(project_details)
            features.platform_support = 0.8  # Assume good platform support
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting features: {e}")
            return PredictiveFeatures(
                creator_a_id=creator_a.get('creator_id', 'unknown'),
                creator_b_id=creator_b.get('creator_id', 'unknown')
            )
    
    async def _calculate_skill_complementarity(self, creator_a: Dict[str, Any], creator_b: Dict[str, Any]) -> float:
        """Calculate how complementary the creators' skills are"""
        skills_a = set(creator_a.get('skills', []))
        skills_b = set(creator_b.get('skills', []))
        
        if not skills_a or not skills_b:
            return 0.0
        
        # Calculate overlap and uniqueness
        overlap = len(skills_a & skills_b)
        unique_a = len(skills_a - skills_b)
        unique_b = len(skills_b - skills_a)
        total_skills = len(skills_a | skills_b)
        
        # Good complementarity: some overlap but also unique skills
        if total_skills == 0:
            return 0.0
        
        overlap_ratio = overlap / total_skills
        uniqueness_ratio = (unique_a + unique_b) / total_skills
        
        # Optimal is moderate overlap (20-40%) with high uniqueness
        overlap_score = 1.0 - abs(0.3 - overlap_ratio) / 0.7  # Peak at 30% overlap
        uniqueness_score = uniqueness_ratio
        
        return (overlap_score + uniqueness_score) / 2
    
    async def _calculate_style_similarity(self, creator_a: Dict[str, Any], creator_b: Dict[str, Any]) -> float:
        """Calculate style compatibility between creators"""
        style_a = creator_a.get('content_style', {})
        style_b = creator_b.get('content_style', {})
        
        if not style_a or not style_b:
            return 0.5
        
        # Compare style attributes
        style_attributes = ['tone', 'formality', 'creativity', 'technical_level']
        similarities = []
        
        for attr in style_attributes:
            val_a = style_a.get(attr, 0.5)
            val_b = style_b.get(attr, 0.5)
            similarity = 1.0 - abs(val_a - val_b)
            similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.5
    
    async def _calculate_experience_gap(self, creator_a: Dict[str, Any], creator_b: Dict[str, Any]) -> float:
        """Calculate experience gap between creators"""
        exp_a = creator_a.get('experience_years', 0)
        exp_b = creator_b.get('experience_years', 0)
        
        if exp_a == 0 and exp_b == 0:
            return 1.0  # Both inexperienced
        
        max_exp = max(exp_a, exp_b)
        min_exp = min(exp_a, exp_b)
        
        if max_exp == 0:
            return 0.0
        
        # Normalize gap (smaller gap is better)
        gap_ratio = min_exp / max_exp
        return gap_ratio
    
    async def _calculate_reputation_match(self, creator_a: Dict[str, Any], creator_b: Dict[str, Any]) -> float:
        """Calculate reputation compatibility"""
        rep_a = creator_a.get('reputation_score', 0.5)
        rep_b = creator_b.get('reputation_score', 0.5)
        
        # Both should have reasonable reputation, and gap shouldn't be too large
        avg_reputation = (rep_a + rep_b) / 2
        reputation_gap = abs(rep_a - rep_b)
        
        # Penalty for large reputation gaps
        gap_penalty = min(reputation_gap * 2, 1.0)
        
        return avg_reputation * (1.0 - gap_penalty)
    
    async def _assess_project_complexity(self, project_details: Dict[str, Any]) -> float:
        """Assess project complexity"""
        complexity_factors = []
        
        # Duration complexity
        duration_days = project_details.get('estimated_duration_days', 30)
        duration_complexity = min(duration_days / 90.0, 1.0)  # Max 90 days
        complexity_factors.append(duration_complexity)
        
        # Budget complexity
        budget = project_details.get('budget', 1000)
        budget_complexity = min(budget / 10000.0, 1.0)  # Max $10k
        complexity_factors.append(budget_complexity)
        
        # Deliverable complexity
        deliverables = project_details.get('deliverables', [])
        deliverable_complexity = min(len(deliverables) / 10.0, 1.0)  # Max 10 deliverables
        complexity_factors.append(deliverable_complexity)
        
        # Technical complexity
        tech_complexity = project_details.get('technical_complexity_score', 0.5)
        complexity_factors.append(tech_complexity)
        
        return np.mean(complexity_factors)
    
    async def _assess_timeline_feasibility(
        self,
        project_details: Dict[str, Any],
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any]
    ) -> float:
        """Assess if timeline is feasible"""
        requested_duration = project_details.get('requested_duration_days', 30)
        
        # Calculate typical duration for similar projects
        avg_duration_a = creator_a.get('average_project_duration', 30)
        avg_duration_b = creator_b.get('average_project_duration', 30)
        typical_duration = (avg_duration_a + avg_duration_b) / 2
        
        # Account for project complexity
        complexity = await self._assess_project_complexity(project_details)
        adjusted_typical_duration = typical_duration * (1 + complexity)
        
        # Calculate feasibility
        if requested_duration >= adjusted_typical_duration:
            return 1.0  # Very feasible
        else:
            ratio = requested_duration / adjusted_typical_duration
            return max(ratio, 0.0)
    
    async def _assess_budget_adequacy(
        self,
        project_details: Dict[str, Any],
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any]
    ) -> float:
        """Assess if budget is adequate"""
        offered_budget = project_details.get('budget', 1000)
        
        # Calculate typical rates
        rate_a = creator_a.get('hourly_rate', 50)
        rate_b = creator_b.get('hourly_rate', 50)
        avg_rate = (rate_a + rate_b) / 2
        
        # Estimate required hours
        estimated_hours = project_details.get('estimated_hours', 40)
        complexity = await self._assess_project_complexity(project_details)
        adjusted_hours = estimated_hours * (1 + complexity * 0.5)
        
        # Calculate required budget
        required_budget = avg_rate * adjusted_hours
        
        if required_budget == 0:
            return 0.5
        
        adequacy_ratio = offered_budget / required_budget
        return min(adequacy_ratio, 1.0)
    
    async def _assess_resource_availability(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any],
        project_details: Dict[str, Any]
    ) -> float:
        """Assess resource availability"""
        # Check availability
        availability_a = creator_a.get('availability_score', 0.5)
        availability_b = creator_b.get('availability_score', 0.5)
        
        # Check current workload
        workload_a = creator_a.get('current_workload', 0.5)
        workload_b = creator_b.get('current_workload', 0.5)
        
        # Calculate availability considering workload
        effective_availability_a = availability_a * (1.0 - workload_a)
        effective_availability_b = availability_b * (1.0 - workload_b)
        
        return (effective_availability_a + effective_availability_b) / 2
    
    async def _count_past_collaborations(self, creator_a: Dict[str, Any], creator_b: Dict[str, Any]) -> int:
        """Count past collaborations between creators"""
        # This would typically query a database
        collab_history_a = creator_a.get('collaboration_history', [])
        
        count = 0
        for collab in collab_history_a:
            if collab.get('partner_id') == creator_b['creator_id']:
                count += 1
        
        return count
    
    async def _assess_communication_compatibility(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any]
    ) -> float:
        """Assess communication style compatibility"""
        comm_a = creator_a.get('communication_style', {})
        comm_b = creator_b.get('communication_style', {})
        
        if not comm_a or not comm_b:
            return 0.5
        
        # Compare communication attributes
        attributes = ['directness', 'frequency', 'formality', 'detail_level']
        similarities = []
        
        for attr in attributes:
            val_a = comm_a.get(attr, 0.5)
            val_b = comm_b.get(attr, 0.5)
            similarity = 1.0 - abs(val_a - val_b)
            similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.5
    
    async def _calculate_timezone_compatibility(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any]
    ) -> float:
        """Calculate timezone compatibility"""
        tz_a = creator_a.get('timezone_offset', 0)
        tz_b = creator_b.get('timezone_offset', 0)
        
        # Calculate hour difference
        hour_diff = abs(tz_a - tz_b)
        
        # Normalize to 0-1 scale (12 hours max difference)
        compatibility = 1.0 - min(hour_diff / 12.0, 1.0)
        
        return compatibility
    
    async def _calculate_language_compatibility(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any]
    ) -> float:
        """Calculate language compatibility"""
        langs_a = set(creator_a.get('languages', ['en']))
        langs_b = set(creator_b.get('languages', ['en']))
        
        # Check for common languages
        common_languages = langs_a & langs_b
        
        if common_languages:
            return 1.0
        else:
            # Check for widely spoken languages
            universal_langs = {'en', 'es', 'fr', 'de', 'pt'}
            if (langs_a & universal_langs) and (langs_b & universal_langs):
                return 0.7
            else:
                return 0.3
    
    async def _assess_response_time_compatibility(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any]
    ) -> float:
        """Assess response time compatibility"""
        response_a = creator_a.get('avg_response_time_hours', 24)
        response_b = creator_b.get('avg_response_time_hours', 24)
        
        # Both should have reasonable response times
        max_acceptable = 48  # 48 hours
        
        if response_a > max_acceptable or response_b > max_acceptable:
            return 0.3
        
        # Calculate compatibility based on difference
        diff = abs(response_a - response_b)
        max_diff = 24  # 24 hours max difference
        
        compatibility = 1.0 - min(diff / max_diff, 1.0)
        
        return compatibility
    
    async def _assess_market_conditions(self) -> float:
        """Assess current market conditions"""
        # This would typically integrate with market data APIs
        # For now, return a reasonable default
        return 0.7
    
    async def _assess_seasonal_factors(self) -> float:
        """Assess seasonal factors"""
        now = datetime.now()
        month = now.month
        
        # Higher activity in certain months
        high_activity_months = [9, 10, 11, 1, 2, 3]  # Sep-Nov, Jan-Mar
        
        if month in high_activity_months:
            return 0.8
        else:
            return 0.6
    
    async def _assess_competitive_landscape(self, project_details: Dict[str, Any]) -> float:
        """Assess competitive landscape"""
        project_category = project_details.get('category', 'general')
        
        # Competitive factors by category (simplified)
        competition_map = {
            'technology': 0.9,  # High competition
            'design': 0.8,
            'marketing': 0.7,
            'content': 0.6,
            'music': 0.5,
            'general': 0.6
        }
        
        return competition_map.get(project_category, 0.6)
    
    async def predict_collaboration_success(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any],
        project_details: Dict[str, Any]
    ) -> SuccessPrediction:
        """Predict collaboration success"""
        try:
            # Generate cache key
            cache_key = f"{creator_a['creator_id']}_{creator_b['creator_id']}_{hash(str(project_details))}"
            
            # Check cache
            if cache_key in self.prediction_cache:
                return self.prediction_cache[cache_key]
            
            # Extract features
            features = await self.extract_features(creator_a, creator_b, project_details)
            feature_vector = features.to_vector()
            
            # Make predictions using different models
            predictions = {}
            
            # Success probability
            if 'success_classifier' in self.models:
                success_prob, confidence = self.models['success_classifier'].predict(feature_vector)
                predictions['success'] = (success_prob, confidence)
            
            # Quality prediction
            if 'quality_regressor' in self.models:
                quality_pred, quality_conf = self.models['quality_regressor'].predict(feature_vector)
                predictions['quality'] = (quality_pred, quality_conf)
            
            # Timeline adherence
            if 'timeline_predictor' in self.models:
                timeline_pred, timeline_conf = self.models['timeline_predictor'].predict(feature_vector)
                predictions['timeline'] = (timeline_pred, timeline_conf)
            
            # ROI prediction
            if 'roi_predictor' in self.models:
                roi_pred, roi_conf = self.models['roi_predictor'].predict(feature_vector)
                predictions['roi'] = (roi_pred, roi_conf)
            
            # Create prediction result
            prediction = SuccessPrediction(
                creator_a_id=creator_a['creator_id'],
                creator_b_id=creator_b['creator_id'],
                project_id=project_details.get('project_id')
            )
            
            # Set main prediction values
            if 'success' in predictions:
                prediction.success_probability = predictions['success'][0]
                overall_confidence = predictions['success'][1]
            else:
                prediction.success_probability = 0.5
                overall_confidence = 0.1
            
            # Set detailed predictions
            prediction.quality_score_prediction = predictions.get('quality', (0.5, 0.5))[0]
            prediction.timeline_adherence_probability = predictions.get('timeline', (0.5, 0.5))[0]
            prediction.budget_adherence_probability = features.budget_adequacy
            prediction.satisfaction_score_prediction = (prediction.quality_score_prediction + prediction.timeline_adherence_probability) / 2
            prediction.roi_prediction = predictions.get('roi', (0.5, 0.5))[0]
            
            # Determine outcome category
            prediction.predicted_outcome = self._categorize_outcome(prediction.success_probability)
            prediction.confidence = self._categorize_confidence(overall_confidence)
            
            # Identify risks and recommendations
            prediction.identified_risks = await self._identify_risks(features)
            prediction.risk_mitigation_suggestions = await self._generate_mitigation_suggestions(features)
            prediction.critical_success_factors = await self._identify_success_factors(features)
            
            # Calculate feature importance
            prediction.feature_importance = await self._calculate_feature_importance(feature_vector)
            
            # Generate explanation
            prediction.explanation = await self._generate_explanation(prediction, features)
            
            # Time predictions
            prediction.predicted_duration_days = int(
                project_details.get('estimated_duration_days', 30) * 
                (2.0 - prediction.timeline_adherence_probability)
            )
            
            # Cache result
            if len(self.prediction_cache) < self.cache_size_limit:
                self.prediction_cache[cache_key] = prediction
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error predicting collaboration success: {e}")
            return SuccessPrediction(
                creator_a_id=creator_a.get('creator_id', 'unknown'),
                creator_b_id=creator_b.get('creator_id', 'unknown'),
                success_probability=0.5,
                confidence=PredictionConfidence.VERY_LOW
            )
    
    def _categorize_outcome(self, success_probability: float) -> CollaborationOutcome:
        """Categorize outcome based on success probability"""
        if success_probability >= 0.9:
            return CollaborationOutcome.HIGHLY_SUCCESSFUL
        elif success_probability >= 0.7:
            return CollaborationOutcome.SUCCESSFUL
        elif success_probability >= 0.5:
            return CollaborationOutcome.MODERATELY_SUCCESSFUL
        elif success_probability >= 0.3:
            return CollaborationOutcome.MIXED_RESULTS
        elif success_probability >= 0.1:
            return CollaborationOutcome.UNSUCCESSFUL
        else:
            return CollaborationOutcome.FAILED
    
    def _categorize_confidence(self, confidence_score: float) -> PredictionConfidence:
        """Categorize confidence level"""
        if confidence_score >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif confidence_score >= 0.8:
            return PredictionConfidence.HIGH
        elif confidence_score >= 0.6:
            return PredictionConfidence.MEDIUM
        elif confidence_score >= 0.4:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    async def _identify_risks(self, features: PredictiveFeatures) -> List[str]:
        """Identify potential risks"""
        risks = []
        
        if features.timeline_feasibility < 0.5:
            risks.append("tight_timeline")
        
        if features.budget_adequacy < 0.6:
            risks.append("insufficient_budget")
        
        if features.communication_style_match < 0.4:
            risks.append("communication_mismatch")
        
        if features.experience_gap < 0.3:
            risks.append("large_experience_gap")
        
        if features.timezone_compatibility < 0.5:
            risks.append("timezone_challenges")
        
        if features.project_complexity > 0.8:
            risks.append("high_project_complexity")
        
        if features.resource_availability < 0.5:
            risks.append("limited_resource_availability")
        
        return risks
    
    async def _generate_mitigation_suggestions(self, features: PredictiveFeatures) -> List[str]:
        """Generate risk mitigation suggestions"""
        suggestions = []
        
        if features.timeline_feasibility < 0.5:
            suggestions.append("Consider extending the project timeline")
        
        if features.budget_adequacy < 0.6:
            suggestions.append("Adjust budget or reduce scope")
        
        if features.communication_style_match < 0.4:
            suggestions.append("Establish clear communication protocols")
        
        if features.timezone_compatibility < 0.5:
            suggestions.append("Schedule regular sync meetings")
        
        if features.project_complexity > 0.8:
            suggestions.append("Break project into smaller milestones")
        
        return suggestions
    
    async def _identify_success_factors(self, features: PredictiveFeatures) -> List[str]:
        """Identify critical success factors"""
        factors = []
        
        if features.skill_complementarity > 0.7:
            factors.append("excellent_skill_complementarity")
        
        if features.past_collaborations_together > 0:
            factors.append("proven_collaboration_history")
        
        if min(features.individual_success_rates) > 0.8:
            factors.append("high_individual_success_rates")
        
        if features.communication_style_match > 0.7:
            factors.append("compatible_communication_styles")
        
        if features.market_demand > 0.7:
            factors.append("high_market_demand")
        
        return factors
    
    async def _calculate_feature_importance(self, feature_vector: np.ndarray) -> Dict[str, float]:
        """Calculate feature importance for prediction"""
        feature_names = self._get_feature_names()
        
        # Simple importance based on feature magnitude
        importances = {}
        for i, name in enumerate(feature_names):
            if i < len(feature_vector):
                importances[name] = float(abs(feature_vector[i]))
        
        # Normalize importances
        total = sum(importances.values())
        if total > 0:
            for name in importances:
                importances[name] /= total
        
        return importances
    
    async def _generate_explanation(self, prediction: SuccessPrediction, features: PredictiveFeatures) -> str:
        """Generate human-readable explanation"""
        probability = prediction.success_probability
        
        if probability >= 0.8:
            explanation = "This collaboration shows excellent potential for success"
        elif probability >= 0.6:
            explanation = "This collaboration has good potential for success"
        elif probability >= 0.4:
            explanation = "This collaboration has moderate potential with some risks"
        else:
            explanation = "This collaboration faces significant challenges"
        
        # Add key factors
        if features.skill_complementarity > 0.7:
            explanation += " due to highly complementary skills"
        elif features.skill_complementarity < 0.3:
            explanation += " with concerns about skill compatibility"
        
        if features.past_collaborations_together > 0:
            explanation += " and proven collaboration history"
        
        return explanation
    
    async def train_models(self, training_data: List[Dict[str, Any]]):
        """Train prediction models with historical data"""
        try:
            logger.info("🚀 Starting collaboration prediction model training...")
            
            if len(training_data) < 20:
                logger.warning("⚠️ Insufficient training data for reliable models")
                return
            
            # Prepare training data
            X, y_success, y_quality, y_timeline, y_roi = await self._prepare_training_data(training_data)
            
            # Train success classifier
            if 'success_classifier' in self.models:
                self.models['success_classifier'].model.fit(X, y_success)
                logger.info("✅ Success classifier trained")
            
            # Train quality regressor
            if 'quality_regressor' in self.models and len(y_quality) > 0:
                self.models['quality_regressor'].model.fit(X, y_quality)
                logger.info("✅ Quality regressor trained")
            
            # Train timeline predictor
            if 'timeline_predictor' in self.models and len(y_timeline) > 0:
                self.models['timeline_predictor'].model.fit(X, y_timeline)
                logger.info("✅ Timeline predictor trained")
            
            # Train ROI predictor
            if 'roi_predictor' in self.models and len(y_roi) > 0:
                self.models['roi_predictor'].model.fit(X, y_roi)
                logger.info("✅ ROI predictor trained")
            
            logger.info("🎯 Collaboration prediction model training completed")
            
        except Exception as e:
            logger.error(f"❌ Error training models: {e}")
    
    async def _prepare_training_data(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data for models"""
        X, y_success, y_quality, y_timeline, y_roi = [], [], [], [], []
        
        for sample in training_data:
            try:
                # Extract features
                features = await self.extract_features(
                    sample['creator_a'],
                    sample['creator_b'],
                    sample['project_details']
                )
                
                X.append(features.to_vector())
                
                # Extract targets
                y_success.append(int(sample.get('successful', False)))
                y_quality.append(sample.get('quality_score', 0.5))
                y_timeline.append(sample.get('timeline_adherence', 0.5))
                y_roi.append(sample.get('roi_score', 0.5))
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing training sample: {e}")
        
        return (
            np.array(X),
            np.array(y_success),
            np.array(y_quality),
            np.array(y_timeline),
            np.array(y_roi)
        )
    
    async def batch_predict(
        self,
        collaboration_requests: List[Dict[str, Any]]
    ) -> List[SuccessPrediction]:
        """Batch predict success for multiple collaboration requests"""
        predictions = []
        
        for request in collaboration_requests:
            try:
                prediction = await self.predict_collaboration_success(
                    request['creator_a'],
                    request['creator_b'],
                    request['project_details']
                )
                predictions.append(prediction)
                
            except Exception as e:
                logger.warning(f"⚠️ Error in batch prediction: {e}")
        
        return predictions
    
    async def get_prediction_analytics(self) -> Dict[str, Any]:
        """Get analytics on prediction performance"""
        if not self.models:
            return {"models": 0, "predictions": 0}
        
        analytics = {
            "total_models": len(self.models),
            "total_predictions": sum(model.prediction_count for model in self.models.values()),
            "cache_size": len(self.prediction_cache),
            "model_performance": {}
        }
        
        for name, model in self.models.items():
            analytics["model_performance"][name] = {
                "training_accuracy": model.training_accuracy,
                "validation_accuracy": model.validation_accuracy,
                "last_trained": model.last_trained.isoformat(),
                "prediction_count": model.prediction_count
            }
        
        return analytics
    
    async def clear_cache(self):
        """Clear prediction cache"""
        self.prediction_cache.clear()
        logger.info("🗑️ Collaboration prediction cache cleared")