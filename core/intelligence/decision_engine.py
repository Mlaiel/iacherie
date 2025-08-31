"""
Decision Engine - Advanced AI Decision Making System

Provides intelligent decision-making capabilities for content protection,
monetization strategies, collaboration matching, and platform optimization.
Uses rule-based logic combined with machine learning models to make
optimal decisions for content creators.

Features:
- Multi-criteria decision analysis
- Risk-based decision making
- Revenue optimization decisions
- Protection strategy selection
- Platform distribution decisions
- Collaboration matching logic

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import json

# ML/AI Libraries
import torch
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Core Dependencies
from ..adapters.decision_adapter import DecisionAdapter
from ..processors.rule_processor import RuleProcessor
from ..engines.optimization_engine import OptimizationEngine
from ..storage.decision_storage import DecisionStorage


class DecisionType(Enum):
    """Types of decisions the engine can make"""
    PROTECTION_STRATEGY = "protection_strategy"
    MONETIZATION_PLAN = "monetization_plan"
    PLATFORM_SELECTION = "platform_selection"
    COLLABORATION_MATCH = "collaboration_match"
    CONTENT_OPTIMIZATION = "content_optimization"
    RISK_MITIGATION = "risk_mitigation"
    REVENUE_STRATEGY = "revenue_strategy"


class DecisionPriority(Enum):
    """Decision priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DecisionStatus(Enum):
    """Decision execution status"""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DecisionCriteria:
    """Criteria for decision making"""
    content_quality: float
    engagement_potential: float
    monetization_score: float
    risk_level: float
    user_preferences: Dict[str, Any]
    market_conditions: Dict[str, Any]
    platform_metrics: Dict[str, Any]
    historical_performance: Dict[str, Any]


@dataclass
class DecisionOption:
    """A decision option with scoring"""
    option_id: str
    description: str
    score: float
    confidence: float
    benefits: List[str]
    risks: List[str]
    cost: float
    expected_roi: float
    implementation_time: int  # in hours
    required_resources: List[str]


@dataclass
class DecisionResult:
    """Result of a decision process"""
    decision_id: str
    decision_type: DecisionType
    selected_option: DecisionOption
    alternative_options: List[DecisionOption]
    reasoning: str
    confidence_score: float
    risk_assessment: Dict[str, float]
    expected_outcomes: Dict[str, Any]
    monitoring_plan: Dict[str, Any]
    created_at: datetime
    priority: DecisionPriority
    status: DecisionStatus


