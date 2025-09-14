"""
Ainflue Platform - Reputation Impact Analyzer
=============================================

Enterprise-grade reputation impact analysis for collaboration partnerships,
brand reputation tracking, influence measurement, and reputation risk assessment.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
import uuid
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReputationMetric(Enum):
    """Types of reputation metrics."""
    TRUST_SCORE = "trust_score"
    BRAND_SENTIMENT = "brand_sentiment"
    COLLABORATION_SUCCESS_RATE = "collaboration_success_rate"
    AUDIENCE_PERCEPTION = "audience_perception"
    INDUSTRY_STANDING = "industry_standing"
    CONTENT_QUALITY_REPUTATION = "content_quality_reputation"
    RELIABILITY_SCORE = "reliability_score"
    PROFESSIONALISM_RATING = "professionalism_rating"

class ImpactLevel(Enum):
    """Impact levels for reputation changes."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class ReputationRisk(Enum):
    """Reputation risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SentimentSource(Enum):
    """Sources of sentiment data."""
    SOCIAL_MEDIA = "social_media"
    COLLABORATION_FEEDBACK = "collaboration_feedback"
    AUDIENCE_REVIEWS = "audience_reviews"
    INDUSTRY_FEEDBACK = "industry_feedback"
    PEER_REVIEWS = "peer_reviews"
    BRAND_MENTIONS = "brand_mentions"

@dataclass
class ReputationEvent:
    """Individual reputation event."""
    event_id: str
    creator_id: str
    event_type: str
    description: str
    impact_level: ImpactLevel
    affected_metrics: List[ReputationMetric]
    timestamp: datetime
    source: SentimentSource
    collaboration_id: Optional[str] = None
    quantitative_impact: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReputationScore:
    """Reputation score for a creator."""
    creator_id: str
    overall_score: float
    metric_scores: Dict[ReputationMetric, float]
    last_updated: datetime
    trend_direction: str  # improving, declining, stable
    risk_level: ReputationRisk
    confidence_level: float
    historical_data: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class CollaborationImpact:
    """Impact of collaboration on reputation."""
    collaboration_id: str
    participants: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    pre_collaboration_scores: Dict[str, float]
    post_collaboration_scores: Dict[str, float]
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    mutual_benefit_score: float = 0.0

@dataclass
class ReputationAlert:
    """Reputation alert for significant changes."""
    alert_id: str
    creator_id: str
    alert_type: str
    severity: ReputationRisk
    message: str
    triggered_at: datetime
    metrics_affected: List[ReputationMetric]
    recommended_actions: List[str] = field(default_factory=list)
    resolved: bool = False

class ReputationImpactAnalyzer:
    """
    Advanced reputation impact analysis system for collaboration partnerships.
    
    Features:
    - Multi-dimensional reputation tracking
    - Collaboration impact assessment
    - Brand sentiment analysis
    - Reputation risk monitoring
    - Influence measurement
    - Peer comparison analysis
    - Reputation recovery recommendations
    - Real-time reputation alerts
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize reputation impact analyzer."""
        self.config = config or {}
        self.reputation_scores: Dict[str, ReputationScore] = {}
        self.reputation_events: List[ReputationEvent] = []
        self.collaboration_impacts: Dict[str, CollaborationImpact] = {}
        self.active_alerts: List[ReputationAlert] = []
        
        # Reputation calculation weights
        self.metric_weights = {
            ReputationMetric.TRUST_SCORE: 0.25,
            ReputationMetric.BRAND_SENTIMENT: 0.20,
            ReputationMetric.COLLABORATION_SUCCESS_RATE: 0.15,
            ReputationMetric.AUDIENCE_PERCEPTION: 0.15,
            ReputationMetric.INDUSTRY_STANDING: 0.10,
            ReputationMetric.CONTENT_QUALITY_REPUTATION: 0.10,
            ReputationMetric.RELIABILITY_SCORE: 0.03,
            ReputationMetric.PROFESSIONALISM_RATING: 0.02
        }
        
        # Risk thresholds
        self.risk_thresholds = {
            ReputationRisk.LOW: 0.8,
            ReputationRisk.MEDIUM: 0.6,
            ReputationRisk.HIGH: 0.4,
            ReputationRisk.CRITICAL: 0.2
        }
        
        # Sentiment analysis configuration
        self.sentiment_config = {
            "positive_keywords": ["excellent", "amazing", "professional", "reliable", "talented", "creative"],
            "negative_keywords": ["unreliable", "unprofessional", "poor", "disappointing", "problematic"],
            "neutral_threshold": 0.1
        }
        
        logger.info("📊 Reputation Impact Analyzer initialized")
        self._initialize_baseline_scores()
    
    def _initialize_baseline_scores(self) -> None:
        """Initialize baseline reputation scoring system."""
        self.baseline_scores = {
            ReputationMetric.TRUST_SCORE: 0.75,
            ReputationMetric.BRAND_SENTIMENT: 0.70,
            ReputationMetric.COLLABORATION_SUCCESS_RATE: 0.80,
            ReputationMetric.AUDIENCE_PERCEPTION: 0.75,
            ReputationMetric.INDUSTRY_STANDING: 0.70,
            ReputationMetric.CONTENT_QUALITY_REPUTATION: 0.80,
            ReputationMetric.RELIABILITY_SCORE: 0.85,
            ReputationMetric.PROFESSIONALISM_RATING: 0.80
        }
    
    def initialize_creator_reputation(
        self,
        creator_id: str,
        initial_metrics: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Initialize reputation tracking for a creator.
        
        Args:
            creator_id: Creator identifier
            initial_metrics: Initial metric values
            
        Returns:
            Status message
        """
        if creator_id in self.reputation_scores:
            return f"Reputation tracking already exists for {creator_id}"
        
        # Use provided metrics or baseline scores
        metric_scores = {}
        for metric in ReputationMetric:
            if initial_metrics and metric.value in initial_metrics:
                metric_scores[metric] = initial_metrics[metric.value]
            else:
                metric_scores[metric] = self.baseline_scores[metric]
        
        # Calculate overall score
        overall_score = sum(
            score * self.metric_weights[metric]
            for metric, score in metric_scores.items()
        )
        
        # Determine risk level
        risk_level = self._calculate_risk_level(overall_score)
        
        reputation_score = ReputationScore(
            creator_id=creator_id,
            overall_score=overall_score,
            metric_scores=metric_scores,
            last_updated=datetime.utcnow(),
            trend_direction="stable",
            risk_level=risk_level,
            confidence_level=0.7  # Medium confidence for new creators
        )
        
        self.reputation_scores[creator_id] = reputation_score
        logger.info(f"📊 Initialized reputation tracking for {creator_id} (score: {overall_score:.3f})")
        return f"Reputation tracking initialized for {creator_id}"
    
    def _calculate_risk_level(self, overall_score: float) -> ReputationRisk:
        """Calculate reputation risk level based on overall score."""
        if overall_score >= self.risk_thresholds[ReputationRisk.LOW]:
            return ReputationRisk.LOW
        elif overall_score >= self.risk_thresholds[ReputationRisk.MEDIUM]:
            return ReputationRisk.MEDIUM
        elif overall_score >= self.risk_thresholds[ReputationRisk.HIGH]:
            return ReputationRisk.HIGH
        else:
            return ReputationRisk.CRITICAL
    
    def record_reputation_event(
        self,
        creator_id: str,
        event_type: str,
        description: str,
        impact_level: str,
        source: str,
        affected_metrics: List[str],
        collaboration_id: Optional[str] = None,
        quantitative_impact: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a reputation-affecting event.
        
        Args:
            creator_id: Creator identifier
            event_type: Type of event
            description: Event description
            impact_level: Impact level (very_positive, positive, neutral, negative, very_negative)
            source: Source of the event
            affected_metrics: List of affected reputation metrics
            collaboration_id: Optional collaboration ID
            quantitative_impact: Quantitative impact values
            metadata: Additional metadata
            
        Returns:
            Event ID
        """
        event_id = f"event_{creator_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Convert string enums
        try:
            impact_enum = ImpactLevel(impact_level)
            source_enum = SentimentSource(source)
            metric_enums = [ReputationMetric(metric) for metric in affected_metrics]
        except ValueError as e:
            logger.error(f"Invalid enum value: {e}")
            raise
        
        event = ReputationEvent(
            event_id=event_id,
            creator_id=creator_id,
            event_type=event_type,
            description=description,
            impact_level=impact_enum,
            affected_metrics=metric_enums,
            timestamp=datetime.utcnow(),
            source=source_enum,
            collaboration_id=collaboration_id,
            quantitative_impact=quantitative_impact or {},
            metadata=metadata or {}
        )
        
        self.reputation_events.append(event)
        
        # Apply impact to reputation scores
        self._apply_event_impact(event)
        
        logger.info(f"📊 Recorded reputation event: {event_id} ({impact_level}) for {creator_id}")
        return event_id
    
    def _apply_event_impact(self, event -> None: ReputationEvent) -> None:
        """Apply reputation event impact to creator scores."""
        if event.creator_id not in self.reputation_scores:
            logger.warning(f"Creator {event.creator_id} not found in reputation tracking")
            return
        
        reputation = self.reputation_scores[event.creator_id]
        
        # Calculate impact multiplier based on impact level
        impact_multipliers = {
            ImpactLevel.VERY_POSITIVE: 0.15,
            ImpactLevel.POSITIVE: 0.08,
            ImpactLevel.NEUTRAL: 0.0,
            ImpactLevel.NEGATIVE: -0.05,
            ImpactLevel.VERY_NEGATIVE: -0.12
        }
        
        base_impact = impact_multipliers[event.impact_level]
        
        # Apply impact to affected metrics
        for metric in event.affected_metrics:
            if metric in reputation.metric_scores:
                # Use quantitative impact if provided, otherwise use base impact
                if metric.value in event.quantitative_impact:
                    impact = event.quantitative_impact[metric.value]
                else:
                    impact = base_impact
                
                # Apply impact with bounds checking
                old_score = reputation.metric_scores[metric]
                new_score = max(0.0, min(1.0, old_score + impact))
                reputation.metric_scores[metric] = new_score
                
                logger.debug(f"Updated {metric.value} for {event.creator_id}: {old_score:.3f} -> {new_score:.3f}")
        
        # Recalculate overall score
        self._recalculate_overall_score(reputation)
        
        # Update trend and risk level
        self._update_reputation_trend(reputation)
        
        # Check for alerts
        self._check_reputation_alerts(reputation, event)
    
    def _recalculate_overall_score(self, reputation -> None: ReputationScore) -> None:
        """Recalculate overall reputation score."""
        old_score = reputation.overall_score
        
        new_score = sum(
            score * self.metric_weights[metric]
            for metric, score in reputation.metric_scores.items()
        )
        
        reputation.overall_score = new_score
        reputation.last_updated = datetime.utcnow()
        
        # Store historical data
        reputation.historical_data.append({
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": new_score,
            "metric_scores": {metric.value: score for metric, score in reputation.metric_scores.items()}
        })
        
        # Keep only last 100 historical records
        if len(reputation.historical_data) > 100:
            reputation.historical_data = reputation.historical_data[-100:]
        
        # Update risk level
        reputation.risk_level = self._calculate_risk_level(new_score)
        
        logger.debug(f"Updated overall score for {reputation.creator_id}: {old_score:.3f} -> {new_score:.3f}")
    
    def _update_reputation_trend(self, reputation -> None: ReputationScore) -> None:
        """Update reputation trend direction."""
        if len(reputation.historical_data) < 2:
            reputation.trend_direction = "stable"
            return
        
        # Compare recent scores to determine trend
        recent_scores = [entry["overall_score"] for entry in reputation.historical_data[-5:]]
        
        if len(recent_scores) >= 2:
            # Calculate trend using linear regression or simple comparison
            if recent_scores[-1] > recent_scores[0] * 1.02:  # 2% improvement
                reputation.trend_direction = "improving"
            elif recent_scores[-1] < recent_scores[0] * 0.98:  # 2% decline
                reputation.trend_direction = "declining"
            else:
                reputation.trend_direction = "stable"
        
        # Update confidence level based on data availability
        data_points = len(reputation.historical_data)
        reputation.confidence_level = min(1.0, 0.5 + (data_points / 20) * 0.5)
    
    def _check_reputation_alerts(self, reputation -> None: ReputationScore, event -> None: ReputationEvent) -> None:
        """Check if reputation changes warrant alerts."""
        alerts_to_create = []
        
        # Critical reputation drop
        if reputation.overall_score < 0.3:
            alerts_to_create.append({
                "type": "critical_reputation_drop",
                "severity": ReputationRisk.CRITICAL,
                "message": f"Critical reputation drop detected (score: {reputation.overall_score:.3f})",
                "recommendations": [
                    "Immediately review recent activities",
                    "Engage with community to address concerns",
                    "Consider reputation recovery strategy"
                ]
            })
        
        # Sudden negative change
        if len(reputation.historical_data) >= 2:
            score_change = reputation.overall_score - reputation.historical_data[-2]["overall_score"]
            if score_change < -0.1:  # 10% drop
                alerts_to_create.append({
                    "type": "sudden_reputation_decline",
                    "severity": ReputationRisk.HIGH,
                    "message": f"Sudden reputation decline detected (change: {score_change:.3f})",
                    "recommendations": [
                        "Investigate cause of reputation decline",
                        "Address any ongoing issues",
                        "Monitor sentiment closely"
                    ]
                })
        
        # Risk level increase
        if reputation.risk_level in [ReputationRisk.HIGH, ReputationRisk.CRITICAL]:
            alerts_to_create.append({
                "type": "reputation_risk_elevated",
                "severity": reputation.risk_level,
                "message": f"Reputation risk elevated to {reputation.risk_level.value}",
                "recommendations": [
                    "Review recent collaborations and activities",
                    "Implement reputation management strategy",
                    "Monitor feedback and sentiment"
                ]
            })
        
        # Create alerts
        for alert_data in alerts_to_create:
            alert_id = f"alert_{reputation.creator_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            alert = ReputationAlert(
                alert_id=alert_id,
                creator_id=reputation.creator_id,
                alert_type=alert_data["type"],
                severity=alert_data["severity"],
                message=alert_data["message"],
                triggered_at=datetime.utcnow(),
                metrics_affected=event.affected_metrics,
                recommended_actions=alert_data["recommendations"]
            )
            
            self.active_alerts.append(alert)
            logger.warning(f"🚨 Reputation alert created: {alert_id} - {alert.message}")
    
    async def analyze_collaboration_impact(
        self,
        collaboration_id: str,
        participants: List[str],
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analyze reputation impact of a collaboration.
        
        Args:
            collaboration_id: Collaboration identifier
            participants: List of participant creator IDs
            start_date: Collaboration start date
            end_date: Collaboration end date (None if ongoing)
            
        Returns:
            Collaboration impact analysis
        """
        try:
            # Get pre-collaboration scores
            pre_scores = {}
            for creator_id in participants:
                if creator_id in self.reputation_scores:
                    # Find historical score closest to start date
                    reputation = self.reputation_scores[creator_id]
                    pre_score = self._get_historical_score(reputation, start_date)
                    pre_scores[creator_id] = pre_score
                else:
                    logger.warning(f"No reputation data for {creator_id}")
                    pre_scores[creator_id] = 0.75  # Default score
            
            # Get current/post-collaboration scores
            post_scores = {}
            for creator_id in participants:
                if creator_id in self.reputation_scores:
                    if end_date:
                        # Get historical score closest to end date
                        reputation = self.reputation_scores[creator_id]
                        post_score = self._get_historical_score(reputation, end_date)
                    else:
                        # Use current score for ongoing collaborations
                        post_score = self.reputation_scores[creator_id].overall_score
                    post_scores[creator_id] = post_score
                else:
                    post_scores[creator_id] = 0.75  # Default score
            
            # Calculate impact metrics
            impact_analysis = await self._calculate_collaboration_impact_metrics(
                collaboration_id, participants, pre_scores, post_scores, start_date, end_date
            )
            
            # Create collaboration impact record
            collaboration_impact = CollaborationImpact(
                collaboration_id=collaboration_id,
                participants=participants,
                start_date=start_date,
                end_date=end_date,
                pre_collaboration_scores=pre_scores,
                post_collaboration_scores=post_scores,
                impact_analysis=impact_analysis,
                mutual_benefit_score=impact_analysis.get("mutual_benefit_score", 0.0)
            )
            
            self.collaboration_impacts[collaboration_id] = collaboration_impact
            
            logger.info(f"📊 Analyzed collaboration impact: {collaboration_id}")
            return impact_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing collaboration impact: {e}")
            return {"error": str(e)}
    
    def _get_historical_score(self, reputation: ReputationScore, target_date: datetime) -> float:
        """Get historical reputation score closest to target date."""
        if not reputation.historical_data:
            return reputation.overall_score
        
        # Find the historical entry closest to target date
        closest_entry = None
        min_time_diff = float('inf')
        
        for entry in reputation.historical_data:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            time_diff = abs((entry_date - target_date).total_seconds())
            
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_entry = entry
        
        return closest_entry["overall_score"] if closest_entry else reputation.overall_score
    
    async def _calculate_collaboration_impact_metrics(
        self,
        collaboration_id: str,
        participants: List[str],
        pre_scores: Dict[str, float],
        post_scores: Dict[str, float],
        start_date: datetime,
        end_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Calculate detailed collaboration impact metrics."""
        impact_metrics = {}
        
        # Individual impact analysis
        individual_impacts = {}
        total_positive_impact = 0
        total_negative_impact = 0
        
        for creator_id in participants:
            pre_score = pre_scores.get(creator_id, 0.75)
            post_score = post_scores.get(creator_id, 0.75)
            
            impact = post_score - pre_score
            impact_percentage = (impact / pre_score * 100) if pre_score > 0 else 0
            
            individual_impacts[creator_id] = {
                "pre_score": pre_score,
                "post_score": post_score,
                "absolute_impact": impact,
                "percentage_impact": impact_percentage,
                "impact_category": self._categorize_impact(impact)
            }
            
            if impact > 0:
                total_positive_impact += impact
            else:
                total_negative_impact += abs(impact)
        
        # Calculate mutual benefit score
        positive_participants = sum(1 for impact in individual_impacts.values() if impact["absolute_impact"] > 0)
        mutual_benefit_score = positive_participants / len(participants) if participants else 0
        
        # Network effect analysis
        network_effect = await self._analyze_network_effect(collaboration_id, participants, individual_impacts)
        
        # Risk assessment
        risk_assessment = self._assess_collaboration_risk(individual_impacts)
        
        impact_metrics = {
            "collaboration_id": collaboration_id,
            "analysis_date": datetime.utcnow().isoformat(),
            "duration_days": (datetime.utcnow() - start_date).days if not end_date else (end_date - start_date).days,
            "participant_count": len(participants),
            "individual_impacts": individual_impacts,
            "aggregate_metrics": {
                "total_positive_impact": total_positive_impact,
                "total_negative_impact": total_negative_impact,
                "net_impact": total_positive_impact - total_negative_impact,
                "average_impact": sum(impact["absolute_impact"] for impact in individual_impacts.values()) / len(participants),
                "mutual_benefit_score": mutual_benefit_score
            },
            "network_effect": network_effect,
            "risk_assessment": risk_assessment,
            "success_indicators": self._identify_success_indicators(individual_impacts, network_effect),
            "recommendations": self._generate_collaboration_recommendations(individual_impacts, network_effect, risk_assessment)
        }
        
        return impact_metrics
    
    def _categorize_impact(self, impact: float) -> str:
        """Categorize impact level."""
        if impact >= 0.1:
            return "significant_positive"
        elif impact >= 0.05:
            return "moderate_positive"
        elif impact >= 0.01:
            return "slight_positive"
        elif impact >= -0.01:
            return "neutral"
        elif impact >= -0.05:
            return "slight_negative"
        elif impact >= -0.1:
            return "moderate_negative"
        else:
            return "significant_negative"
    
    async def _analyze_network_effect(
        self,
        collaboration_id: str,
        participants: List[str],
        individual_impacts: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze network effects of the collaboration."""
        network_metrics = {
            "cross_pollination_effect": 0.0,
            "reputation_spillover": 0.0,
            "network_strength": 0.0,
            "influence_distribution": {}
        }
        
        # Calculate cross-pollination effect (how participants benefit from each other)
        positive_impacts = [impact["absolute_impact"] for impact in individual_impacts.values() if impact["absolute_impact"] > 0]
        if positive_impacts:
            network_metrics["cross_pollination_effect"] = statistics.mean(positive_impacts)
        
        # Calculate reputation spillover
        score_variances = [impact["absolute_impact"] for impact in individual_impacts.values()]
        if score_variances:
            network_metrics["reputation_spillover"] = statistics.stdev(score_variances) if len(score_variances) > 1 else 0
        
        # Network strength (how well participants complement each other)
        pre_scores = [impact["pre_score"] for impact in individual_impacts.values()]
        post_scores = [impact["post_score"] for impact in individual_impacts.values()]
        
        if pre_scores and post_scores:
            pre_avg = statistics.mean(pre_scores)
            post_avg = statistics.mean(post_scores)
            network_metrics["network_strength"] = post_avg - pre_avg
        
        # Influence distribution (who influenced whom the most)
        for creator_id, impact_data in individual_impacts.items():
            influence_score = max(0, impact_data["absolute_impact"]) * impact_data["pre_score"]
            network_metrics["influence_distribution"][creator_id] = influence_score
        
        return network_metrics
    
    def _assess_collaboration_risk(self, individual_impacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Assess risks associated with the collaboration."""
        risk_factors = []
        risk_score = 0.0
        
        # Check for participants with negative impact
        negative_impacts = [impact for impact in individual_impacts.values() if impact["absolute_impact"] < -0.05]
        if negative_impacts:
            risk_factors.append("significant_negative_impact_on_participants")
            risk_score += 0.3
        
        # Check for uneven benefit distribution
        impacts = [impact["absolute_impact"] for impact in individual_impacts.values()]
        if impacts and statistics.stdev(impacts) > 0.1:
            risk_factors.append("uneven_benefit_distribution")
            risk_score += 0.2
        
        # Check for overall negative trend
        total_impact = sum(impacts)
        if total_impact < -0.05:
            risk_factors.append("overall_negative_reputation_impact")
            risk_score += 0.4
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_recommendations": self._generate_risk_mitigation_recommendations(risk_factors)
        }
    
    def _generate_risk_mitigation_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if "significant_negative_impact_on_participants" in risk_factors:
            recommendations.extend([
                "Monitor affected participants closely",
                "Implement reputation recovery strategies",
                "Consider adjusting collaboration terms"
            ])
        
        if "uneven_benefit_distribution" in risk_factors:
            recommendations.extend([
                "Rebalance collaboration benefits",
                "Ensure fair exposure for all participants",
                "Review revenue sharing agreements"
            ])
        
        if "overall_negative_reputation_impact" in risk_factors:
            recommendations.extend([
                "Conduct immediate damage assessment",
                "Implement crisis communication strategy",
                "Consider collaboration termination if necessary"
            ])
        
        return recommendations
    
    def _identify_success_indicators(
        self,
        individual_impacts: Dict[str, Dict[str, Any]],
        network_effect: Dict[str, Any]
    ) -> List[str]:
        """Identify success indicators from the collaboration."""
        success_indicators = []
        
        # All participants benefit
        if all(impact["absolute_impact"] >= 0 for impact in individual_impacts.values()):
            success_indicators.append("universal_positive_impact")
        
        # Strong network effect
        if network_effect["cross_pollination_effect"] > 0.05:
            success_indicators.append("strong_cross_pollination")
        
        # Balanced benefits
        impacts = [impact["absolute_impact"] for impact in individual_impacts.values()]
        if impacts and statistics.stdev(impacts) < 0.03:
            success_indicators.append("balanced_benefit_distribution")
        
        # Significant improvement for any participant
        if any(impact["absolute_impact"] > 0.1 for impact in individual_impacts.values()):
            success_indicators.append("significant_individual_improvement")
        
        return success_indicators
    
    def _generate_collaboration_recommendations(
        self,
        individual_impacts: Dict[str, Dict[str, Any]],
        network_effect: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on collaboration analysis."""
        recommendations = []
        
        # Based on risk level
        if risk_assessment["risk_level"] == "high":
            recommendations.extend([
                "Implement immediate risk mitigation strategies",
                "Monitor reputation metrics closely",
                "Consider collaboration modification or termination"
            ])
        elif risk_assessment["risk_level"] == "medium":
            recommendations.extend([
                "Address identified risk factors",
                "Increase monitoring frequency",
                "Adjust collaboration strategy as needed"
            ])
        
        # Based on network effects
        if network_effect["cross_pollination_effect"] > 0.05:
            recommendations.append("Leverage successful collaboration model for future partnerships")
        
        if network_effect["reputation_spillover"] > 0.1:
            recommendations.append("Manage reputation spillover effects carefully")
        
        # Based on individual impacts
        negative_participants = [
            creator_id for creator_id, impact in individual_impacts.items()
            if impact["absolute_impact"] < -0.02
        ]
        
        if negative_participants:
            recommendations.append(f"Provide additional support to participants experiencing negative impact: {', '.join(negative_participants)}")
        
        return recommendations
    
    async def get_reputation_analytics(
        self,
        creator_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive reputation analytics.
        
        Args:
            creator_id: Optional creator filter
            period_days: Analysis period in days
            
        Returns:
            Reputation analytics data
        """
        try:
            period_start = datetime.utcnow() - timedelta(days=period_days)
            
            if creator_id:
                # Single creator analysis
                if creator_id not in self.reputation_scores:
                    return {"error": "Creator not found"}
                
                return await self._generate_creator_analytics(creator_id, period_days)
            else:
                # Platform-wide analysis
                return await self._generate_platform_analytics(period_days)
                
        except Exception as e:
            logger.error(f"❌ Error generating reputation analytics: {e}")
            return {"error": str(e)}
    
    async def _generate_creator_analytics(self, creator_id: str, period_days: int) -> Dict[str, Any]:
        """Generate analytics for a specific creator."""
        reputation = self.reputation_scores[creator_id]
        period_start = datetime.utcnow() - timedelta(days=period_days)
        
        # Get period events
        period_events = [
            event for event in self.reputation_events
            if event.creator_id == creator_id and event.timestamp >= period_start
        ]
        
        # Get period alerts
        period_alerts = [
            alert for alert in self.active_alerts
            if alert.creator_id == creator_id and alert.triggered_at >= period_start
        ]
        
        # Calculate trend metrics
        period_scores = [
            entry for entry in reputation.historical_data
            if datetime.fromisoformat(entry["timestamp"]) >= period_start
        ]
        
        trend_analysis = {}
        if len(period_scores) >= 2:
            start_score = period_scores[0]["overall_score"]
            end_score = period_scores[-1]["overall_score"]
            trend_analysis = {
                "score_change": end_score - start_score,
                "percentage_change": (end_score - start_score) / start_score * 100 if start_score > 0 else 0,
                "trend_direction": reputation.trend_direction
            }
        
        return {
            "creator_id": creator_id,
            "period_days": period_days,
            "current_reputation": {
                "overall_score": reputation.overall_score,
                "risk_level": reputation.risk_level.value,
                "trend_direction": reputation.trend_direction,
                "confidence_level": reputation.confidence_level
            },
            "metric_breakdown": {metric.value: score for metric, score in reputation.metric_scores.items()},
            "trend_analysis": trend_analysis,
            "period_events": {
                "total_events": len(period_events),
                "positive_events": len([e for e in period_events if e.impact_level in [ImpactLevel.POSITIVE, ImpactLevel.VERY_POSITIVE]]),
                "negative_events": len([e for e in period_events if e.impact_level in [ImpactLevel.NEGATIVE, ImpactLevel.VERY_NEGATIVE]]),
                "event_breakdown": self._analyze_event_breakdown(period_events)
            },
            "alerts": {
                "total_alerts": len(period_alerts),
                "active_alerts": len([a for a in period_alerts if not a.resolved]),
                "alert_breakdown": self._analyze_alert_breakdown(period_alerts)
            },
            "recommendations": self._generate_creator_recommendations(reputation, period_events, period_alerts)
        }
    
    async def _generate_platform_analytics(self, period_days: int) -> Dict[str, Any]:
        """Generate platform-wide reputation analytics."""
        period_start = datetime.utcnow() - timedelta(days=period_days)
        
        # Overall platform metrics
        total_creators = len(self.reputation_scores)
        if total_creators == 0:
            return {"message": "No creators tracked"}
        
        overall_scores = [rep.overall_score for rep in self.reputation_scores.values()]
        average_score = statistics.mean(overall_scores)
        
        # Risk distribution
        risk_distribution = defaultdict(int)
        for reputation in self.reputation_scores.values():
            risk_distribution[reputation.risk_level.value] += 1
        
        # Platform events
        platform_events = [
            event for event in self.reputation_events
            if event.timestamp >= period_start
        ]
        
        # Platform alerts
        platform_alerts = [
            alert for alert in self.active_alerts
            if alert.triggered_at >= period_start
        ]
        
        return {
            "period_days": period_days,
            "platform_overview": {
                "total_creators": total_creators,
                "average_reputation_score": average_score,
                "score_distribution": {
                    "excellent": len([s for s in overall_scores if s >= 0.9]),
                    "good": len([s for s in overall_scores if 0.8 <= s < 0.9]),
                    "average": len([s for s in overall_scores if 0.6 <= s < 0.8]),
                    "poor": len([s for s in overall_scores if s < 0.6])
                },
                "risk_distribution": dict(risk_distribution)
            },
            "platform_events": {
                "total_events": len(platform_events),
                "event_breakdown": self._analyze_event_breakdown(platform_events)
            },
            "platform_alerts": {
                "total_alerts": len(platform_alerts),
                "alert_breakdown": self._analyze_alert_breakdown(platform_alerts)
            },
            "collaboration_insights": await self._analyze_platform_collaboration_trends(),
            "recommendations": self._generate_platform_recommendations(overall_scores, platform_events, platform_alerts)
        }
    
    def _analyze_event_breakdown(self, events: List[ReputationEvent]) -> Dict[str, Any]:
        """Analyze breakdown of reputation events."""
        if not events:
            return {}
        
        breakdown = {
            "by_impact_level": defaultdict(int),
            "by_source": defaultdict(int),
            "by_event_type": defaultdict(int)
        }
        
        for event in events:
            breakdown["by_impact_level"][event.impact_level.value] += 1
            breakdown["by_source"][event.source.value] += 1
            breakdown["by_event_type"][event.event_type] += 1
        
        return {k: dict(v) for k, v in breakdown.items()}
    
    def _analyze_alert_breakdown(self, alerts: List[ReputationAlert]) -> Dict[str, Any]:
        """Analyze breakdown of reputation alerts."""
        if not alerts:
            return {}
        
        breakdown = {
            "by_severity": defaultdict(int),
            "by_type": defaultdict(int),
            "resolution_status": {"resolved": 0, "active": 0}
        }
        
        for alert in alerts:
            breakdown["by_severity"][alert.severity.value] += 1
            breakdown["by_type"][alert.alert_type] += 1
            if alert.resolved:
                breakdown["resolution_status"]["resolved"] += 1
            else:
                breakdown["resolution_status"]["active"] += 1
        
        return {k: dict(v) if isinstance(v, defaultdict) else v for k, v in breakdown.items()}
    
    async def _analyze_platform_collaboration_trends(self) -> Dict[str, Any]:
        """Analyze collaboration trends across the platform."""
        if not self.collaboration_impacts:
            return {"message": "No collaboration data available"}
        
        impacts = list(self.collaboration_impacts.values())
        
        # Success rate
        successful_collaborations = len([
            impact for impact in impacts
            if impact.mutual_benefit_score >= 0.7
        ])
        
        success_rate = successful_collaborations / len(impacts) if impacts else 0
        
        # Average impact metrics
        avg_mutual_benefit = statistics.mean([
            impact.mutual_benefit_score for impact in impacts
        ]) if impacts else 0
        
        return {
            "total_collaborations_analyzed": len(impacts),
            "collaboration_success_rate": success_rate,
            "average_mutual_benefit_score": avg_mutual_benefit,
            "trending_collaboration_types": self._identify_trending_collaboration_types()
        }
    
    def _identify_trending_collaboration_types(self) -> List[str]:
        """Identify trending collaboration types based on success."""
        # This would analyze collaboration metadata to identify trends
        # For now, return placeholder data
        return ["music_collaboration", "brand_partnership", "cross_promotion"]
    
    def _generate_creator_recommendations(
        self,
        reputation: ReputationScore,
        events: List[ReputationEvent],
        alerts: List[ReputationAlert]
    ) -> List[str]:
        """Generate personalized recommendations for a creator."""
        recommendations = []
        
        # Based on reputation score
        if reputation.overall_score < 0.6:
            recommendations.extend([
                "Focus on improving core reputation metrics",
                "Engage with community to rebuild trust",
                "Consider reputation recovery strategy"
            ])
        elif reputation.overall_score < 0.8:
            recommendations.extend([
                "Continue building positive reputation",
                "Seek quality collaboration opportunities",
                "Monitor feedback and sentiment closely"
            ])
        
        # Based on trend
        if reputation.trend_direction == "declining":
            recommendations.append("Address factors causing reputation decline")
        elif reputation.trend_direction == "improving":
            recommendations.append("Maintain positive momentum with consistent quality")
        
        # Based on recent events
        negative_events = [e for e in events if e.impact_level in [ImpactLevel.NEGATIVE, ImpactLevel.VERY_NEGATIVE]]
        if negative_events:
            recommendations.append("Address recent negative feedback and concerns")
        
        # Based on active alerts
        active_alerts = [a for a in alerts if not a.resolved]
        if active_alerts:
            recommendations.append("Resolve active reputation alerts")
        
        return recommendations
    
    def _generate_platform_recommendations(
        self,
        scores: List[float],
        events: List[ReputationEvent],
        alerts: List[ReputationAlert]
    ) -> List[str]:
        """Generate platform-wide recommendations."""
        recommendations = []
        
        avg_score = statistics.mean(scores) if scores else 0
        
        if avg_score < 0.7:
            recommendations.extend([
                "Implement platform-wide reputation improvement initiatives",
                "Provide creator education and support resources",
                "Review platform policies and guidelines"
            ])
        
        # Based on alert frequency
        critical_alerts = len([a for a in alerts if a.severity == ReputationRisk.CRITICAL])
        if critical_alerts > len(scores) * 0.1:  # More than 10% of creators have critical alerts
            recommendations.append("Investigate widespread reputation issues")
        
        return recommendations

# Global instance for enterprise reputation monitoring
reputation_impact_analyzer = ReputationImpactAnalyzer()

__all__ = [
    'ReputationImpactAnalyzer',
    'ReputationScore',
    'ReputationEvent',
    'CollaborationImpact',
    'ReputationAlert',
    'ReputationMetric',
    'ImpactLevel',
    'ReputationRisk',
    'SentimentSource',
    'reputation_impact_analyzer'
]