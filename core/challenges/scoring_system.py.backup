"""📊 Scoring System - IA Influencer Agent Platform Enterprise
===========================================================
Module: backend/core/challenges/scoring_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Scoring and Ranking System - Production-Ready
Responsibility: Enterprise scoring algorithms and leaderboard management
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Performance Metrics → Score Calculation → Weighted Rankings → 
Real-time Leaderboards → Tier Classification → Reward Distribution

SCORING ARCHITECTURE:
Metric Collection → Score Algorithms → Ranking Engine → 
Leaderboard Manager → Performance Analytics → Fraud Detection
"""
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import logging
import asyncio
import math
import statistics
from abc import ABC, abstractmethod

class ScoreMetric(Enum):
    """Available scoring metrics"""
    EXPERIENCE_POINTS = "experience_points"
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT_RATE = "engagement_rate"
    COLLABORATION_COUNT = "collaboration_count"
    REVENUE_GENERATED = "revenue_generated"
    VIEWS_COUNT = "views_count"
    LIKES_COUNT = "likes_count"
    SHARES_COUNT = "shares_count"
    COMMENTS_COUNT = "comments_count"
    UPLOAD_COUNT = "upload_count"
    UPLOAD_FREQUENCY = "upload_frequency"
    AUDIENCE_GROWTH = "audience_growth"
    RETENTION_RATE = "retention_rate"
    COMPLETION_RATE = "completion_rate"
    TIME_TO_COMPLETE = "time_to_complete"
    DIFFICULTY_BONUS = "difficulty_bonus"
    STREAK_BONUS = "streak_bonus"
    COMMUNITY_IMPACT = "community_impact"
    INNOVATION_SCORE = "innovation_score"
    CONSISTENCY_SCORE = "consistency_score"

class ScoreWeight(Enum):
    """Score weight categories"""
    MINIMAL = 0.1
    LOW = 0.25
    NORMAL = 0.5
    HIGH = 0.75
    CRITICAL = 1.0
    AMPLIFIED = 1.5
    MAXIMUM = 2.0

