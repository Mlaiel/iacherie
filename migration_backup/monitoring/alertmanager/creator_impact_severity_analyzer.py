#!/usr/bin/env python3
"""
Creator Impact Severity Analyzer - Creator Economy Impact Assessment
===================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - All Rights Reserved

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries - AI-Powered Creator Economy Platform
Module: Creator Impact Severity Analyzer
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import math

logger = logging.getLogger(__name__)


class CreatorSpecialization(Enum):
    """Creator content specializations"""
    MUSICIANS = "musicians"
    BLOGGERS = "bloggers"
    PHOTOGRAPHERS = "photographers"
    INFLUENCERS = "influencers"
    COMEDIANS = "comedians"
    PODCASTERS = "podcasters"
    STREAMERS = "streamers"
    EDUCATORS = "educators"
    ARTISTS = "artists"
    GAMERS = "gamers"


class ImpactDimension(Enum):
    """Different dimensions of Creator impact"""
    CONTENT_CREATION = "content_creation"        # Ability to create content
    CONTENT_DELIVERY = "content_delivery"        # Content distribution
    MONETIZATION = "monetization"                # Revenue generation
    AUDIENCE_ENGAGEMENT = "audience_engagement"   # Fan interaction
    BRAND_REPUTATION = "brand_reputation"        # Creator brand image
    COLLABORATION = "collaboration"              # Creator-to-creator interaction
    ANALYTICS_INSIGHTS = "analytics_insights"    # Performance metrics access


@dataclass
class CreatorProfile:
    """Enhanced Creator profile for impact analysis"""
    creator_id: str
    tier: str  # premium, professional, emerging, starter
    specialization: CreatorSpecialization
    follower_count: int
    engagement_rate: float  # 0-1 scale
    monthly_revenue: float  # USD
    content_frequency: int  # Posts per month
    geographic_reach: List[str]
    peak_activity_hours: List[int]  # Hours in UTC
    collaboration_count: int
    brand_partnerships: int
    audience_demographics: Dict[str, float] = field(default_factory=dict)
    content_categories: List[str] = field(default_factory=list)
    platform_distribution: Dict[str, float] = field(default_factory=dict)


@dataclass
class ImpactScore:
    """Detailed impact scoring for different dimensions"""
    overall_score: float  # 0-1 scale
    dimension_scores: Dict[ImpactDimension, float]
    affected_creators: List[str]
    estimated_revenue_loss: float
    estimated_audience_reach_loss: int
    reputation_risk_score: float
    recovery_time_estimate: int  # Minutes
    business_continuity_risk: float
    rationale: str
    confidence_level: float


@dataclass
class ServiceImpactMatrix:
    """Matrix defining how services impact Creator activities"""
    service_name: str
    impact_weights: Dict[ImpactDimension, float]
    creator_specialization_multipliers: Dict[CreatorSpecialization, float]
    tier_sensitivity: Dict[str, float]  # How sensitive each tier is to this service


class CreatorImpactSeverityAnalyzer:
    """
    Advanced Creator Impact Analysis Engine
    
    Analyzes how system issues affect the Creator Economy with:
    - Creator tier impact calculation
    - Revenue impact severity scoring
    - User experience degradation assessment
    - Creator satisfaction impact prediction
    - Business continuity risk evaluation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Creator Impact Analyzer"""
        self.config = config
        self.service_impact_matrix = self._build_service_impact_matrix()
        self.creator_profiles_cache = {}  # Would be loaded from database
        self.impact_history = {}  # Historical impact data
        self.business_metrics = self._initialize_business_metrics()
        
        logger.info("Creator Impact Severity Analyzer initialized")
    
    def _build_service_impact_matrix(self) -> Dict[str, ServiceImpactMatrix]:
        """Build impact matrix for different services"""
        return {
            "api": ServiceImpactMatrix(
                service_name="api",
                impact_weights={
                    ImpactDimension.CONTENT_CREATION: 0.9,
                    ImpactDimension.CONTENT_DELIVERY: 0.95,
                    ImpactDimension.MONETIZATION: 0.8,
                    ImpactDimension.AUDIENCE_ENGAGEMENT: 0.85,
                    ImpactDimension.BRAND_REPUTATION: 0.6,
                    ImpactDimension.COLLABORATION: 0.7,
                    ImpactDimension.ANALYTICS_INSIGHTS: 0.9
                },
                creator_specialization_multipliers={
                    CreatorSpecialization.STREAMERS: 1.5,    # Highly dependent on API
                    CreatorSpecialization.PODCASTERS: 1.3,
                    CreatorSpecialization.BLOGGERS: 1.2,
                    CreatorSpecialization.MUSICIANS: 1.1,
                    CreatorSpecialization.PHOTOGRAPHERS: 1.0,
                    CreatorSpecialization.INFLUENCERS: 1.4,
                    CreatorSpecialization.COMEDIANS: 1.2,
                    CreatorSpecialization.EDUCATORS: 1.3,
                    CreatorSpecialization.ARTISTS: 1.0,
                    CreatorSpecialization.GAMERS: 1.5
                },
                tier_sensitivity={
                    "premium": 2.0,      # Premium creators heavily impacted
                    "professional": 1.5,
                    "emerging": 1.2,
                    "starter": 1.0
                }
            ),
            
            "database": ServiceImpactMatrix(
                service_name="database",
                impact_weights={
                    ImpactDimension.CONTENT_CREATION: 0.7,
                    ImpactDimension.CONTENT_DELIVERY: 0.9,
                    ImpactDimension.MONETIZATION: 0.95,  # Payment data critical
                    ImpactDimension.AUDIENCE_ENGAGEMENT: 0.8,
                    ImpactDimension.BRAND_REPUTATION: 0.5,
                    ImpactDimension.COLLABORATION: 0.6,
                    ImpactDimension.ANALYTICS_INSIGHTS: 0.95
                },
                creator_specialization_multipliers={
                    CreatorSpecialization.STREAMERS: 1.4,
                    CreatorSpecialization.PODCASTERS: 1.2,
                    CreatorSpecialization.BLOGGERS: 1.3,
                    CreatorSpecialization.MUSICIANS: 1.2,
                    CreatorSpecialization.PHOTOGRAPHERS: 1.1,
                    CreatorSpecialization.INFLUENCERS: 1.3,
                    CreatorSpecialization.COMEDIANS: 1.1,
                    CreatorSpecialization.EDUCATORS: 1.2,
                    CreatorSpecialization.ARTISTS: 1.1,
                    CreatorSpecialization.GAMERS: 1.4
                },
                tier_sensitivity={
                    "premium": 2.5,      # Premium creators most affected by data issues
                    "professional": 2.0,
                    "emerging": 1.5,
                    "starter": 1.0
                }
            ),
            
            "ai-engine": ServiceImpactMatrix(
                service_name="ai-engine",
                impact_weights={
                    ImpactDimension.CONTENT_CREATION: 0.95,  # AI heavily used in content creation
                    ImpactDimension.CONTENT_DELIVERY: 0.7,
                    ImpactDimension.MONETIZATION: 0.6,
                    ImpactDimension.AUDIENCE_ENGAGEMENT: 0.8,
                    ImpactDimension.BRAND_REPUTATION: 0.7,
                    ImpactDimension.COLLABORATION: 0.5,
                    ImpactDimension.ANALYTICS_INSIGHTS: 0.8
                },
                creator_specialization_multipliers={
                    CreatorSpecialization.MUSICIANS: 1.8,    # AI heavily used for music
                    CreatorSpecialization.ARTISTS: 1.7,
                    CreatorSpecialization.PHOTOGRAPHERS: 1.6,
                    CreatorSpecialization.BLOGGERS: 1.5,
                    CreatorSpecialization.COMEDIANS: 1.4,
                    CreatorSpecialization.PODCASTERS: 1.3,
                    CreatorSpecialization.STREAMERS: 1.2,
                    CreatorSpecialization.INFLUENCERS: 1.1,
                    CreatorSpecialization.EDUCATORS: 1.3,
                    CreatorSpecialization.GAMERS: 1.1
                },
                tier_sensitivity={
                    "premium": 1.8,
                    "professional": 1.6,
                    "emerging": 1.3,
                    "starter": 1.0
                }
            ),
            
            "payment": ServiceImpactMatrix(
                service_name="payment",
                impact_weights={
                    ImpactDimension.CONTENT_CREATION: 0.3,
                    ImpactDimension.CONTENT_DELIVERY: 0.2,
                    ImpactDimension.MONETIZATION: 1.0,      # Direct monetization impact
                    ImpactDimension.AUDIENCE_ENGAGEMENT: 0.4,
                    ImpactDimension.BRAND_REPUTATION: 0.8,   # Payment issues hurt reputation
                    ImpactDimension.COLLABORATION: 0.3,
                    ImpactDimension.ANALYTICS_INSIGHTS: 0.5
                },
                creator_specialization_multipliers={
                    # All creators equally affected by payment issues
                    spec: 1.0 for spec in CreatorSpecialization
                },
                tier_sensitivity={
                    "premium": 3.0,      # Premium creators lose most revenue
                    "professional": 2.5,
                    "emerging": 2.0,
                    "starter": 1.0
                }
            ),
            
            "security": ServiceImpactMatrix(
                service_name="security",
                impact_weights={
                    ImpactDimension.CONTENT_CREATION: 0.6,
                    ImpactDimension.CONTENT_DELIVERY: 0.7,
                    ImpactDimension.MONETIZATION: 0.8,
                    ImpactDimension.AUDIENCE_ENGAGEMENT: 0.5,
                    ImpactDimension.BRAND_REPUTATION: 1.0,   # Security issues heavily impact reputation
                    ImpactDimension.COLLABORATION: 0.6,
                    ImpactDimension.ANALYTICS_INSIGHTS: 0.7
                },
                creator_specialization_multipliers={
                    **{CreatorSpecialization.INFLUENCERS: 1.5,  # Brand reputation critical
                       CreatorSpecialization.EDUCATORS: 1.4},
                    **{spec: 1.2 for spec in CreatorSpecialization 
                       if spec not in [CreatorSpecialization.INFLUENCERS, CreatorSpecialization.EDUCATORS]}
                },
                tier_sensitivity={
                    "premium": 2.5,
                    "professional": 2.0,
                    "emerging": 1.5,
                    "starter": 1.0
                }
            ),
            
            "storage": ServiceImpactMatrix(
                service_name="storage",
                impact_weights={
                    ImpactDimension.CONTENT_CREATION: 0.8,
                    ImpactDimension.CONTENT_DELIVERY: 0.95,  # Storage critical for delivery
                    ImpactDimension.MONETIZATION: 0.7,
                    ImpactDimension.AUDIENCE_ENGAGEMENT: 0.6,
                    ImpactDimension.BRAND_REPUTATION: 0.5,
                    ImpactDimension.COLLABORATION: 0.7,
                    ImpactDimension.ANALYTICS_INSIGHTS: 0.6
                },
                creator_specialization_multipliers={
                    CreatorSpecialization.PHOTOGRAPHERS: 2.0,  # High storage needs
                    CreatorSpecialization.STREAMERS: 1.8,
                    CreatorSpecialization.MUSICIANS: 1.6,
                    CreatorSpecialization.PODCASTERS: 1.5,
                    CreatorSpecialization.COMEDIANS: 1.4,
                    CreatorSpecialization.ARTISTS: 1.7,
                    CreatorSpecialization.GAMERS: 1.5,
                    CreatorSpecialization.BLOGGERS: 1.2,
                    CreatorSpecialization.INFLUENCERS: 1.3,
                    CreatorSpecialization.EDUCATORS: 1.4
                },
                tier_sensitivity={
                    "premium": 2.0,
                    "professional": 1.8,
                    "emerging": 1.4,
                    "starter": 1.0
                }
            )
        }
    
    def _initialize_business_metrics(self) -> Dict[str, Any]:
        """Initialize business metrics for impact calculation"""
        return {
            "average_revenue_per_creator": {
                "premium": 10000.0,      # Monthly USD
                "professional": 2500.0,
                "emerging": 500.0,
                "starter": 50.0
            },
            "average_audience_size": {
                "premium": 500000,
                "professional": 50000,
                "emerging": 5000,
                "starter": 500
            },
            "engagement_multipliers": {
                "high": 1.5,    # High engagement creators
                "medium": 1.0,
                "low": 0.7
            },
            "geographic_impact_multipliers": {
                "US": 1.5,
                "EU": 1.3,
                "ASIA": 1.2,
                "OTHER": 1.0
            },
            "downtime_cost_per_minute": {
                "premium": 50.0,     # USD per minute of downtime
                "professional": 12.0,
                "emerging": 2.0,
                "starter": 0.5
            }
        }
    
    async def analyze_creator_impact(self, alert_context: Any) -> Any:
        """
        Main analysis function - enhances alert context with Creator impact
        
        Args:
            alert_context: Alert context from orchestrator
            
        Returns:
            Enhanced alert context with Creator impact analysis
        """
        try:
            # Get affected creators
            affected_creators = await self._identify_affected_creators(alert_context)
            
            # Calculate impact scores
            impact_score = await self._calculate_impact_score(
                alert_context, affected_creators
            )
            
            # Enhance alert context
            enhanced_context = await self._enhance_alert_context(
                alert_context, impact_score, affected_creators
            )
            
            # Store impact analysis for historical data
            await self._store_impact_analysis(enhanced_context, impact_score)
            
            logger.info(
                f"Creator impact analyzed: {alert_context.alert_id} -> "
                f"Overall Score: {impact_score.overall_score:.2f}, "
                f"Affected Creators: {len(affected_creators)}"
            )
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Failed to analyze Creator impact: {e}")
            # Return original context if analysis fails
            return alert_context
    
    async def _identify_affected_creators(self, alert_context: Any) -> List[CreatorProfile]:
        """Identify which creators are affected by the alert"""
        try:
            affected_creators = []
            
            # If specific creator_id is provided
            if alert_context.creator_id:
                creator_profile = await self._get_creator_profile(alert_context.creator_id)
                if creator_profile:
                    affected_creators.append(creator_profile)
                return affected_creators
            
            # For system-wide issues, identify affected creators based on:
            # 1. Service impact matrix
            # 2. Geographic scope
            # 3. Time-based activity patterns
            # 4. Creator specialization
            
            service_impact = self.service_impact_matrix.get(alert_context.source_service)
            if not service_impact:
                return affected_creators
            
            # Mock creator identification (would query real database)
            mock_creators = await self._get_active_creators(alert_context)
            
            for creator in mock_creators:
                # Check if creator is affected based on various factors
                if self._is_creator_affected(creator, alert_context, service_impact):
                    affected_creators.append(creator)
            
            # Sort by impact priority (tier, revenue, engagement)
            affected_creators.sort(
                key=lambda c: (
                    {"premium": 4, "professional": 3, "emerging": 2, "starter": 1}[c.tier],
                    c.monthly_revenue,
                    c.engagement_rate
                ),
                reverse=True
            )
            
            return affected_creators
            
        except Exception as e:
            logger.error(f"Failed to identify affected creators: {e}")
            return []
    
    async def _get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Get Creator profile by ID (would query database)"""
        # Mock implementation - would query real database
        if creator_id in self.creator_profiles_cache:
            return self.creator_profiles_cache[creator_id]
        
        # Mock profile for testing
        mock_profile = CreatorProfile(
            creator_id=creator_id,
            tier="professional",
            specialization=CreatorSpecialization.MUSICIANS,
            follower_count=25000,
            engagement_rate=0.07,
            monthly_revenue=2500.0,
            content_frequency=15,
            geographic_reach=["US", "EU"],
            peak_activity_hours=[14, 15, 16, 20, 21],
            collaboration_count=5,
            brand_partnerships=3,
            audience_demographics={"18-24": 0.3, "25-34": 0.4, "35-44": 0.2, "45+": 0.1},
            content_categories=["music", "tutorials", "live_streams"],
            platform_distribution={"instagram": 0.4, "youtube": 0.3, "tiktok": 0.3}
        )
        
        self.creator_profiles_cache[creator_id] = mock_profile
        return mock_profile
    
    async def _get_active_creators(self, alert_context: Any) -> List[CreatorProfile]:
        """Get currently active creators (would query database)"""
        # Mock implementation - would query real database for active creators
        current_hour = datetime.now().hour
        
        # Mock active creators based on time and geography
        mock_creators = []
        
        # Generate mock creator profiles for different tiers and specializations
        creator_templates = [
            ("premium", CreatorSpecialization.INFLUENCERS, 750000, 0.12, 12000.0),
            ("premium", CreatorSpecialization.MUSICIANS, 500000, 0.08, 8000.0),
            ("professional", CreatorSpecialization.BLOGGERS, 75000, 0.06, 3000.0),
            ("professional", CreatorSpecialization.PHOTOGRAPHERS, 45000, 0.09, 2200.0),
            ("emerging", CreatorSpecialization.COMEDIANS, 8000, 0.11, 600.0),
            ("emerging", CreatorSpecialization.PODCASTERS, 12000, 0.05, 800.0),
            ("starter", CreatorSpecialization.ARTISTS, 800, 0.15, 80.0),
            ("starter", CreatorSpecialization.STREAMERS, 1200, 0.08, 120.0)
        ]
        
        for i, (tier, spec, followers, engagement, revenue) in enumerate(creator_templates):
            # Only include creators who would be active at this time
            if current_hour in [14, 15, 16, 20, 21, 22]:  # Peak hours
                creator = CreatorProfile(
                    creator_id=f"creator_{i+1:03d}",
                    tier=tier,
                    specialization=spec,
                    follower_count=followers,
                    engagement_rate=engagement,
                    monthly_revenue=revenue,
                    content_frequency=20 if tier == "premium" else 15 if tier == "professional" else 10,
                    geographic_reach=alert_context.geographic_scope if alert_context.geographic_scope else ["US"],
                    peak_activity_hours=[14, 15, 16, 20, 21, 22],
                    collaboration_count=8 if tier == "premium" else 5 if tier == "professional" else 2,
                    brand_partnerships=5 if tier == "premium" else 2 if tier == "professional" else 0
                )
                mock_creators.append(creator)
        
        return mock_creators
    
    def _is_creator_affected(
        self,
        creator: CreatorProfile,
        alert_context: Any,
        service_impact: ServiceImpactMatrix
    ) -> bool:
        """Determine if a specific creator is affected by the alert"""
        try:
            # Geographic check
            if alert_context.geographic_scope:
                if not any(geo in creator.geographic_reach for geo in alert_context.geographic_scope):
                    return False
            
            # Time-based activity check
            current_hour = datetime.now().hour
            if current_hour not in creator.peak_activity_hours:
                # Lower probability of being affected if not active
                if creator.tier not in ["premium", "professional"]:
                    return False
            
            # Service specialization check
            specialization_multiplier = service_impact.creator_specialization_multipliers.get(
                creator.specialization, 1.0
            )
            
            # If multiplier is low, creator is less likely to be affected
            if specialization_multiplier < 1.0:
                return np.random.random() < 0.5  # 50% chance
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check creator impact: {e}")
            return False
    
    async def _calculate_impact_score(
        self,
        alert_context: Any,
        affected_creators: List[CreatorProfile]
    ) -> ImpactScore:
        """Calculate comprehensive impact score"""
        try:
            if not affected_creators:
                return ImpactScore(
                    overall_score=0.0,
                    dimension_scores={dim: 0.0 for dim in ImpactDimension},
                    affected_creators=[],
                    estimated_revenue_loss=0.0,
                    estimated_audience_reach_loss=0,
                    reputation_risk_score=0.0,
                    recovery_time_estimate=0,
                    business_continuity_risk=0.0,
                    rationale="No creators affected",
                    confidence_level=1.0
                )
            
            service_impact = self.service_impact_matrix.get(
                alert_context.source_service,
                self.service_impact_matrix["api"]  # Default fallback
            )
            
            # Calculate dimension scores
            dimension_scores = {}
            total_weighted_impact = 0.0
            total_weight = 0.0
            
            for dimension, base_weight in service_impact.impact_weights.items():
                dimension_impact = 0.0
                
                for creator in affected_creators:
                    # Base impact from service
                    creator_impact = base_weight
                    
                    # Apply creator specialization multiplier
                    spec_multiplier = service_impact.creator_specialization_multipliers.get(
                        creator.specialization, 1.0
                    )
                    creator_impact *= spec_multiplier
                    
                    # Apply tier sensitivity
                    tier_multiplier = service_impact.tier_sensitivity.get(creator.tier, 1.0)
                    creator_impact *= tier_multiplier
                    
                    # Apply engagement multiplier
                    if creator.engagement_rate > 0.10:
                        engagement_mult = self.business_metrics["engagement_multipliers"]["high"]
                    elif creator.engagement_rate > 0.05:
                        engagement_mult = self.business_metrics["engagement_multipliers"]["medium"]
                    else:
                        engagement_mult = self.business_metrics["engagement_multipliers"]["low"]
                    
                    creator_impact *= engagement_mult
                    
                    # Apply severity multiplier
                    severity_multipliers = {
                        "emergency": 1.0, "critical": 0.9, "high": 0.7,
                        "warning": 0.5, "info": 0.3, "debug": 0.1
                    }
                    severity_mult = severity_multipliers.get(alert_context.severity.value, 0.5)
                    creator_impact *= severity_mult
                    
                    dimension_impact += creator_impact
                
                # Normalize by number of creators
                if affected_creators:
                    dimension_impact /= len(affected_creators)
                
                dimension_scores[dimension] = min(1.0, dimension_impact)
                total_weighted_impact += dimension_impact * base_weight
                total_weight += base_weight
            
            # Calculate overall score
            overall_score = min(1.0, total_weighted_impact / total_weight if total_weight > 0 else 0.0)
            
            # Calculate revenue impact
            estimated_revenue_loss = self._calculate_revenue_impact(
                affected_creators, alert_context, service_impact
            )
            
            # Calculate audience reach impact
            estimated_audience_reach_loss = sum(creator.follower_count for creator in affected_creators)
            
            # Calculate reputation risk
            reputation_risk_score = self._calculate_reputation_risk(
                affected_creators, alert_context, dimension_scores
            )
            
            # Estimate recovery time
            recovery_time_estimate = self._estimate_recovery_time(
                alert_context, overall_score, len(affected_creators)
            )
            
            # Calculate business continuity risk
            business_continuity_risk = self._calculate_business_continuity_risk(
                overall_score, len(affected_creators), estimated_revenue_loss
            )
            
            # Generate rationale
            rationale = self._generate_impact_rationale(
                alert_context, affected_creators, dimension_scores, overall_score
            )
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(
                affected_creators, service_impact, alert_context
            )
            
            return ImpactScore(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                affected_creators=[c.creator_id for c in affected_creators],
                estimated_revenue_loss=estimated_revenue_loss,
                estimated_audience_reach_loss=estimated_audience_reach_loss,
                reputation_risk_score=reputation_risk_score,
                recovery_time_estimate=recovery_time_estimate,
                business_continuity_risk=business_continuity_risk,
                rationale=rationale,
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate impact score: {e}")
            return ImpactScore(
                overall_score=0.5,  # Default medium impact
                dimension_scores={dim: 0.5 for dim in ImpactDimension},
                affected_creators=[c.creator_id for c in affected_creators],
                estimated_revenue_loss=0.0,
                estimated_audience_reach_loss=0,
                reputation_risk_score=0.5,
                recovery_time_estimate=30,
                business_continuity_risk=0.5,
                rationale="Impact calculation failed, using default estimates",
                confidence_level=0.3
            )
    
    def _calculate_revenue_impact(
        self,
        affected_creators: List[CreatorProfile],
        alert_context: Any,
        service_impact: ServiceImpactMatrix
    ) -> float:
        """Calculate estimated revenue loss"""
        try:
            total_revenue_loss = 0.0
            
            # Base downtime duration estimate (minutes)
            estimated_downtime = {
                "emergency": 60,  # 1 hour
                "critical": 30,   # 30 minutes
                "high": 15,       # 15 minutes
                "warning": 5,     # 5 minutes
                "info": 2         # 2 minutes
            }.get(alert_context.severity.value, 15)
            
            for creator in affected_creators:
                # Base cost per minute for this creator tier
                cost_per_minute = self.business_metrics["downtime_cost_per_minute"][creator.tier]
                
                # Apply monetization impact weight
                monetization_impact = service_impact.impact_weights[ImpactDimension.MONETIZATION]
                
                # Calculate revenue loss for this creator
                creator_revenue_loss = cost_per_minute * estimated_downtime * monetization_impact
                
                # Apply specialization multiplier
                spec_multiplier = service_impact.creator_specialization_multipliers.get(
                    creator.specialization, 1.0
                )
                creator_revenue_loss *= spec_multiplier
                
                total_revenue_loss += creator_revenue_loss
            
            return total_revenue_loss
            
        except Exception as e:
            logger.error(f"Failed to calculate revenue impact: {e}")
            return 0.0
    
    def _calculate_reputation_risk(
        self,
        affected_creators: List[CreatorProfile],
        alert_context: Any,
        dimension_scores: Dict[ImpactDimension, float]
    ) -> float:
        """Calculate reputation risk score"""
        try:
            # Base reputation risk from brand reputation dimension
            base_risk = dimension_scores.get(ImpactDimension.BRAND_REPUTATION, 0.0)
            
            # Amplify risk for public-facing creators
            public_facing_specializations = [
                CreatorSpecialization.INFLUENCERS,
                CreatorSpecialization.STREAMERS,
                CreatorSpecialization.EDUCATORS
            ]
            
            amplification_factor = 1.0
            for creator in affected_creators:
                if creator.specialization in public_facing_specializations:
                    amplification_factor += 0.2
                if creator.tier in ["premium", "professional"]:
                    amplification_factor += 0.3
            
            reputation_risk = min(1.0, base_risk * amplification_factor)
            
            return reputation_risk
            
        except Exception as e:
            logger.error(f"Failed to calculate reputation risk: {e}")
            return 0.5
    
    def _estimate_recovery_time(
        self,
        alert_context: Any,
        overall_score: float,
        affected_creator_count: int
    ) -> int:
        """Estimate recovery time in minutes"""
        try:
            # Base recovery times by severity
            base_recovery_times = {
                "emergency": 120,  # 2 hours
                "critical": 60,    # 1 hour
                "high": 30,        # 30 minutes
                "warning": 15,     # 15 minutes
                "info": 5          # 5 minutes
            }
            
            base_time = base_recovery_times.get(alert_context.severity.value, 30)
            
            # Adjust based on impact score
            impact_multiplier = 1.0 + overall_score  # 1.0 to 2.0
            
            # Adjust based on number of affected creators
            scale_multiplier = 1.0 + math.log10(max(1, affected_creator_count)) * 0.2
            
            estimated_time = int(base_time * impact_multiplier * scale_multiplier)
            
            return max(5, min(480, estimated_time))  # 5 minutes to 8 hours max
            
        except Exception as e:
            logger.error(f"Failed to estimate recovery time: {e}")
            return 30  # Default 30 minutes
    
    def _calculate_business_continuity_risk(
        self,
        overall_score: float,
        affected_creator_count: int,
        estimated_revenue_loss: float
    ) -> float:
        """Calculate business continuity risk"""
        try:
            # Base risk from overall impact score
            base_risk = overall_score
            
            # Scale risk based on number of affected creators
            if affected_creator_count > 100:
                scale_factor = 1.5
            elif affected_creator_count > 50:
                scale_factor = 1.3
            elif affected_creator_count > 10:
                scale_factor = 1.1
            else:
                scale_factor = 1.0
            
            # Revenue loss impact
            revenue_factor = 1.0
            if estimated_revenue_loss > 10000:  # $10K+
                revenue_factor = 1.4
            elif estimated_revenue_loss > 5000:  # $5K+
                revenue_factor = 1.2
            elif estimated_revenue_loss > 1000:  # $1K+
                revenue_factor = 1.1
            
            continuity_risk = min(1.0, base_risk * scale_factor * revenue_factor)
            
            return continuity_risk
            
        except Exception as e:
            logger.error(f"Failed to calculate business continuity risk: {e}")
            return 0.5
    
    def _generate_impact_rationale(
        self,
        alert_context: Any,
        affected_creators: List[CreatorProfile],
        dimension_scores: Dict[ImpactDimension, float],
        overall_score: float
    ) -> str:
        """Generate human-readable impact rationale"""
        try:
            parts = []
            
            # Overall impact assessment
            if overall_score > 0.8:
                parts.append("SEVERE Creator impact detected")
            elif overall_score > 0.6:
                parts.append("HIGH Creator impact detected")
            elif overall_score > 0.4:
                parts.append("MODERATE Creator impact detected")
            else:
                parts.append("LOW Creator impact detected")
            
            # Affected creators summary
            creator_tiers = {}
            for creator in affected_creators:
                creator_tiers[creator.tier] = creator_tiers.get(creator.tier, 0) + 1
            
            if creator_tiers:
                tier_summary = ", ".join([f"{count} {tier}" for tier, count in creator_tiers.items()])
                parts.append(f"Affecting {len(affected_creators)} creators ({tier_summary})")
            
            # Most impacted dimensions
            sorted_dimensions = sorted(
                dimension_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            if sorted_dimensions:
                dimension_names = [dim.value.replace('_', ' ').title() for dim, _ in sorted_dimensions]
                parts.append(f"Primary impact areas: {', '.join(dimension_names)}")
            
            # Service-specific context
            service_context = {
                "api": "affecting core platform functionality",
                "database": "impacting data access and analytics",
                "ai-engine": "disrupting AI-powered content creation",
                "payment": "blocking monetization capabilities",
                "security": "compromising Creator data protection",
                "storage": "limiting content storage and delivery"
            }
            
            if alert_context.source_service in service_context:
                parts.append(service_context[alert_context.source_service])
            
            return ". ".join(parts) + "."
            
        except Exception as e:
            logger.error(f"Failed to generate rationale: {e}")
            return f"Creator impact analysis for {alert_context.source_service} service issue"
    
    def _calculate_confidence_level(
        self,
        affected_creators: List[CreatorProfile],
        service_impact: ServiceImpactMatrix,
        alert_context: Any
    ) -> float:
        """Calculate confidence level of the impact assessment"""
        try:
            confidence_factors = []
            
            # Data completeness factor
            if alert_context.creator_id:
                confidence_factors.append(0.9)  # High confidence for specific creator
            elif affected_creators:
                confidence_factors.append(0.7)  # Medium confidence for identified creators
            else:
                confidence_factors.append(0.4)  # Low confidence for general impact
            
            # Service mapping confidence
            if alert_context.source_service in self.service_impact_matrix:
                confidence_factors.append(0.8)  # High confidence for known service
            else:
                confidence_factors.append(0.5)  # Medium confidence for unknown service
            
            # Severity confidence
            severity_confidence = {
                "emergency": 0.9, "critical": 0.8, "high": 0.7,
                "warning": 0.6, "info": 0.5, "debug": 0.4
            }
            confidence_factors.append(severity_confidence.get(alert_context.severity.value, 0.5))
            
            # Calculate overall confidence
            overall_confidence = np.mean(confidence_factors)
            
            return overall_confidence
            
        except Exception as e:
            logger.error(f"Failed to calculate confidence level: {e}")
            return 0.5
    
    async def _enhance_alert_context(
        self,
        alert_context: Any,
        impact_score: ImpactScore,
        affected_creators: List[CreatorProfile]
    ) -> Any:
        """Enhance alert context with impact analysis results"""
        try:
            # Add impact scores to alert context
            alert_context.business_impact = max(
                alert_context.business_impact,
                impact_score.overall_score
            )
            
            alert_context.revenue_impact = max(
                alert_context.revenue_impact,
                min(1.0, impact_score.estimated_revenue_loss / 10000.0)  # Normalize to 0-1
            )
            
            # Update user count affected
            alert_context.user_count_affected = max(
                alert_context.user_count_affected,
                impact_score.estimated_audience_reach_loss
            )
            
            # Add Creator-specific metadata
            if not hasattr(alert_context, 'metadata'):
                alert_context.metadata = {}
            
            alert_context.metadata.update({
                "creator_impact_analysis": {
                    "overall_score": impact_score.overall_score,
                    "dimension_scores": {dim.value: score for dim, score in impact_score.dimension_scores.items()},
                    "affected_creators_count": len(affected_creators),
                    "affected_creator_ids": impact_score.affected_creators,
                    "estimated_revenue_loss": impact_score.estimated_revenue_loss,
                    "estimated_audience_reach_loss": impact_score.estimated_audience_reach_loss,
                    "reputation_risk_score": impact_score.reputation_risk_score,
                    "recovery_time_estimate": impact_score.recovery_time_estimate,
                    "business_continuity_risk": impact_score.business_continuity_risk,
                    "confidence_level": impact_score.confidence_level,
                    "rationale": impact_score.rationale
                }
            })
            
            # Enhance Creator tier if not set
            if not alert_context.creator_tier and affected_creators:
                # Use highest tier among affected creators
                tier_priority = {"premium": 4, "professional": 3, "emerging": 2, "starter": 1}
                highest_tier = max(affected_creators, key=lambda c: tier_priority[c.tier])
                alert_context.creator_tier = type('CreatorTier', (), {'value': highest_tier.tier})()
            
            return alert_context
            
        except Exception as e:
            logger.error(f"Failed to enhance alert context: {e}")
            return alert_context
    
    async def _store_impact_analysis(self, alert_context: Any, impact_score: ImpactScore) -> None:
        """Store impact analysis for historical tracking"""
        try:
            analysis_data = {
                "alert_id": alert_context.alert_id,
                "timestamp": datetime.now().isoformat(),
                "service": alert_context.source_service,
                "severity": alert_context.severity.value,
                "overall_impact_score": impact_score.overall_score,
                "affected_creators_count": len(impact_score.affected_creators),
                "estimated_revenue_loss": impact_score.estimated_revenue_loss,
                "recovery_time_estimate": impact_score.recovery_time_estimate,
                "confidence_level": impact_score.confidence_level
            }
            
            # Store in impact history (would be saved to database)
            self.impact_history[alert_context.alert_id] = analysis_data
            
            logger.debug(f"Stored impact analysis for alert: {alert_context.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to store impact analysis: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the impact analyzer"""
        return {
            "status": "healthy",
            "service_impact_matrix_loaded": len(self.service_impact_matrix),
            "creator_profiles_cached": len(self.creator_profiles_cache),
            "impact_analyses_stored": len(self.impact_history),
            "business_metrics_loaded": bool(self.business_metrics)
        }
    
    def get_impact_statistics(self) -> Dict[str, Any]:
        """Get impact analysis statistics"""
        if not self.impact_history:
            return {"message": "No impact analyses performed yet"}
        
        analyses = list(self.impact_history.values())
        
        return {
            "total_analyses": len(analyses),
            "average_impact_score": np.mean([a["overall_impact_score"] for a in analyses]),
            "total_estimated_revenue_loss": sum([a["estimated_revenue_loss"] for a in analyses]),
            "average_affected_creators": np.mean([a["affected_creators_count"] for a in analyses]),
            "average_confidence_level": np.mean([a["confidence_level"] for a in analyses])
        }


if __name__ == "__main__":
    # Testing/development code
    import asyncio
    
    async def test_impact_analyzer():
        config = {}
        analyzer = CreatorImpactSeverityAnalyzer(config)
        
        # Mock alert context
        class MockAlertContext:
            def __init__(self):
                self.alert_id = "test_impact_001"
                self.severity = type('Severity', (), {'value': 'critical'})()
                self.source_service = "ai-engine"
                self.creator_id = None
                self.creator_tier = None
                self.business_impact = 0.5
                self.revenue_impact = 0.3
                self.user_count_affected = 0
                self.geographic_scope = ["US", "EU"]
                self.metadata = {}
        
        mock_context = MockAlertContext()
        enhanced_context = await analyzer.analyze_creator_impact(mock_context)
        
        print("Enhanced Alert Context:")
        print(f"Business Impact: {enhanced_context.business_impact}")
        print(f"Revenue Impact: {enhanced_context.revenue_impact}")
        print(f"User Count Affected: {enhanced_context.user_count_affected}")
        if hasattr(enhanced_context, 'metadata') and 'creator_impact_analysis' in enhanced_context.metadata:
            impact_data = enhanced_context.metadata['creator_impact_analysis']
            print(f"Impact Analysis: {json.dumps(impact_data, indent=2)}")
    
    asyncio.run(test_impact_analyzer())