class DecisionEngine:
    """
    Advanced AI-powered decision engine for content strategy optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the decision engine
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_models()
        self._initialize_processors()
        self._initialize_storage()
        
        # Decision tracking
        self.active_decisions = {}
        self.decision_history = []
        self.performance_metrics = {
            "total_decisions": 0,
            "successful_decisions": 0,
            "average_confidence": 0.0,
            "roi_accuracy": 0.0
        }
    
    def _initialize_models(self) -> None:
        """Initialize ML models for decision making"""



        try:
            # Revenue prediction model
            self.revenue_model = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            
            # Risk assessment model
            self.risk_model = RandomForestClassifier(
                n_estimators=50,
                random_state=42
            )
            
            # Platform performance model
            self.platform_model = RandomForestClassifier(
                n_estimators=75,
                random_state=42
            )
            
            # Feature scaler
            self.scaler = StandardScaler()
            
            # Load pre-trained models if available
            self._load_pretrained_models()
            
            self.logger.info("Decision models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {e}")
            raise
    
    def _initialize_processors(self) -> None:
        """Initialize decision processors"""
        self.decision_adapter = DecisionAdapter(self.config)
        self.rule_processor = RuleProcessor(self.config)
        self.optimization_engine = OptimizationEngine(self.config)
    
    def _initialize_storage(self) -> None:
        """Initialize decision storage"""
        self.decision_storage = DecisionStorage(self.config)
    
    def _load_pretrained_models(self) -> None:
        """Load pre-trained models from storage"""



        try:
            # This would load actual pre-trained models in production
            # For now, we'll train with synthetic data
            self._train_with_synthetic_data()
        except Exception as e:
            self.logger.warning(f"Could not load pre-trained models: {e}")
    
    def _train_with_synthetic_data(self) -> None:
        """Train models with synthetic data for demonstration"""
        # Generate synthetic training data
        n_samples = 1000
        
        # Revenue prediction data
        X_revenue = np.random.rand(n_samples, 8)  # 8 features
        y_revenue = (X_revenue[:, 0] + X_revenue[:, 1] + X_revenue[:, 2]) > 1.5
        
        # Risk assessment data
        X_risk = np.random.rand(n_samples, 6)  # 6 features
        y_risk = (X_risk[:, 0] * X_risk[:, 1]) > 0.5
        
        # Platform performance data
        X_platform = np.random.rand(n_samples, 7)  # 7 features
        y_platform = np.argmax(X_platform[:, :3], axis=1)  # 3 platform classes
        
        # Train models
        self.revenue_model.fit(X_revenue, y_revenue)
        self.risk_model.fit(X_risk, y_risk)
        self.platform_model.fit(X_platform, y_platform)
        
        # Fit scaler
        self.scaler.fit(np.vstack([X_revenue, X_risk, X_platform]))
        
        self.logger.info("Models trained with synthetic data")
    
    async def make_decision(
        self,
        decision_type: DecisionType,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> DecisionResult:
        """
        Make an intelligent decision based on criteria and context
        
        Args:
            decision_type: Type of decision to make
            criteria: Decision criteria
            context: Additional context information
            
        Returns:
            DecisionResult: Complete decision with reasoning
        """
        start_time = datetime.now()
        decision_id = self._generate_decision_id(decision_type)
        
        try:
            self.logger.info(f"Making decision {decision_id} of type {decision_type.value}")
            
            # Generate decision options
            options = await self._generate_options(decision_type, criteria, context)
            
            # Evaluate options
            evaluated_options = await self._evaluate_options(options, criteria, context)
            
            # Select best option
            selected_option = self._select_best_option(evaluated_options)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(selected_option, evaluated_options, criteria)
            
            # Assess risks
            risk_assessment = self._assess_decision_risks(selected_option, criteria)
            
            # Predict outcomes
            expected_outcomes = await self._predict_outcomes(selected_option, criteria)
            
            # Create monitoring plan
            monitoring_plan = self._create_monitoring_plan(selected_option, decision_type)
            
            # Determine priority
            priority = self._determine_priority(selected_option, criteria)
            
            # Calculate confidence
            confidence_score = self._calculate_confidence(selected_option, evaluated_options)
            
            # Create decision result
            decision_result = DecisionResult(
                decision_id=decision_id,
                decision_type=decision_type,
                selected_option=selected_option,
                alternative_options=[opt for opt in evaluated_options if opt != selected_option],
                reasoning=reasoning,
                confidence_score=confidence_score,
                risk_assessment=risk_assessment,
                expected_outcomes=expected_outcomes,
                monitoring_plan=monitoring_plan,
                created_at=start_time,
                priority=priority,
                status=DecisionStatus.APPROVED
            )
            
            # Store decision
            await self._store_decision(decision_result)
            
            # Update metrics
            self._update_performance_metrics(decision_result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Decision {decision_id} completed in {processing_time:.2f}s")
            
            return decision_result
            
        except Exception as e:
            self.logger.error(f"Decision making failed for {decision_id}: {e}")
            raise
    
    async def _generate_options(
        self,
        decision_type: DecisionType,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DecisionOption]:
        """Generate decision options based on type and criteria"""
        
        if decision_type == DecisionType.PROTECTION_STRATEGY:
            return self._generate_protection_options(criteria, context)
        
        elif decision_type == DecisionType.MONETIZATION_PLAN:
            return self._generate_monetization_options(criteria, context)
        
        elif decision_type == DecisionType.PLATFORM_SELECTION:
            return self._generate_platform_options(criteria, context)
        
        elif decision_type == DecisionType.COLLABORATION_MATCH:
            return self._generate_collaboration_options(criteria, context)
        
        elif decision_type == DecisionType.CONTENT_OPTIMIZATION:
            return self._generate_optimization_options(criteria, context)
        
        elif decision_type == DecisionType.RISK_MITIGATION:
            return self._generate_risk_mitigation_options(criteria, context)
        
        elif decision_type == DecisionType.REVENUE_STRATEGY:
            return self._generate_revenue_strategy_options(criteria, context)
        
        else:
            return []
    
    def _generate_protection_options(
        self,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DecisionOption]:
        """Generate content protection strategy options"""
        options = []
        
        # Basic protection option
        options.append(DecisionOption(
            option_id="basic_protection",
            description="Basic fingerprinting and monitoring",
            score=0.0,  # Will be calculated
            confidence=0.8,
            benefits=["Cost-effective", "Quick implementation", "Basic coverage"],
            risks=["Limited detection", "Manual intervention needed"],
            cost=100.0,
            expected_roi=2.0,
            implementation_time=24,
            required_resources=["fingerprinting_service", "basic_monitoring"]
        ))
        
        # Advanced protection option
        options.append(DecisionOption(
            option_id="advanced_protection",
            description="AI-powered multi-platform protection",
            score=0.0,
            confidence=0.9,
            benefits=["Comprehensive coverage", "Automated responses", "High accuracy"],
            risks=["Higher cost", "Complex setup"],
            cost=500.0,
            expected_roi=5.0,
            implementation_time=72,
            required_resources=["ai_engine", "multi_platform_apis", "legal_framework"]
        ))
        
        # Premium protection option
        if criteria.monetization_score > 80:
            options.append(DecisionOption(
                option_id="premium_protection",
                description="Enterprise-grade protection with legal support",
                score=0.0,
                confidence=0.95,
                benefits=["Maximum protection", "Legal backing", "Priority support"],
                risks=["High cost", "Long setup time"],
                cost=1500.0,
                expected_roi=8.0,
                implementation_time=168,
                required_resources=["enterprise_ai", "legal_team", "priority_support"]
            ))
        
        return options
    
    def _generate_monetization_options(
        self,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DecisionOption]:
        """Generate monetization strategy options"""
        options = []
        
        # Streaming monetization
        if criteria.content_quality > 60:
            options.append(DecisionOption(
                option_id="streaming_monetization",
                description="Focus on streaming platform royalties",
                score=0.0,
                confidence=0.85,
                benefits=["Passive income", "Scalable", "Platform support"],
                risks=["Low per-stream rates", "Platform dependency"],
                cost=50.0,
                expected_roi=3.0,
                implementation_time=12,
                required_resources=["streaming_platforms", "metadata_optimization"]
            ))
        
        # Direct sales
        if criteria.engagement_potential > 70:
            options.append(DecisionOption(
                option_id="direct_sales",
                description="Direct sales and merchandise",
                score=0.0,
                confidence=0.75,
                benefits=["Higher margins", "Direct fan connection", "Brand building"],
                risks=["Marketing required", "Inventory management"],
                cost=200.0,
                expected_roi=6.0,
                implementation_time=48,
                required_resources=["e_commerce_platform", "marketing_budget", "fulfillment"]
            ))
        
        # Licensing strategy
        if criteria.content_quality > 80:
            options.append(DecisionOption(
                option_id="licensing_strategy",
                description="Content licensing to media companies",
                score=0.0,
                confidence=0.9,
                benefits=["High revenue potential", "Professional exposure", "Long-term deals"],
                risks=["Competitive market", "Negotiation complexity"],
                cost=300.0,
                expected_roi=10.0,
                implementation_time=96,
                required_resources=["licensing_agent", "legal_support", "portfolio_preparation"]
            ))
        
        return options
    
    def _generate_platform_options(
        self,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DecisionOption]:
        """Generate platform selection options"""
        options = []
        
        platforms = [
            {
                "id": "youtube_focus",
                "name": "YouTube",
                "description": "Focus on YouTube for video content",
                "cost": 100.0,
                "roi": 4.0,
                "time": 24,
                "fit_score": criteria.engagement_potential * 0.8
            },
            {
                "id": "tiktok_focus", 
                "name": "TikTok",
                "description": "Focus on TikTok for short-form content",
                "cost": 75.0,
                "roi": 6.0,
                "time": 16,
                "fit_score": criteria.engagement_potential * 0.9 if criteria.content_quality > 60 else 0.3
            },
            {
                "id": "instagram_focus",
                "name": "Instagram",
                "description": "Focus on Instagram for visual content",
                "cost": 80.0,
                "roi": 3.5,
                "time": 20,
                "fit_score": criteria.monetization_score * 0.7
            },
            {
                "id": "spotify_focus",
                "name": "Spotify",
                "description": "Focus on Spotify for audio content",
                "cost": 60.0,
                "roi": 3.0,
                "time": 12,
                "fit_score": criteria.content_quality * 0.6
            }
        ]
        
        for platform in platforms:
            if platform["fit_score"] > 40:  # Only include if good fit
                options.append(DecisionOption(
                    option_id=platform["id"],
                    description=platform["description"],
                    score=platform["fit_score"],
                    confidence=0.8,
                    benefits=[f"Optimized for {platform['name']}", "Platform-specific features"],
                    risks=["Platform dependency", "Algorithm changes"],
                    cost=platform["cost"],
                    expected_roi=platform["roi"],
                    implementation_time=platform["time"],
                    required_resources=[f"{platform['name'].lower()}_api", "content_optimization"]
                ))
        
        return options
    
    def _generate_collaboration_options(
        self,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DecisionOption]:
        """Generate collaboration matching options"""
        options = []
        
        # Similar artists collaboration
        options.append(DecisionOption(
            option_id="similar_artists",
            description="Collaborate with artists in similar genre",
            score=0.0,
            confidence=0.8,
            benefits=["Audience overlap", "Genre expertise", "Mutual growth"],
            risks=["Competition", "Shared revenue"],
            cost=150.0,
            expected_roi=4.0,
            implementation_time=48,
            required_resources=["artist_matching", "collaboration_platform"]
        ))
        
        # Cross-genre collaboration
        if criteria.engagement_potential > 70:
            options.append(DecisionOption(
                option_id="cross_genre",
                description="Collaborate with artists from different genres",
                score=0.0,
                confidence=0.7,
                benefits=["Audience expansion", "Creative innovation", "Viral potential"],
                risks=["Audience mismatch", "Creative differences"],
                cost=200.0,
                expected_roi=6.0,
                implementation_time=72,
                required_resources=["cross_genre_matching", "creative_direction"]
            ))
        
        # Influencer collaboration
        if criteria.monetization_score > 60:
            options.append(DecisionOption(
                option_id="influencer_collab",
                description="Partner with social media influencers",
                score=0.0,
                confidence=0.85,
                benefits=["Large reach", "Social media boost", "Brand awareness"],
                risks=["High cost", "Brand alignment"],
                cost=500.0,
                expected_roi=5.0,
                implementation_time=36,
                required_resources=["influencer_network", "campaign_management"]
            ))
        
        return options
    
    def _generate_optimization_options(
        self,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DecisionOption]:
        """Generate content optimization options"""
        options = []
        
        # SEO optimization
        options.append(DecisionOption(
            option_id="seo_optimization",
            description="Optimize content for search discovery",
            score=0.0,
            confidence=0.9,
            benefits=["Organic discovery", "Long-term traffic", "Cost-effective"],
            risks=["Time to results", "Algorithm changes"],
            cost=100.0,
            expected_roi=4.0,
            implementation_time=24,
            required_resources=["seo_tools", "keyword_research", "metadata_optimization"]
        ))
        
        # Quality enhancement
        if criteria.content_quality < 80:
            options.append(DecisionOption(
                option_id="quality_enhancement",
                description="Improve content quality through post-processing",
                score=0.0,
                confidence=0.8,
                benefits=["Better audience retention", "Professional appearance", "Platform favor"],
                risks=["Additional cost", "Processing time"],
                cost=200.0,
                expected_roi=3.0,
                implementation_time=48,
                required_resources=["editing_software", "professional_services"]
            ))
        
        # Engagement optimization
        if criteria.engagement_potential < 70:
            options.append(DecisionOption(
                option_id="engagement_optimization",
                description="Optimize content for maximum engagement",
                score=0.0,
                confidence=0.85,
                benefits=["Higher engagement rates", "Algorithm boost", "Audience growth"],
                risks=["Content format changes", "Audience adaptation"],
                cost=150.0,
                expected_roi=5.0,
                implementation_time=36,
                required_resources=["engagement_analytics", "a_b_testing", "content_strategy"]
            ))
        
        return options
    
    def _generate_risk_mitigation_options(
        self,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DecisionOption]:
        """Generate risk mitigation options"""
        options = []
        
        # Copyright protection
        if criteria.risk_level > 0.5:
            options.append(DecisionOption(
                option_id="copyright_protection",
                description="Implement comprehensive copyright protection",
                score=0.0,
                confidence=0.9,
                benefits=["Legal protection", "Revenue recovery", "Deterrent effect"],
                risks=["Implementation cost", "False positives"],
                cost=300.0,
                expected_roi=4.0,
                implementation_time=72,
                required_resources=["legal_framework", "monitoring_system", "enforcement_tools"]
            ))
        
        # Diversification strategy
        options.append(DecisionOption(
            option_id="diversification",
            description="Diversify across multiple platforms and revenue streams",
            score=0.0,
            confidence=0.8,
            benefits=["Risk distribution", "Multiple income sources", "Platform independence"],
            risks=["Resource distribution", "Management complexity"],
            cost=250.0,
            expected_roi=3.5,
            implementation_time=96,
            required_resources=["multi_platform_management", "analytics_dashboard"]
        ))
        
        # Insurance and backup
        if criteria.monetization_score > 70:
            options.append(DecisionOption(
                option_id="insurance_backup",
                description="Content insurance and backup strategies",
                score=0.0,
                confidence=0.7,
                benefits=["Financial protection", "Business continuity", "Peace of mind"],
                risks=["Ongoing cost", "Limited coverage"],
                cost=150.0,
                expected_roi=2.0,
                implementation_time=24,
                required_resources=["insurance_provider", "backup_infrastructure"]
            ))
        
        return options
    
    def _generate_revenue_strategy_options(
        self,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DecisionOption]:
        """Generate revenue strategy options"""
        options = []
        
        # Subscription model
        if criteria.engagement_potential > 75:
            options.append(DecisionOption(
                option_id="subscription_model",
                description="Launch subscription-based premium content",
                score=0.0,
                confidence=0.8,
                benefits=["Recurring revenue", "Loyal fanbase", "Predictable income"],
                risks=["Content demand", "Subscription fatigue"],
                cost=400.0,
                expected_roi=7.0,
                implementation_time=120,
                required_resources=["subscription_platform", "premium_content", "community_management"]
            ))
        
        # Pay-per-view model
        if criteria.content_quality > 85:
            options.append(DecisionOption(
                option_id="pay_per_view",
                description="High-value pay-per-view content",
                score=0.0,
                confidence=0.75,
                benefits=["High margin", "Premium positioning", "Event marketing"],
                risks=["Limited audience", "Production cost"],
                cost=600.0,
                expected_roi=10.0,
                implementation_time=168,
                required_resources=["ppv_platform", "premium_production", "marketing_campaign"]
            ))
        
        # Freemium model
        options.append(DecisionOption(
            option_id="freemium_model",
            description="Free content with premium upgrades",
            score=0.0,
            confidence=0.85,
            benefits=["Wide reach", "Conversion funnel", "Low barrier to entry"],
            risks=["Conversion rates", "Free content cost"],
            cost=200.0,
            expected_roi=4.0,
            implementation_time=72,
            required_resources=["freemium_platform", "conversion_optimization", "analytics"]
        ))
        
        return options
    
    async def _evaluate_options(
        self,
        options: List[DecisionOption],
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DecisionOption]:
        """Evaluate and score decision options"""
        evaluated_options = []
        
        for option in options:
            # Calculate multi-criteria score
            score = self._calculate_option_score(option, criteria)
            
            # Update option with calculated score
            option.score = score
            
            # Add ML-based adjustments
            ml_adjustment = await self._get_ml_score_adjustment(option, criteria)
            option.score += ml_adjustment
            
            # Ensure score is within bounds
            option.score = max(0.0, min(100.0, option.score))
            
            evaluated_options.append(option)
        
        # Sort by score (highest first)
        evaluated_options.sort(key=lambda x: x.score, reverse=True)
        
        return evaluated_options
    
    def _calculate_option_score(
        self,
        option: DecisionOption,
        criteria: DecisionCriteria
    ) -> float:
        """Calculate base score for an option"""
        score = 0.0
        
        # ROI weight (30%)
        roi_score = min(100, option.expected_roi * 10)
        score += roi_score * 0.3
        
        # Cost efficiency weight (20%)
        cost_efficiency = max(0, 100 - (option.cost / 10))
        score += cost_efficiency * 0.2
        
        # Implementation speed weight (15%)
        speed_score = max(0, 100 - (option.implementation_time / 2))
        score += speed_score * 0.15
        
        # Quality alignment weight (20%)
        quality_alignment = criteria.content_quality
        score += quality_alignment * 0.2
        
        # Risk adjustment weight (15%)
        risk_penalty = criteria.risk_level * 50
        score += (100 - risk_penalty) * 0.15
        
        return score
    
    async def _get_ml_score_adjustment(
        self,
        option: DecisionOption,
        criteria: DecisionCriteria
    ) -> float:
        """Get ML-based score adjustment"""



        try:
            # Prepare features for ML models
            features = self._prepare_ml_features(option, criteria)
            
            # Get predictions from different models
            revenue_pred = self.revenue_model.predict_proba([features])[0][1]
            risk_pred = self.risk_model.predict_proba([features])[0][1]
            
            # Calculate adjustment
            adjustment = (revenue_pred * 10) - (risk_pred * 5)
            
            return adjustment
            
        except Exception as e:
            self.logger.warning(f"ML score adjustment failed: {e}")
            return 0.0
    
    def _prepare_ml_features(
        self,
        option: DecisionOption,
        criteria: DecisionCriteria
    ) -> List[float]:
        """Prepare features for ML models"""
        features = [
            criteria.content_quality / 100,
            criteria.engagement_potential / 100,
            criteria.monetization_score / 100,
            criteria.risk_level,
            option.expected_roi / 10,
            option.cost / 1000,
            option.implementation_time / 168,
            option.confidence
        ]
        return features
    
    def _select_best_option(self, evaluated_options: List[DecisionOption]) -> DecisionOption:
        """Select the best option from evaluated options"""
        if not evaluated_options:
            raise ValueError("No options available for selection")
        
        # Return the highest scored option
        return evaluated_options[0]
    
    def _generate_reasoning(
        self,
        selected_option: DecisionOption,
        all_options: List[DecisionOption],
        criteria: DecisionCriteria
    ) -> str:
        """Generate human-readable reasoning for the decision"""
        reasoning = f"Selected '{selected_option.description}' with a score of {selected_option.score:.1f}. "
        
        # Add key factors
        reasoning += f"This option offers an expected ROI of {selected_option.expected_roi:.1f}x "
        reasoning += f"with implementation cost of €{selected_option.cost:.0f}. "
        
        # Compare with alternatives
        if len(all_options) > 1:
            second_best = all_options[1]
            score_diff = selected_option.score - second_best.score
            reasoning += f"It scored {score_diff:.1f} points higher than the next best option '{second_best.description}'. "
        
        # Add specific benefits
        if selected_option.benefits:
            reasoning += f"Key benefits include: {', '.join(selected_option.benefits[:3])}. "
        
        # Add risk consideration
        if selected_option.risks:
            reasoning += f"Main risks to monitor: {', '.join(selected_option.risks[:2])}."
        
        return reasoning
    
    def _assess_decision_risks(
        self,
        selected_option: DecisionOption,
        criteria: DecisionCriteria
    ) -> Dict[str, float]:
        """Assess risks associated with the decision"""
        risks = {}
        
        # Financial risk
        financial_risk = min(0.9, selected_option.cost / 1000)
        risks["financial_risk"] = financial_risk
        
        # Implementation risk
        implementation_risk = min(0.8, selected_option.implementation_time / 168)
        risks["implementation_risk"] = implementation_risk
        
        # Market risk
        market_risk = criteria.risk_level
        risks["market_risk"] = market_risk
        
        # ROI risk
        roi_risk = max(0.1, 1.0 - (selected_option.confidence / 1.0))
        risks["roi_risk"] = roi_risk
        
        # Overall risk
        risks["overall_risk"] = np.mean(list(risks.values()))
        
        return risks
    
    async def _predict_outcomes(
        self,
        selected_option: DecisionOption,
        criteria: DecisionCriteria
    ) -> Dict[str, Any]:
        """Predict expected outcomes from the decision"""
        outcomes = {}
        
        # Revenue prediction
        outcomes["expected_revenue"] = selected_option.expected_roi * selected_option.cost
        
        # Timeline prediction
        outcomes["implementation_timeline"] = selected_option.implementation_time
        
        # Success probability
        outcomes["success_probability"] = selected_option.confidence
        
        # Market impact prediction
        outcomes["market_impact"] = criteria.engagement_potential / 100
        
        # Risk mitigation success
        outcomes["risk_mitigation"] = max(0.3, 1.0 - criteria.risk_level)
        
        return outcomes
    
    def _create_monitoring_plan(
        self,
        selected_option: DecisionOption,
        decision_type: DecisionType
    ) -> Dict[str, Any]:
        """Create monitoring plan for decision execution"""
        plan = {
            "monitoring_frequency": "weekly",
            "key_metrics": [],
            "alert_thresholds": {},
            "review_schedule": [],
            "success_criteria": []
        }
        
        # Add type-specific monitoring
        if decision_type == DecisionType.MONETIZATION_PLAN:
            plan["key_metrics"].extend(["revenue", "conversion_rate", "customer_acquisition_cost"])
            plan["alert_thresholds"]["revenue_decline"] = 0.2
            
        elif decision_type == DecisionType.PROTECTION_STRATEGY:
            plan["key_metrics"].extend(["detection_rate", "false_positives", "response_time"])
            plan["alert_thresholds"]["detection_rate_drop"] = 0.1
            
        elif decision_type == DecisionType.PLATFORM_SELECTION:
            plan["key_metrics"].extend(["engagement_rate", "reach", "conversion"])
            plan["alert_thresholds"]["engagement_drop"] = 0.15
        
        # Add general monitoring
        plan["key_metrics"].extend(["roi", "cost", "timeline_adherence"])
        plan["alert_thresholds"]["roi_below_expected"] = 0.2
        
        # Review schedule
        plan["review_schedule"] = [
            {"period": "1_week", "focus": "initial_implementation"},
            {"period": "1_month", "focus": "early_results"},
            {"period": "3_months", "focus": "full_evaluation"}
        ]
        
        # Success criteria
        plan["success_criteria"] = [
            f"Achieve at least {selected_option.expected_roi * 0.8:.1f}x ROI",
            f"Complete implementation within {selected_option.implementation_time * 1.2:.0f} hours",
            "Maintain risk levels below 0.3"
        ]
        
        return plan
    
    def _determine_priority(
        self,
        selected_option: DecisionOption,
        criteria: DecisionCriteria
    ) -> DecisionPriority:
        """Determine decision priority level"""
        # High-impact, high-urgency decisions
        if selected_option.expected_roi > 5.0 and criteria.risk_level > 0.7:
            return DecisionPriority.CRITICAL
        
        # High ROI or high risk
        if selected_option.expected_roi > 7.0 or criteria.risk_level > 0.6:
            return DecisionPriority.HIGH
        
        # Moderate impact
        if selected_option.expected_roi > 3.0 or criteria.monetization_score > 70:
            return DecisionPriority.MEDIUM
        
        # Low impact
        return DecisionPriority.LOW
    
    def _calculate_confidence(
        self,
        selected_option: DecisionOption,
        all_options: List[DecisionOption]
    ) -> float:
        """Calculate confidence in the decision"""
        if len(all_options) <= 1:
            return selected_option.confidence
        
        # Base confidence from option
        confidence = selected_option.confidence
        
        # Adjust based on score difference with next best option
        score_diff = selected_option.score - all_options[1].score
        confidence_boost = min(0.2, score_diff / 100)
        confidence += confidence_boost
        
        # Adjust based on option consensus
        if len(all_options) >= 3:
            top_3_scores = [opt.score for opt in all_options[:3]]
            score_variance = np.var(top_3_scores)
            
            # Lower confidence if scores are very close
            if score_variance < 25:
                confidence -= 0.1
        
        return min(0.99, max(0.5, confidence))
    
    async def _store_decision(self, decision_result: DecisionResult) -> None:
        """Store decision result"""



        try:
            await self.decision_storage.store_decision(decision_result)
            self.active_decisions[decision_result.decision_id] = decision_result
            self.decision_history.append(decision_result)
        except Exception as e:
            self.logger.error(f"Failed to store decision: {e}")
    
    def _update_performance_metrics(self, decision_result: DecisionResult) -> None:
        """Update decision engine performance metrics"""
        self.performance_metrics["total_decisions"] += 1
        
        # Update average confidence
        total = self.performance_metrics["total_decisions"]
        current_avg = self.performance_metrics["average_confidence"]
        new_confidence = decision_result.confidence_score
        
        self.performance_metrics["average_confidence"] = (
            (current_avg * (total - 1) + new_confidence) / total
        )
    
    def _generate_decision_id(self, decision_type: DecisionType) -> str:
        """Generate unique decision ID"""
        import hashlib
        timestamp = str(datetime.now().timestamp())
        content = f"{decision_type.value}_{timestamp}"
        return f"dec_{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    async def get_decision_status(self, decision_id: str) -> Optional[DecisionResult]:
        """Get status of a specific decision"""



        return self.active_decisions.get(decision_id)
    
    async def update_decision_status(
        self,
        decision_id: str,
        status: DecisionStatus,
        notes: Optional[str] = None
    ) -> bool:
        """Update decision execution status"""
        if decision_id in self.active_decisions:
            self.active_decisions[decision_id].status = status
            await self.decision_storage.update_decision_status(decision_id, status, notes)
            return True
        return False
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get decision engine performance metrics"""



        return self.performance_metrics.copy()
    
    async def get_decision_history(
        self,
        decision_type: Optional[DecisionType] = None,
        limit: int = 100
    ) -> List[DecisionResult]:
        """Get decision history with optional filtering"""
        history = self.decision_history
        
        if decision_type:
            history = [d for d in history if d.decision_type == decision_type]
        
        return history[-limit:]
    
    async def recommend_decision_type(
        self,
        criteria: DecisionCriteria,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DecisionType, float]]:
        """Recommend decision types based on criteria"""
        recommendations = []
        
        # Analyze criteria to recommend decision types
        if criteria.risk_level > 0.6:
            recommendations.append((DecisionType.RISK_MITIGATION, 0.9))
            recommendations.append((DecisionType.PROTECTION_STRATEGY, 0.8))
        
        if criteria.monetization_score > 70:
            recommendations.append((DecisionType.MONETIZATION_PLAN, 0.85))
            recommendations.append((DecisionType.REVENUE_STRATEGY, 0.7))
        
        if criteria.engagement_potential > 75:
            recommendations.append((DecisionType.PLATFORM_SELECTION, 0.8))
            recommendations.append((DecisionType.COLLABORATION_MATCH, 0.6))
        
        if criteria.content_quality < 70:
            recommendations.append((DecisionType.CONTENT_OPTIMIZATION, 0.9))
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