class RankingTier(Enum):
    """User ranking tiers"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    LEGEND = "legend"

class ScoreModifier(Enum):
    """Score modifiers for special conditions"""
    EARLY_COMPLETION = "early_completion"
    PERFECT_SCORE = "perfect_score"
    FIRST_ATTEMPT = "first_attempt"
    COMEBACK_BONUS = "comeback_bonus"
    TEAM_SYNERGY = "team_synergy"
    INNOVATION_BONUS = "innovation_bonus"
    COMMUNITY_FAVORITE = "community_favorite"
    MILESTONE_ACHIEVEMENT = "milestone_achievement"
    STREAK_MAINTAINER = "streak_maintainer"
    DIFFICULTY_OVERCOMER = "difficulty_overcomer"

@dataclass
class ScoreComponent:
    """Individual score component"""
    metric: ScoreMetric
    value: Union[int, float, Decimal]
    weight: float
    max_value: Optional[Union[int, float, Decimal]] = None
    normalization_method: str = "linear"  # "linear", "logarithmic", "exponential"
    time_decay_factor: float = 1.0
    quality_threshold: float = 0.0

@dataclass
class ScoreCalculation:
    """Complete score calculation result"""
    total_score: Decimal
    weighted_score: Decimal
    normalized_score: Decimal
    percentile_rank: float
    tier: RankingTier
    components: List[Dict[str, Any]]
    modifiers: List[Dict[str, Any]]
    calculation_timestamp: datetime
    version: str = "1.0"

@dataclass
class LeaderboardEntry:
    """Leaderboard entry with comprehensive data"""
    rank: int
    user_id: str
    username: str
    total_score: Decimal
    tier: RankingTier
    score_breakdown: Dict[str, Any]
    achievements_count: int
    streak_days: int
    last_active: datetime
    rank_change: int = 0
    trend_direction: str = "stable"  # "rising", "falling", "stable"
    profile_data: Dict[str, Any] = field(default_factory=dict)

class ScoreCalculator:
    """Advanced score calculation engine"""
    
    def __init__(self):
        """Initialize score calculator with algorithms"""
        self.logger = logging.getLogger(__name__)
        
        # Score normalization ranges
        self._normalization_ranges = {
            ScoreMetric.EXPERIENCE_POINTS: (0, 100000),
            ScoreMetric.CONTENT_QUALITY: (0, 10),
            ScoreMetric.ENGAGEMENT_RATE: (0, 100),
            ScoreMetric.REVENUE_GENERATED: (0, 50000),
            ScoreMetric.VIEWS_COUNT: (0, 10000000),
            ScoreMetric.COLLABORATION_COUNT: (0, 1000),
            ScoreMetric.UPLOAD_COUNT: (0, 10000),
            ScoreMetric.COMPLETION_RATE: (0, 100)
        }
        
        # Tier thresholds (percentile-based)
        self._tier_thresholds = {
            RankingTier.BRONZE: 0.0,
            RankingTier.SILVER: 15.0,
            RankingTier.GOLD: 35.0,
            RankingTier.PLATINUM: 55.0,
            RankingTier.DIAMOND: 75.0,
            RankingTier.MASTER: 90.0,
            RankingTier.GRANDMASTER: 97.0,
            RankingTier.LEGEND: 99.5
        }
        
        # Score modifier values
        self._modifier_values = {
            ScoreModifier.EARLY_COMPLETION: 1.2,
            ScoreModifier.PERFECT_SCORE: 1.5,
            ScoreModifier.FIRST_ATTEMPT: 1.1,
            ScoreModifier.COMEBACK_BONUS: 1.3,
            ScoreModifier.TEAM_SYNERGY: 1.15,
            ScoreModifier.INNOVATION_BONUS: 1.25,
            ScoreModifier.COMMUNITY_FAVORITE: 1.4,
            ScoreModifier.MILESTONE_ACHIEVEMENT: 1.3,
            ScoreModifier.STREAK_MAINTAINER: 1.2,
            ScoreModifier.DIFFICULTY_OVERCOMER: 1.6
        }
    
    def calculate_score(self, 
                       components: List[ScoreComponent],
                       modifiers: Optional[List[ScoreModifier]] = None,
                       context: Optional[Dict[str, Any]] = None) -> ScoreCalculation:
        """Calculate comprehensive score from components"""
        try:
            total_score = Decimal('0.00')
            weighted_score = Decimal('0.00')
            component_details = []
            modifier_details = []
            
            # Calculate base score from components
            total_weight = sum(comp.weight for comp in components)
            
            for component in components:
                # Normalize component value
                normalized_value = self._normalize_value(
                    component.metric,
                    component.value,
                    component.normalization_method,
                    component.max_value
                )
                
                # Apply time decay if specified
                if component.time_decay_factor != 1.0:
                    normalized_value *= component.time_decay_factor
                
                # Apply quality threshold
                if normalized_value < component.quality_threshold:
                    normalized_value = 0
                
                # Calculate weighted contribution
                component_score = normalized_value * component.weight
                weighted_score += component_score
                
                component_details.append({
                    "metric": component.metric.value,
                    "raw_value": float(component.value),
                    "normalized_value": float(normalized_value),
                    "weight": component.weight,
                    "component_score": float(component_score),
                    "percentage_contribution": float((component_score / (weighted_score or 1)) * 100)
                })
            
            # Calculate total score
            total_score = weighted_score
            
            # Apply modifiers
            if modifiers:
                for modifier in modifiers:
                    modifier_value = self._modifier_values.get(modifier, 1.0)
                    modifier_boost = (modifier_value - 1.0) * total_score
                    total_score *= modifier_value
                    
                    modifier_details.append({
                        "modifier": modifier.value,
                        "multiplier": modifier_value,
                        "boost_amount": float(modifier_boost),
                        "description": self._get_modifier_description(modifier)
                    })
            
            # Normalize final score to 0-100 range
            normalized_score = self._normalize_final_score(total_score)
            
            # Determine tier based on percentile
            tier = self._determine_tier(normalized_score, context)
            
            # Calculate percentile rank (would require population data)
            percentile_rank = self._calculate_percentile_rank(normalized_score, context)
            
            return ScoreCalculation(
                total_score=total_score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                weighted_score=weighted_score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                normalized_score=normalized_score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                percentile_rank=percentile_rank,
                tier=tier,
                components=component_details,
                modifiers=modifier_details,
                calculation_timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Score calculation failed: {str(e)}")
            raise
    
    def _normalize_value(self, 
                        metric: ScoreMetric,
                        value: Union[int, float, Decimal],
                        method: str,
                        max_value: Optional[Union[int, float, Decimal]] = None) -> Decimal:
        """Normalize value to 0-100 range using specified method"""
        value = Decimal(str(value))
        
        # Get normalization range
        min_val, max_val = self._normalization_ranges.get(metric, (0, 100))
        if max_value:
            max_val = float(max_value)
        
        max_val = Decimal(str(max_val))
        min_val = Decimal(str(min_val))
        
        # Clamp value to range
        value = max(min_val, min(value, max_val))
        
        if method == "linear":
            return ((value - min_val) / (max_val - min_val)) * 100
        
        elif method == "logarithmic":
            if value <= 0:
                return Decimal('0')
            log_value = Decimal(str(math.log10(float(value) + 1)))
            log_max = Decimal(str(math.log10(float(max_val) + 1)))
            return (log_value / log_max) * 100
        
        elif method == "exponential":
            exp_value = value ** Decimal('0.5')  # Square root
            exp_max = max_val ** Decimal('0.5')
            return (exp_value / exp_max) * 100
        
        else:
            # Default to linear
            return ((value - min_val) / (max_val - min_val)) * 100
    
    def _normalize_final_score(self, score: Decimal) -> Decimal:
        """Normalize final score to 0-100 range"""
        # Apply sigmoid-like function for smooth distribution
        if score <= 0:
            return Decimal('0')
        
        # Use tanh normalization for better distribution
        normalized = (1 + math.tanh(float(score) / 1000 - 3)) / 2 * 100
        return Decimal(str(normalized))
    
    def _determine_tier(self, score: Decimal, context: Optional[Dict[str, Any]] = None) -> RankingTier:
        """Determine tier based on score"""
        score_float = float(score)
        
        for tier, threshold in reversed(list(self._tier_thresholds.items())):
            if score_float >= threshold:
                return tier
        
        return RankingTier.BRONZE
    
    def _calculate_percentile_rank(self, score: Decimal, context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate percentile rank (simplified without population data)"""
        # In real implementation, this would use actual population statistics
        score_float = float(score)
        
        # Rough estimation based on score distribution
        if score_float >= 95:
            return 99.5
        elif score_float >= 90:
            return 97.0
        elif score_float >= 80:
            return 90.0
        elif score_float >= 70:
            return 75.0
        elif score_float >= 60:
            return 55.0
        elif score_float >= 40:
            return 35.0
        elif score_float >= 20:
            return 15.0
        else:
            return score_float / 20 * 15
    
    def _get_modifier_description(self, modifier: ScoreModifier) -> str:
        """Get description for score modifier"""
        descriptions = {
            ScoreModifier.EARLY_COMPLETION: "Completed ahead of schedule",
            ScoreModifier.PERFECT_SCORE: "Achieved perfect performance",
            ScoreModifier.FIRST_ATTEMPT: "Succeeded on first try",
            ScoreModifier.COMEBACK_BONUS: "Made impressive comeback",
            ScoreModifier.TEAM_SYNERGY: "Excellent team collaboration",
            ScoreModifier.INNOVATION_BONUS: "Demonstrated innovation",
            ScoreModifier.COMMUNITY_FAVORITE: "Community choice winner",
            ScoreModifier.MILESTONE_ACHIEVEMENT: "Reached significant milestone",
            ScoreModifier.STREAK_MAINTAINER: "Maintained achievement streak",
            ScoreModifier.DIFFICULTY_OVERCOMER: "Overcame high difficulty"
        }
        return descriptions.get(modifier, "Special performance bonus")

class RankingEngine:
    """Advanced ranking and tier management engine"""
    
    def __init__(self, score_calculator: ScoreCalculator):
        """Initialize ranking engine"""
        self.score_calculator = score_calculator
        self.logger = logging.getLogger(__name__)
        
        # Tier promotion requirements
        self._promotion_requirements = {
            RankingTier.SILVER: {"min_score": 60, "consistency_days": 7},
            RankingTier.GOLD: {"min_score": 70, "consistency_days": 14},
            RankingTier.PLATINUM: {"min_score": 80, "consistency_days": 21},
            RankingTier.DIAMOND: {"min_score": 85, "consistency_days": 30},
            RankingTier.MASTER: {"min_score": 90, "consistency_days": 45},
            RankingTier.GRANDMASTER: {"min_score": 95, "consistency_days": 60},
            RankingTier.LEGEND: {"min_score": 98, "consistency_days": 90}
        }
        
        # Demotion protection thresholds
        self._demotion_thresholds = {
            RankingTier.SILVER: 50,
            RankingTier.GOLD: 60,
            RankingTier.PLATINUM: 70,
            RankingTier.DIAMOND: 75,
            RankingTier.MASTER: 80,
            RankingTier.GRANDMASTER: 85,
            RankingTier.LEGEND: 90
        }
    
    def calculate_user_ranking(self, 
                             user_data: Dict[str, Any],
                             historical_performance: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Calculate comprehensive user ranking"""
        try:
            # Extract score components from user data
            components = self._extract_score_components(user_data)
            
            # Determine applicable modifiers
            modifiers = self._determine_modifiers(user_data, historical_performance)
            
            # Calculate current score
            score_calculation = self.score_calculator.calculate_score(
                components, modifiers, {"user_data": user_data}
            )
            
            # Check tier eligibility
            tier_analysis = self._analyze_tier_eligibility(
                user_data, score_calculation, historical_performance
            )
            
            # Calculate trend analysis
            trend_analysis = self._calculate_trend_analysis(historical_performance)
            
            return {
                "user_id": user_data.get("user_id"),
                "current_score": score_calculation,
                "tier_analysis": tier_analysis,
                "trend_analysis": trend_analysis,
                "ranking_factors": self._get_ranking_factors(user_data),
                "improvement_suggestions": self._get_improvement_suggestions(score_calculation),
                "next_milestone": self._get_next_milestone(score_calculation.tier),
                "calculation_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"User ranking calculation failed: {str(e)}")
            raise
    
    def _extract_score_components(self, user_data: Dict[str, Any]) -> List[ScoreComponent]:
        """Extract score components from user data"""
        components = []
        
        # Experience points (high weight)
        if "experience_points" in user_data:
            components.append(ScoreComponent(
                metric=ScoreMetric.EXPERIENCE_POINTS,
                value=user_data["experience_points"],
                weight=ScoreWeight.HIGH.value,
                normalization_method="logarithmic"
            ))
        
        # Content quality (critical weight)
        if "content_quality_avg" in user_data:
            components.append(ScoreComponent(
                metric=ScoreMetric.CONTENT_QUALITY,
                value=user_data["content_quality_avg"],
                weight=ScoreWeight.CRITICAL.value,
                max_value=10
            ))
        
        # Engagement rate (high weight)
        if "engagement_rate" in user_data:
            components.append(ScoreComponent(
                metric=ScoreMetric.ENGAGEMENT_RATE,
                value=user_data["engagement_rate"],
                weight=ScoreWeight.HIGH.value,
                max_value=100
            ))
        
        # Revenue generated (high weight)
        if "revenue_generated" in user_data:
            components.append(ScoreComponent(
                metric=ScoreMetric.REVENUE_GENERATED,
                value=user_data["revenue_generated"],
                weight=ScoreWeight.HIGH.value,
                normalization_method="logarithmic"
            ))
        
        # Collaboration count (normal weight)
        if "collaboration_count" in user_data:
            components.append(ScoreComponent(
                metric=ScoreMetric.COLLABORATION_COUNT,
                value=user_data["collaboration_count"],
                weight=ScoreWeight.NORMAL.value,
                normalization_method="logarithmic"
            ))
        
        # Upload count and frequency (normal weight)
        if "upload_count" in user_data:
            components.append(ScoreComponent(
                metric=ScoreMetric.UPLOAD_COUNT,
                value=user_data["upload_count"],
                weight=ScoreWeight.NORMAL.value,
                normalization_method="logarithmic"
            ))
        
        # Consistency score (high weight)
        if "consistency_score" in user_data:
            components.append(ScoreComponent(
                metric=ScoreMetric.CONSISTENCY_SCORE,
                value=user_data["consistency_score"],
                weight=ScoreWeight.HIGH.value,
                max_value=100
            ))
        
        return components
    
    def _determine_modifiers(self, 
                           user_data: Dict[str, Any],
                           historical_performance: Optional[List[Dict[str, Any]]] = None) -> List[ScoreModifier]:
        """Determine applicable score modifiers"""
        modifiers = []
        
        # Streak bonus
        if user_data.get("current_streak", 0) >= 7:
            modifiers.append(ScoreModifier.STREAK_MAINTAINER)
        
        # Perfect score bonus
        if user_data.get("content_quality_avg", 0) >= 9.8:
            modifiers.append(ScoreModifier.PERFECT_SCORE)
        
        # Innovation bonus
        if user_data.get("innovation_score", 0) >= 8.0:
            modifiers.append(ScoreModifier.INNOVATION_BONUS)
        
        # Community favorite
        if user_data.get("community_votes", 0) >= 100:
            modifiers.append(ScoreModifier.COMMUNITY_FAVORITE)
        
        # Comeback bonus (if recovering from low performance)
        if historical_performance:
            recent_trend = self._calculate_recent_trend(historical_performance)
            if recent_trend > 0.3:  # 30% improvement
                modifiers.append(ScoreModifier.COMEBACK_BONUS)
        
        # Milestone achievement
        if user_data.get("recent_achievements", 0) >= 3:
            modifiers.append(ScoreModifier.MILESTONE_ACHIEVEMENT)
        
        return modifiers
    
    def _analyze_tier_eligibility(self, 
                                user_data: Dict[str, Any],
                                score_calculation: ScoreCalculation,
                                historical_performance: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Analyze tier promotion/demotion eligibility"""
        current_tier = score_calculation.tier
        current_score = float(score_calculation.normalized_score)
        
        # Check for promotion eligibility
        promotion_eligible = False
        promotion_target = None
        promotion_requirements = {}
        
        tier_list = list(RankingTier)
        current_tier_index = tier_list.index(current_tier)
        
        if current_tier_index < len(tier_list) - 1:
            next_tier = tier_list[current_tier_index + 1]
            requirements = self._promotion_requirements.get(next_tier, {})
            
            if current_score >= requirements.get("min_score", 100):
                # Check consistency requirement
                consistency_met = self._check_consistency_requirement(
                    user_data, requirements.get("consistency_days", 0), historical_performance
                )
                
                if consistency_met:
                    promotion_eligible = True
                    promotion_target = next_tier
                else:
                    promotion_requirements = {
                        "consistency_days_remaining": requirements.get("consistency_days", 0) - 
                                                    user_data.get("consistency_days", 0)
                    }
            else:
                promotion_requirements = {
                    "score_needed": requirements.get("min_score", 100) - current_score
                }
        
        # Check for demotion risk
        demotion_risk = False
        demotion_threshold = self._demotion_thresholds.get(current_tier, 0)
        
        if current_score < demotion_threshold:
            demotion_risk = True
        
        return {
            "current_tier": current_tier.value,
            "promotion_eligible": promotion_eligible,
            "promotion_target": promotion_target.value if promotion_target else None,
            "promotion_requirements": promotion_requirements,
            "demotion_risk": demotion_risk,
            "demotion_threshold": demotion_threshold,
            "score_buffer": current_score - demotion_threshold
        }
    
    def _calculate_trend_analysis(self, 
                                historical_performance: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Calculate performance trend analysis"""
        if not historical_performance or len(historical_performance) < 2:
            return {
                "trend_direction": "stable",
                "trend_strength": 0.0,
                "momentum": "neutral",
                "prediction": "insufficient_data"
            }
        
        # Extract scores from historical data
        scores = [p.get("score", 0) for p in historical_performance[-30:]]  # Last 30 data points
        
        if len(scores) < 2:
            return {"trend_direction": "stable", "trend_strength": 0.0}
        
        # Calculate trend using linear regression
        trend_strength = self._calculate_linear_trend(scores)
        
        # Determine trend direction
        if trend_strength > 0.1:
            trend_direction = "rising"
            momentum = "positive"
        elif trend_strength < -0.1:
            trend_direction = "falling"
            momentum = "negative"
        else:
            trend_direction = "stable"
            momentum = "neutral"
        
        # Calculate volatility
        volatility = statistics.stdev(scores) if len(scores) > 1 else 0
        
        # Make prediction
        prediction = self._predict_future_performance(scores, trend_strength)
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "momentum": momentum,
            "volatility": volatility,
            "prediction": prediction,
            "data_points": len(scores)
        }
    
    def _calculate_linear_trend(self, scores: List[float]) -> float:
        """Calculate linear trend coefficient"""
        if len(scores) < 2:
            return 0.0
        
        n = len(scores)
        x_values = list(range(n))
        
        # Calculate linear regression slope
        x_mean = sum(x_values) / n
        y_mean = sum(scores) / n
        
        numerator = sum((x_values[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _get_ranking_factors(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get factors contributing to user ranking"""
        factors = []
        
        # Top contributing factors
        if user_data.get("content_quality_avg", 0) >= 8.0:
            factors.append({
                "factor": "High Content Quality",
                "impact": "positive",
                "strength": "high",
                "value": user_data.get("content_quality_avg", 0)
            })
        
        if user_data.get("engagement_rate", 0) >= 15.0:
            factors.append({
                "factor": "Strong Engagement",
                "impact": "positive",
                "strength": "high",
                "value": user_data.get("engagement_rate", 0)
            })
        
        if user_data.get("consistency_score", 0) >= 80.0:
            factors.append({
                "factor": "Consistent Performance",
                "impact": "positive",
                "strength": "medium",
                "value": user_data.get("consistency_score", 0)
            })
        
        # Areas for improvement
        if user_data.get("collaboration_count", 0) < 5:
            factors.append({
                "factor": "Limited Collaborations",
                "impact": "negative",
                "strength": "medium",
                "value": user_data.get("collaboration_count", 0)
            })
        
        return factors
    
    def _get_improvement_suggestions(self, score_calculation: ScoreCalculation) -> List[str]:
        """Get personalized improvement suggestions"""
        suggestions = []
        
        # Analyze component contributions
        components = score_calculation.components
        sorted_components = sorted(components, key=lambda x: x["percentage_contribution"])
        
        # Suggest improvements for lowest contributing components
        lowest_components = sorted_components[:3]
        
        for component in lowest_components:
            metric = component["metric"]
            
            if metric == "content_quality":
                suggestions.append("Focus on improving content quality through better storytelling and production values")
            elif metric == "engagement_rate":
                suggestions.append("Increase audience engagement by responding to comments and creating interactive content")
            elif metric == "collaboration_count":
                suggestions.append("Seek more collaboration opportunities to expand your network and audience")
            elif metric == "consistency_score":
                suggestions.append("Maintain a regular posting schedule to improve consistency")
            elif metric == "revenue_generated":
                suggestions.append("Explore monetization strategies like sponsorships and merchandise")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _get_next_milestone(self, current_tier: RankingTier) -> Dict[str, Any]:
        """Get next milestone information"""
        tier_list = list(RankingTier)
        current_index = tier_list.index(current_tier)
        
        if current_index < len(tier_list) - 1:
            next_tier = tier_list[current_index + 1]
            requirements = self._promotion_requirements.get(next_tier, {})
            
            return {
                "target_tier": next_tier.value,
                "requirements": requirements,
                "estimated_time": f"{requirements.get('consistency_days', 0)} days",
                "benefits": self._get_tier_benefits(next_tier)
            }
        
        return {
            "target_tier": "max_tier_reached",
            "message": "You've reached the highest tier! Focus on maintaining your legend status."
        }
    
    def _get_tier_benefits(self, tier: RankingTier) -> List[str]:
        """Get benefits for reaching specific tier"""
        benefits = {
            RankingTier.SILVER: ["Increased visibility", "Basic analytics access"],
            RankingTier.GOLD: ["Premium features access", "Priority support"],
            RankingTier.PLATINUM: ["Advanced analytics", "Collaboration matching"],
            RankingTier.DIAMOND: ["Revenue sharing boost", "Featured placement"],
            RankingTier.MASTER: ["Beta features access", "Mentorship opportunities"],
            RankingTier.GRANDMASTER: ["VIP support", "Exclusive events"],
            RankingTier.LEGEND: ["Ultimate recognition", "Maximum benefits"]
        }
        return benefits.get(tier, ["Exclusive benefits"])

class LeaderboardManager:
    """Enterprise leaderboard management system"""
    
    def __init__(self, ranking_engine: RankingEngine):
        """Initialize leaderboard manager"""
        self.ranking_engine = ranking_engine
        self.logger = logging.getLogger(__name__)
        
        # Leaderboard update frequencies
        self._update_frequencies = {
            "real_time": timedelta(minutes=1),
            "frequent": timedelta(minutes=5),
            "normal": timedelta(minutes=15),
            "periodic": timedelta(hours=1),
            "daily": timedelta(hours=24)
        }
    
    async def generate_leaderboard(self, 
                                 users_data: List[Dict[str, Any]],
                                 leaderboard_type: str = "global",
                                 limit: int = 100,
                                 include_trends: bool = True) -> List[LeaderboardEntry]:
        """Generate comprehensive leaderboard"""
        try:
            # Calculate rankings for all users
            ranked_users = []
            
            for user_data in users_data:
                try:
                    ranking_result = self.ranking_engine.calculate_user_ranking(user_data)
                    score_calc = ranking_result["current_score"]
                    trend_analysis = ranking_result.get("trend_analysis", {})
                    
                    ranked_users.append({
                        "user_id": user_data.get("user_id"),
                        "username": user_data.get("username", "Unknown"),
                        "total_score": score_calc.normalized_score,
                        "tier": score_calc.tier,
                        "score_breakdown": {
                            "components": score_calc.components,
                            "modifiers": score_calc.modifiers
                        },
                        "achievements_count": user_data.get("achievements_count", 0),
                        "streak_days": user_data.get("current_streak", 0),
                        "last_active": user_data.get("last_active", datetime.now(timezone.utc)),
                        "trend_direction": trend_analysis.get("trend_direction", "stable"),
                        "profile_data": {
                            "avatar_url": user_data.get("avatar_url"),
                            "country": user_data.get("country"),
                            "verified": user_data.get("verified", False)
                        }
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to rank user {user_data.get('user_id')}: {str(e)}")
                    continue
            
            # Sort by total score (descending)
            ranked_users.sort(key=lambda x: x["total_score"], reverse=True)
            
            # Create leaderboard entries with ranks
            leaderboard = []
            for i, user_data in enumerate(ranked_users[:limit]):
                # Calculate rank change (would need historical data)
                rank_change = self._calculate_rank_change(user_data, i + 1)
                
                entry = LeaderboardEntry(
                    rank=i + 1,
                    user_id=user_data["user_id"],
                    username=user_data["username"],
                    total_score=user_data["total_score"],
                    tier=user_data["tier"],
                    score_breakdown=user_data["score_breakdown"],
                    achievements_count=user_data["achievements_count"],
                    streak_days=user_data["streak_days"],
                    last_active=user_data["last_active"],
                    rank_change=rank_change,
                    trend_direction=user_data["trend_direction"],
                    profile_data=user_data["profile_data"]
                )
                
                leaderboard.append(entry)
            
            return leaderboard
            
        except Exception as e:
            self.logger.error(f"Leaderboard generation failed: {str(e)}")
            raise
    
    def _calculate_rank_change(self, user_data: Dict[str, Any], current_rank: int) -> int:
        """Calculate rank change from previous period"""
        # In real implementation, this would compare with historical leaderboard data
        # For now, return a placeholder calculation
        trend_direction = user_data.get("trend_direction", "stable")
        
        if trend_direction == "rising":
            return 5  # Moved up 5 positions
        elif trend_direction == "falling":
            return -3  # Moved down 3 positions
        else:
            return 0  # No change

class ScoringSystem:
    """Main scoring system orchestrator"""
    
    def __init__(self,
                 analytics_service=None,
                 user_service=None,
                 cache_service=None,
                 notification_service=None):
        """Initialize scoring system"""
        self.analytics_service = analytics_service
        self.user_service = user_service
        self.cache_service = cache_service
        self.notification_service = notification_service
        
        # Initialize components
        self.score_calculator = ScoreCalculator()
        self.ranking_engine = RankingEngine(self.score_calculator)
        self.leaderboard_manager = LeaderboardManager(self.ranking_engine)
        
        self.logger = logging.getLogger(__name__)
    
    async def calculate_user_score(self, user_id: str) -> Dict[str, Any]:
        """Calculate comprehensive user score"""
        try:
            # Get user data
            user_data = await self._get_user_data(user_id)
            if not user_data:
                return {"success": False, "error": "User not found"}
            
            # Get historical performance
            historical_data = await self._get_historical_performance(user_id)
            
            # Calculate ranking
            ranking_result = self.ranking_engine.calculate_user_ranking(
                user_data, historical_data
            )
            
            # Cache result
            if self.cache_service:
                await self.cache_service.set(
                    f"user_score_{user_id}",
                    ranking_result,
                    ttl=300  # 5 minutes
                )
            
            return {
                "success": True,
                "user_id": user_id,
                "ranking": ranking_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate user score: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_global_leaderboard(self, limit: int = 100) -> Dict[str, Any]:
        """Generate global leaderboard"""
        try:
            # Get top users data
            users_data = await self._get_top_users_data(limit * 2)  # Get more for filtering
            
            # Generate leaderboard
            leaderboard = await self.leaderboard_manager.generate_leaderboard(
                users_data, "global", limit
            )
            
            # Cache leaderboard
            if self.cache_service:
                await self.cache_service.set(
                    "global_leaderboard",
                    [entry.__dict__ for entry in leaderboard],
                    ttl=900  # 15 minutes
                )
            
            return {
                "success": True,
                "leaderboard": [entry.__dict__ for entry in leaderboard],
                "total_entries": len(leaderboard),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate global leaderboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive user data for scoring"""
        if self.user_service:
            try:
                return await self.user_service.get_user_scoring_data(user_id)
            except Exception as e:
                self.logger.warning(f"Failed to get user data from service: {str(e)}")
        
        # Fallback mock data
        return {
            "user_id": user_id,
            "username": f"user_{user_id}",
            "experience_points": 1500,
            "content_quality_avg": 7.5,
            "engagement_rate": 12.5,
            "revenue_generated": 2500,
            "collaboration_count": 8,
            "upload_count": 45,
            "consistency_score": 75,
            "current_streak": 5,
            "achievements_count": 12
        }
    
    async def _get_historical_performance(self, user_id: str) -> List[Dict[str, Any]]:
        """Get historical performance data"""
        if self.analytics_service:
            try:
                return await self.analytics_service.get_user_performance_history(user_id)
            except Exception as e:
                self.logger.warning(f"Failed to get historical data: {str(e)}")
        
        # Return empty list as fallback
        return []
    
    async def _get_top_users_data(self, limit: int) -> List[Dict[str, Any]]:
        """Get data for top users"""
        if self.user_service:
            try:
                return await self.user_service.get_top_users_data(limit)
            except Exception as e:
                self.logger.warning(f"Failed to get top users data: {str(e)}")
        
        # Fallback mock data
        return [
            await self._get_user_data(f"user_{i}")
            for i in range(1, limit + 1)
        ]